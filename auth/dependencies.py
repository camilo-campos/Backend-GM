from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from typing import Optional, Dict, Any
import logging

from .jwt_handler import verify_token

logger = logging.getLogger(__name__)

# Esquema de seguridad Bearer
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependencia que extrae y valida el token JWT del header Authorization.
    Requiere autenticación - falla si no hay token válido.

    Returns:
        Diccionario con la información del usuario extraída del token

    Raises:
        HTTPException 401: Si no hay token o es inválido
    """
    token = credentials.credentials

    try:
        payload = await verify_token(token)

        # Extraer información relevante del usuario
        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "given_name": payload.get("given_name"),
            "family_name": payload.get("family_name"),
            "roles": payload.get("roles", []),
            "groups": payload.get("groups", []),
            # Metadata adicional
            "iss": payload.get("iss"),
            "aud": payload.get("aud"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }

        return user_data

    except JWTError as e:
        logger.warning(f"Token JWT invalido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Error inesperado en autenticacion: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticacion",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)
) -> Optional[Dict[str, Any]]:
    """
    Dependencia opcional que extrae el token JWT si está presente.
    No falla si no hay token - útil para endpoints públicos que
    pueden tener comportamiento diferente si el usuario está autenticado.

    Returns:
        Diccionario con info del usuario si hay token válido, None si no hay token
    """
    if credentials is None:
        return None

    try:
        payload = await verify_token(credentials.credentials)

        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "given_name": payload.get("given_name"),
            "family_name": payload.get("family_name"),
            "roles": payload.get("roles", []),
            "groups": payload.get("groups", [])
        }

        return user_data

    except (JWTError, Exception) as e:
        logger.debug(f"Token opcional invalido: {e}")
        return None


async def get_user_from_docs_auth(
    request: Request,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dependencia para autenticacion de documentacion.
    Busca el token JWT en: query parameter, cookie o header Authorization.

    Returns:
        Diccionario con el payload del token y el token mismo

    Raises:
        HTTPException 401: Si no hay token valido
    """
    jwt_token = token

    if not jwt_token:
        jwt_token = request.cookies.get("docs_token")

    if not jwt_token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header[7:]

    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido para acceder a la documentacion"
        )

    try:
        payload = await verify_token(jwt_token)
        return {"payload": payload, "token": jwt_token}
    except JWTError as e:
        logger.warning(f"Token JWT invalido en docs: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado"
        )
    except Exception as e:
        logger.error(f"Error en autenticacion de docs: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticacion"
        )

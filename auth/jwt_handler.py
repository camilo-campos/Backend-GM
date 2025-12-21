import httpx
from jose import jwt, JWTError, jwk
from jose.utils import base64url_decode
from cachetools import TTLCache
from typing import Optional, Dict, Any
import logging

from .config import (
    IBM_APPID_JWKS_URL,
    IBM_APPID_ISSUER,
    IBM_APPID_CLIENT_ID,
    JWT_ALGORITHM,
    JWKS_CACHE_TTL
)

logger = logging.getLogger(__name__)

# Caché para las claves públicas JWKS
_jwks_cache: TTLCache = TTLCache(maxsize=10, ttl=JWKS_CACHE_TTL)


async def get_jwks() -> Dict[str, Any]:
    """
    Obtiene las claves públicas JWKS de IBM App ID.
    Las claves se cachean para evitar peticiones repetidas.
    """
    cache_key = "jwks"

    if cache_key in _jwks_cache:
        return _jwks_cache[cache_key]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(IBM_APPID_JWKS_URL, timeout=10.0)
            response.raise_for_status()
            jwks_data = response.json()
            _jwks_cache[cache_key] = jwks_data
            logger.info("JWKS obtenido exitosamente de IBM App ID")
            return jwks_data
    except httpx.HTTPError as e:
        logger.error(f"Error al obtener JWKS: {e}")
        raise Exception(f"No se pudo obtener las claves públicas de IBM App ID: {e}")


def get_public_key_from_jwks(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la clave pública correspondiente al kid del token.
    Agrega el campo 'alg' si no está presente (requerido por python-jose).
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            # Agregar algoritmo si no está presente (IBM App ID no lo incluye)
            if "alg" not in key:
                key = {**key, "alg": JWT_ALGORITHM}
            return key
    return None


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT de IBM App ID.

    Args:
        token: El token JWT a verificar

    Returns:
        El payload decodificado del token

    Raises:
        JWTError: Si el token es inválido o ha expirado
    """
    try:
        # Decodificar el header sin verificar para obtener el kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise JWTError("Token no contiene 'kid' en el header")

        # Obtener JWKS
        jwks = await get_jwks()

        # Buscar la clave pública correspondiente
        key_data = get_public_key_from_jwks(jwks, kid)

        if not key_data:
            # Puede que las claves hayan rotado, limpiar caché y reintentar
            _jwks_cache.clear()
            jwks = await get_jwks()
            key_data = get_public_key_from_jwks(jwks, kid)

            if not key_data:
                raise JWTError(f"No se encontró clave pública para kid: {kid}")

        # Construir la clave pública RSA
        public_key = jwk.construct(key_data)

        # Verificar y decodificar el token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[JWT_ALGORITHM],
            audience=IBM_APPID_CLIENT_ID,
            issuer=IBM_APPID_ISSUER,
            options={
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_iat": True
            }
        )

        logger.debug(f"Token verificado exitosamente para usuario: {payload.get('email', payload.get('sub'))}")
        return payload

    except JWTError as e:
        logger.warning(f"Error de validación JWT: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al verificar token: {e}")
        raise JWTError(f"Error al verificar token: {e}")


def decode_token_unverified(token: str) -> Dict[str, Any]:
    """
    Decodifica un token sin verificar la firma.
    Útil solo para debugging, NO usar en producción para validación.
    """
    try:
        return jwt.get_unverified_claims(token)
    except JWTError as e:
        logger.error(f"Error al decodificar token: {e}")
        raise

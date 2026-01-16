# Sistema de Autenticación y Protección de Rutas

Este documento explica cómo funciona el sistema de login y la restricción de acceso a rutas en el Backend GM.

---

## Resumen Ejecutivo

El backend utiliza **JWT (JSON Web Tokens)** con **IBM App ID** como proveedor de identidad. No existe un endpoint de login tradicional en este backend; la autenticación se delega completamente a IBM App ID, y el backend solo valida los tokens emitidos por ese servicio.

---

## Arquitectura del Sistema

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│                 │      │                  │      │                 │
│  Cliente/App    │─────►│   IBM App ID     │─────►│  Backend GM     │
│  (Frontend)     │      │  (Login/Tokens)  │      │  (Validación)   │
│                 │      │                  │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │                        │
        │  1. Usuario se loguea   │                        │
        │────────────────────────►│                        │
        │                         │                        │
        │  2. Recibe JWT Token    │                        │
        │◄────────────────────────│                        │
        │                         │                        │
        │  3. Envía request con token                      │
        │─────────────────────────────────────────────────►│
        │                         │                        │
        │                         │  4. Valida firma JWT   │
        │                         │◄───────────────────────│
        │                         │                        │
        │  5. Respuesta (datos o 401)                      │
        │◄─────────────────────────────────────────────────│
```

---

## Componentes del Sistema

### 1. Configuración (`auth/config.py`)

Define los parámetros de conexión con IBM App ID:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `IBM_APPID_TENANT_ID` | ID del tenant de IBM App ID | `85e29de8-031c-4ea9-baf3-4d196998a2bb` |
| `IBM_APPID_REGION` | Región del servicio | `us-south` |
| `IBM_APPID_CLIENT_ID` | ID de la aplicación cliente | `25e71bc4-15ee-4837-946a-ecf8015c775c` |
| `JWT_ALGORITHM` | Algoritmo de firma | `RS256` |
| `JWKS_CACHE_TTL` | Tiempo de caché para claves públicas | `3600` segundos (1 hora) |

Estos valores se pueden sobrescribir con variables de entorno.

---

### 2. Manejador JWT (`auth/jwt_handler.py`)

Este módulo se encarga de verificar los tokens JWT. El proceso de verificación es:

```
Token JWT recibido
       │
       ▼
┌──────────────────────────────┐
│ 1. Extraer 'kid' del header  │  ← Identifica qué clave usar
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 2. Obtener JWKS de IBM       │  ← Claves públicas (cacheadas)
│    (JSON Web Key Set)        │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 3. Buscar clave por 'kid'    │  ← Si no existe, limpia caché
└──────────────────────────────┘     y reintenta
       │
       ▼
┌──────────────────────────────┐
│ 4. Verificar firma RS256     │  ← Criptografía asimétrica
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ 5. Validar claims:           │
│    - aud (audience)          │  ← Debe coincidir con CLIENT_ID
│    - iss (issuer)            │  ← Debe ser IBM App ID
│    - exp (expiración)        │  ← No debe estar expirado
│    - iat (issued at)         │  ← Tiempo de emisión válido
└──────────────────────────────┘
       │
       ▼
   Payload decodificado
```

**Funciones principales:**

- `get_jwks()`: Obtiene las claves públicas de IBM App ID (con caché de 1 hora)
- `verify_token(token)`: Verifica y decodifica un token JWT
- `get_public_key_from_jwks(jwks, kid)`: Busca la clave correspondiente al token

---

### 3. Dependencias de Autenticación (`auth/dependencies.py`)

Define dos funciones de dependencia para FastAPI:

#### `get_current_user` - Autenticación Obligatoria

```python
async def get_current_user(credentials) -> Dict[str, Any]:
```

- **Uso**: Endpoints que REQUIEREN autenticación
- **Comportamiento**:
  - Si no hay token → Error 401
  - Si token inválido → Error 401
  - Si token válido → Retorna datos del usuario

#### `get_current_user_optional` - Autenticación Opcional

```python
async def get_current_user_optional(credentials) -> Optional[Dict[str, Any]]:
```

- **Uso**: Endpoints públicos con funcionalidad extra para usuarios autenticados
- **Comportamiento**:
  - Si no hay token → Retorna `None`
  - Si token inválido → Retorna `None`
  - Si token válido → Retorna datos del usuario

---

## Estructura del Token JWT

Un token decodificado de IBM App ID contiene:

```json
{
    "sub": "abc123-user-id",
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "given_name": "Juan",
    "family_name": "Pérez",
    "roles": ["operador", "admin"],
    "groups": ["equipo-a"],
    "iss": "https://us-south.appid.cloud.ibm.com/oauth/v4/...",
    "aud": "25e71bc4-15ee-4837-946a-ecf8015c775c",
    "exp": 1704816000,
    "iat": 1704812400
}
```

---

## Protección de Rutas (`main.py`)

### Endpoints Públicos (Sin autenticación)

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Redirección a la documentación |
| `GET /health` | Health check del servicio |

### Endpoints Protegidos (Requieren token JWT)

La protección se aplica a nivel de router usando el parámetro `dependencies`:

```python
app.include_router(sensores_router, dependencies=[Depends(get_current_user)])
app.include_router(bitacoras_router, dependencies=[Depends(get_current_user)])
app.include_router(alertas_router, dependencies=[Depends(get_current_user)])
# ... etc
```

**Esto significa que TODOS los endpoints de estos routers requieren autenticación.**

| Router | Rutas Protegidas |
|--------|------------------|
| `sensores_router` | `/sensores/*` |
| `sensores_router_b` | Rutas adicionales de sensores |
| `bitacoras_router` | `/bitacoras/*` |
| `bitacoras_router_b` | Rutas adicionales de bitácoras |
| `alertas_router` | `/alertas/*` |

### Endpoints de Prueba de Autenticación

| Endpoint | Descripción |
|----------|-------------|
| `GET /auth/test` | Verifica que el token es válido |
| `GET /auth/me` | Obtiene información del usuario autenticado |

---

## Cómo Autenticarse

### Paso 1: Obtener Token de IBM App ID

El frontend debe autenticarse con IBM App ID para obtener un JWT. Este proceso ocurre fuera del backend.

### Paso 2: Enviar Token en las Peticiones

Incluir el token en el header `Authorization`:

```http
GET /sensores/data HTTP/1.1
Host: api.ejemplo.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6...
```

### Paso 3: El Backend Valida Automáticamente

Si el token es válido, la petición se procesa. Si no:

```json
{
    "detail": "Token invalido o expirado"
}
```
Status: `401 Unauthorized`

---

## Diagrama de Flujo de una Petición

```
Cliente envía petición a /sensores/data
                │
                ▼
       ┌────────────────┐
       │ ¿Tiene header  │
       │ Authorization? │
       └────────────────┘
              │
      ┌───────┴───────┐
      │ NO            │ SÍ
      ▼               ▼
  ┌────────┐   ┌──────────────┐
  │ 401    │   │ Extraer      │
  │ Error  │   │ token Bearer │
  └────────┘   └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Verificar    │
              │ firma JWT    │
              └──────────────┘
                      │
              ┌───────┴───────┐
              │ INVÁLIDO      │ VÁLIDO
              ▼               ▼
          ┌────────┐   ┌──────────────┐
          │ 401    │   │ Verificar    │
          │ Error  │   │ exp, iss,    │
          └────────┘   │ aud, iat     │
                       └──────────────┘
                              │
                      ┌───────┴───────┐
                      │ FALLA         │ PASA
                      ▼               ▼
                  ┌────────┐   ┌──────────────┐
                  │ 401    │   │ Ejecutar     │
                  │ Error  │   │ endpoint     │
                  └────────┘   │ (user_data   │
                               │ disponible)  │
                               └──────────────┘
```

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `401 - Token invalido o expirado` | Token JWT no válido | Obtener nuevo token de IBM App ID |
| `401 - No authorization header` | Falta el header Authorization | Agregar `Authorization: Bearer <token>` |
| `401 - Error de autenticacion` | Error interno de validación | Verificar configuración de IBM App ID |

---

## Notas Importantes

1. **No hay endpoint de login**: La autenticación se maneja externamente via IBM App ID
2. **No hay logout**: Al ser stateless, el cliente simplemente deja de enviar el token
3. **Roles no se validan**: Se extraen del token pero no se usan para autorización
4. **Tokens no se refrescan**: El cliente debe obtener nuevos tokens de IBM App ID cuando expiran
5. **Cache de claves**: Las claves públicas se cachean 1 hora para mejor rendimiento

---

## Librerías Utilizadas

- `python-jose[cryptography]`: Manejo de JWT
- `httpx`: Cliente HTTP async para obtener JWKS
- `cachetools`: Cache TTL para las claves públicas
- `fastapi`: Framework web con sistema de dependencias

---

## Configuración de Variables de Entorno

```bash
# Opcional: Sobrescribir configuración de IBM App ID
IBM_APPID_TENANT_ID=tu-tenant-id
IBM_APPID_REGION=us-south
IBM_APPID_CLIENT_ID=tu-client-id

# CORS
ALLOWED_ORIGINS=https://tu-frontend.com,https://otro-dominio.com
```

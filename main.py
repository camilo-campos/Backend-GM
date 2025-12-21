import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from rutas.sensores_router import router as sensores_router
from rutas.alertas_umbral import router as alertas_router
from rutas.bitacoras_router import router as bitacoras_router
from rutas.bitacoras_router_b import router as bitacoras_router_b
from rutas.sensores_router_B import router_b as sensores_router_b
from modelos.database import engine, Base, SessionLocal
from auth.dependencies import get_current_user, get_current_user_optional

load_dotenv()

app = FastAPI(
    title="backend GM",
    description="backend para obtener los valores de los sensores para graficar y predecir",
    version="1.0"
)

# Crear todas las tablas si no existen
Base.metadata.create_all(bind=engine)

# Configurar CORS - URLs permitidas
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ENDPOINTS PUBLICOS
# ==========================================

@app.get("/")
async def redirect_to_docs():
    """Redirige a la documentacion de la API"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Endpoint de health check - publico"""
    return {"status": "ok", "message": "Backend GM funcionando correctamente"}


# ==========================================
# ENDPOINTS DE PRUEBA DE AUTENTICACION
# ==========================================

@app.get("/auth/test")
async def test_auth(current_user: dict = Depends(get_current_user)):
    """
    Endpoint de prueba para verificar autenticacion.
    Requiere token JWT valido en el header Authorization.
    """
    return {
        "message": "Autenticacion exitosa",
        "user": {
            "email": current_user.get("email"),
            "name": current_user.get("name"),
            "sub": current_user.get("sub")
        }
    }


@app.get("/auth/me")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtiene la informacion completa del usuario autenticado.
    """
    return {
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "given_name": current_user.get("given_name"),
        "family_name": current_user.get("family_name"),
        "sub": current_user.get("sub"),
        "roles": current_user.get("roles", []),
        "groups": current_user.get("groups", [])
    }


# ==========================================
# REGISTRAR ROUTERS
# ==========================================
# NOTA: Para proteger todos los endpoints de un router, agregar:
# dependencies=[Depends(get_current_user)]
#
# Ejemplo:
# app.include_router(sensores_router, dependencies=[Depends(get_current_user)])

# Todas las rutas protegidas con autenticacion JWT
app.include_router(sensores_router, dependencies=[Depends(get_current_user)])
app.include_router(bitacoras_router, dependencies=[Depends(get_current_user)])
app.include_router(bitacoras_router_b, dependencies=[Depends(get_current_user)])
app.include_router(alertas_router, dependencies=[Depends(get_current_user)])
app.include_router(sensores_router_b, dependencies=[Depends(get_current_user)])

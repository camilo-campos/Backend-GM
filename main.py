from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rutas.sensores_router import router as sensores_router


app = FastAPI(title="backend GM",
              description="backend para obtener los valores de los graficos y hacer la prediccion",
              version="1.0")

from modelos.database import engine, Base

# Crear todas las tablas
Base.metadata.create_all(bind=engine)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers existentes

app.include_router(sensores_router)

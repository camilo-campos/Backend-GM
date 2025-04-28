import os
import asyncio
import select
import json
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from rutas.sensores_router import router as sensores_router 
from rutas.alertas_umbral import router as alertas_router 
from rutas.bitacoras_router import router as bitacoras_router
from modelos.database import engine, Base, SessionLocal

# Importa tus funciones de predicción y manejo de bitácora
from rutas.sensores_router import (
    predecir_corriente, predecir_salida, predecir_presion,
     predecir_temperatura_ambiental,
    predecir_temp_empuje, predecir_temp_motor,
     predecir_vibracion,
    predecir_voltaje
)


app = FastAPI(
    title="backend GM",
    description="backend para obtener los valores de los sensores para graficar y predecir",
    version="1.0"
)

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Crear todas las tablas si no existen
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
app.include_router(bitacoras_router)
app.include_router(alertas_router)





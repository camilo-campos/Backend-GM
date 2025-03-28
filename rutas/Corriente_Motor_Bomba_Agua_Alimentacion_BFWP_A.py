from fastapi import APIRouter
from funciones.isolation_forest import predecir_sensores
from esquemas import DatosSensores  # Importamos la clase de esquema
import joblib

# Cargar el modelo
modelo = joblib.load("../modelos_prediccion/model_Corriente Motor Bomba Agua Alimentacion BFWP A (A).pkl")

router = APIRouter()

@router.post("/datos")
def recibir_datos(datos_sensores: DatosSensores):
    prediccion = predecir_sensores(datos_sensores.datos, modelo)
    return {"prediccion": prediccion.tolist()}  

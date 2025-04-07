from fastapi import APIRouter, Depends , HTTPException
from esquemas.esquema import SensorInput
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import SensorCorriente, SensorPresionAgua, SensorSalidaAgua

router = APIRouter(prefix="/sensores", tags=["Sensores"])



# Datos por defecto
DEFAULT_SENSORES_CORRIENTE = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 10.5, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 12.7, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 10.5, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 12.7, "clasificacion": -1},
    {"id": 5, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:04", "valor_sensor": 10.5, "clasificacion": 1},
    {"id": 6, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:05", "valor_sensor": 12.7, "clasificacion": -1},
    {"id": 7, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:06", "valor_sensor": 10.5, "clasificacion": 1},
    {"id": 8, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:07", "valor_sensor": 12.7, "clasificacion": -1}
]

DEFAULT_SENSORES_SALIDA_AGUA = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 13:00:00", "tiempo_sensor": "13:00", "valor_sensor": 20.1, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 13:05:00", "tiempo_sensor": "13:01", "valor_sensor": 22.3, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 13:00:00", "tiempo_sensor": "13:02", "valor_sensor": 20.1, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 13:05:00", "tiempo_sensor": "13:03", "valor_sensor": 22.3, "clasificacion": -1},
    {"id": 5, "tiempo_ejecucion": "2024-07-30 13:00:00", "tiempo_sensor": "13:04", "valor_sensor": 20.1, "clasificacion": 1},
    {"id": 6, "tiempo_ejecucion": "2024-07-30 13:05:00", "tiempo_sensor": "13:05", "valor_sensor": 22.3, "clasificacion": -1},
    {"id": 7, "tiempo_ejecucion": "2024-07-30 13:00:00", "tiempo_sensor": "13:06", "valor_sensor": 20.1, "clasificacion": 1},
    {"id": 8, "tiempo_ejecucion": "2024-07-30 13:05:00", "tiempo_sensor": "13:07", "valor_sensor": 22.3, "clasificacion": -1}
]

DEFAULT_SENSORES_PRESION_AGUA = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 14:00:00", "tiempo_sensor": "14:00", "valor_sensor": 30.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 14:05:00", "tiempo_sensor": "14:01", "valor_sensor": 28.9, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 14:00:00", "tiempo_sensor": "14:02", "valor_sensor": 30.2, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 14:05:00", "tiempo_sensor": "14:03", "valor_sensor": 28.9, "clasificacion": -1},
    {"id": 5, "tiempo_ejecucion": "2024-07-30 14:00:00", "tiempo_sensor": "14:04", "valor_sensor": 30.2, "clasificacion": 1},
    {"id": 6, "tiempo_ejecucion": "2024-07-30 14:05:00", "tiempo_sensor": "14:05", "valor_sensor": 28.9, "clasificacion": -1},
    {"id": 7, "tiempo_ejecucion": "2024-07-30 14:00:00", "tiempo_sensor": "14:06", "valor_sensor": 30.2, "clasificacion": 1},
    {"id": 8, "tiempo_ejecucion": "2024-07-30 14:05:00", "tiempo_sensor": "14:07", "valor_sensor": 28.9, "clasificacion": -1},
    {"id": 9, "tiempo_ejecucion": "2024-07-30 14:00:00", "tiempo_sensor": "14:08", "valor_sensor": 30.2, "clasificacion": 1},
    {"id": 10, "tiempo_ejecucion": "2024-07-30 14:05:00", "tiempo_sensor": "14:09", "valor_sensor": 28.9, "clasificacion": -1}
]


import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del archivo actual
MODELS_DIR = os.path.join(BASE_DIR, "..", "modelos_prediccion")  # Ruta absoluta a la carpeta de modelos

modelos = {
    "corriente_motor": joblib.load(os.path.join(MODELS_DIR, "model_Corriente Motor Bomba Agua Alimentacion BFWP A (A).pkl")),
    
    "presion_agua": joblib.load(os.path.join(MODELS_DIR, "model_Presión Agua Alimentación AP (barg).pkl")),
    "salida_bomba": joblib.load(os.path.join(MODELS_DIR, "model_Salida de Bomba de Alta Presión.pkl")),
    
}


def predecir_sensores(datos, modelo):
    # Convierte los datos en un DataFrame
    df_nuevo = pd.DataFrame(datos, columns=["valor"])
    # Aplica la predicción y retorna la lista resultante
    return modelo.predict(df_nuevo).tolist()



@router.post("/prediccion_corriente")
async def predecir_corriente(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        # Realizar la predicción (el modelo devuelve 1 o -1)
        prediccion = predecir_sensores([[sensor.valor]], modelos["corriente_motor"])
        clase = int(prediccion[0])

        # Buscar el registro en la base de datos por ID
        sensor_db = db.query(SensorCorriente).filter(SensorCorriente.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        # Actualizar la clasificación
        sensor_db.clasificacion = clase
        db.commit()

        # Traducción opcional de la clase
        descripcion = "Normal" if clase == 1 else "Anomalía"

        return {
            "id_sensor": sensor.id_sensor,
            "valor": sensor.valor,
            "prediccion": clase,
            "descripcion": descripcion,
            "mensaje": "Clasificación actualizada correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/prediccion_salida-agua")
async def predecir_salida(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        # Realizar la predicción (el modelo devuelve 1 o -1)
        prediccion = predecir_sensores([[sensor.valor]], modelos["salida_bomba"])
        clase = int(prediccion[0])

        # Buscar el registro en la base de datos por ID
        sensor_db = db.query(SensorSalidaAgua).filter(SensorSalidaAgua.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        # Actualizar la clasificación
        sensor_db.clasificacion = clase
        db.commit()

        # Traducción opcional de la clase
        descripcion = "Normal" if clase == 1 else "Anomalía"

        return {
            "id_sensor": sensor.id_sensor,
            "valor": sensor.valor,
            "prediccion": clase,
            "descripcion": descripcion,
            "mensaje": "Clasificación actualizada correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/prediccion_presion-agua")
async def predecir_presion(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        # Realizar la predicción (el modelo devuelve 1 o -1)
        prediccion = predecir_sensores([[sensor.valor]], modelos["presion_agua"])
        clase = int(prediccion[0])

        # Buscar el registro en la base de datos por ID
        sensor_db = db.query(SensorPresionAgua).filter(SensorPresionAgua.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        # Actualizar la clasificación
        sensor_db.clasificacion = clase
        db.commit()

        # Traducción opcional de la clase
        descripcion = "Normal" if clase == 1 else "Anomalía"

        return {
            "id_sensor": sensor.id_sensor,
            "valor": sensor.valor,
            "prediccion": clase,
            "descripcion": descripcion,
            "mensaje": "Clasificación actualizada correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Ruta para obtener datos de sensores de corriente
@router.get("/corriente")
async def get_sensores_corriente(db: Session = Depends(get_db)):
    try:
        sensores = (
            db.query(SensorCorriente)
            .order_by(SensorCorriente.id.desc())  # Ordenar en orden descendente
            .limit(40)  # Obtener solo los últimos 40 registros
            .all()
        )
        
        if not sensores:
            return {
                "message": "No hay datos en la base de datos, devolviendo valores por defecto",
                "data": DEFAULT_SENSORES_CORRIENTE,
            }

            
        return sensores
    except Exception as e:
        print("Error:", e)
        return {
            "message": "Error al conectar con la base de datos, devolviendo valores por defecto",
            "data": DEFAULT_SENSORES_CORRIENTE,
        }



# Ruta para obtener datos de sensores de salida de agua
@router.get("/salida-agua")
async def get_sensores_salida_agua(db: Session = Depends(get_db)):
    try:
        sensores = (db.query(SensorSalidaAgua).order_by(SensorSalidaAgua.id.desc())  # Ordenar en orden descendente
            .limit(40)  # Obtener solo los últimos 40 registros
            .all())
        if not sensores:
            return {"message": "No hay datos en la base de datos, devolviendo valores por defecto", "data": DEFAULT_SENSORES_SALIDA_AGUA}
        return sensores
    except:
        return {"message": "Error al conectar con la base de datos, devolviendo valores por defecto", "data": DEFAULT_SENSORES_SALIDA_AGUA}

# Ruta para obtener datos de sensores de presión de agua
@router.get("/presion-agua")
async def get_sensores_presion_agua(db: Session = Depends(get_db)):
    try:
        sensores = (db.query(SensorPresionAgua).order_by(SensorPresionAgua.id.desc())  # Ordenar en orden descendente
            .limit(40)  # Obtener solo los últimos 40 registros
            .all())
        if not sensores:
            return {"message": "No hay datos en la base de datos, devolviendo valores por defecto", "data": DEFAULT_SENSORES_PRESION_AGUA}
        return sensores
    except:
        return {"message": "Error al conectar con la base de datos, devolviendo valores por defecto", "data": DEFAULT_SENSORES_PRESION_AGUA}

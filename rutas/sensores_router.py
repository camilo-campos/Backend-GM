from fastapi import APIRouter, Depends , HTTPException
from esquemas.esquema import SensorInput
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import SensorCorriente, SensorPresionAgua, SensorSalidaAgua , SensorMw_brutos_generacion_gas , SensorTemperatura_Ambiental , SensorTemperatura_descanso_interna_empuje_bomba_1aa , SensorTemperatura_descanso_interna_motor_bomba_1a , SensorTemperatura_descanso_interno_bomba_1a ,SensorVibracion_axial_descanso ,SensorVoltaje_barra

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
    "mw_brutos_gas": joblib.load(os.path.join(MODELS_DIR, "model_MW Brutos de Generación Total Gas (MW).pkl")),
    "presion_agua": joblib.load(os.path.join(MODELS_DIR, "model_Presión Agua Alimentación AP (barg).pkl")),
    "salida_bomba": joblib.load(os.path.join(MODELS_DIR, "model_Salida de Bomba de Alta Presión.pkl")),
    "temperatura_ambiental": joblib.load(os.path.join(MODELS_DIR, "model_Temperatura Ambiental (°C).pkl")),
    "temp_descanso_bomba_1a": joblib.load(os.path.join(MODELS_DIR, "model_Temperatura Descanso Interno Bomba 1A (°C).pkl")),
    "temp_descanso_empuje_bomba_1a": joblib.load(os.path.join(MODELS_DIR, "model_Temperatura Descanso Interno Empuje Bomba 1A (°C).pkl")),
    "temp_descanso_motor_bomba_1a": joblib.load(os.path.join(MODELS_DIR, "model_Temperatura Descanso Interno Motor Bomba 1A (°C).pkl")),
    "vibracion_axial_empuje": joblib.load(os.path.join(MODELS_DIR, "model_Vibración Axial Descanso Emp Bomba 1A (ms).pkl")),
    "voltaje_barra": joblib.load(os.path.join(MODELS_DIR, "model_Voltaje Barra 6,6KV (V).pkl")),
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


@router.post("/prediccion_mw-brutos-gas")
async def predecir_mw(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["mw_brutos_gas"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorMw_brutos_generacion_gas).filter(SensorMw_brutos_generacion_gas.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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


@router.post("/prediccion_temperatura-ambiental")
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["temperatura_ambiental"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorTemperatura_Ambiental).filter(SensorTemperatura_Ambiental.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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


@router.post("/prediccion_temp-descanso-bomba-1a")
async def predecir_temp_bomba(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["temp_descanso_bomba_1a"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorTemperatura_descanso_interno_bomba_1a).filter(SensorTemperatura_descanso_interno_bomba_1a.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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




@router.post("/prediccion_temp-empuje-bomba-1a")
async def predecir_temp_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["temp_descanso_empuje_bomba_1a"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorTemperatura_descanso_interna_empuje_bomba_1aa).filter(SensorTemperatura_descanso_interna_empuje_bomba_1aa.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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



@router.post("/prediccion_temp-motor-bomba-1a")
async def predecir_temp_motor(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["temp_descanso_motor_bomba_1a"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorTemperatura_descanso_interna_motor_bomba_1a).filter(SensorTemperatura_descanso_interna_motor_bomba_1a.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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



@router.post("/prediccion_vibracion-axial")
async def predecir_vibracion(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["vibracion_axial_empuje"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorVibracion_axial_descanso).filter(SensorVibracion_axial_descanso.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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




@router.post("/prediccion_voltaje-barra")
async def predecir_voltaje(sensor: SensorInput, db: Session = Depends(get_db)):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos["voltaje_barra"])
        clase = int(prediccion[0])

        sensor_db = db.query(SensorVoltaje_barra).filter(SensorVoltaje_barra.id == sensor.id_sensor).first()
        if not sensor_db:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")

        sensor_db.clasificacion = clase
        db.commit()

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
# Helper genérica
async def _get_and_classify(db: Session, SensorModel, model_key, default_data):
    sensores = (
        db.query(SensorModel)
          .order_by(SensorModel.id.desc())
          .limit(40)
          .all()
    )
    if not sensores:
        return {"message": f"No hay datos en la base de datos, devolviendo valores por defecto", "data": default_data}

    no_clasificados = [s for s in sensores if s.clasificacion is None]
    if no_clasificados:
        datos = [[s.valor_sensor] for s in no_clasificados]
        preds = predecir_sensores(datos, modelos[model_key])
        for obj, cl in zip(no_clasificados, preds):
            obj.clasificacion = int(cl)
            db.add(obj)
        db.commit()
        for obj in no_clasificados:
            db.refresh(obj)

    salida = []
    for s in reversed(sensores):
        salida.append({
            "clasificacion": s.clasificacion,
            "tiempo_sensor": s.tiempo_sensor,
            "valor_sensor": s.valor_sensor,
            "id": s.id,
            "tiempo_ejecucion": s.tiempo_ejecucion.isoformat() if s.tiempo_ejecucion else None
        })
    return salida

# Rutas
@router.get("/corriente")
async def get_sensores_corriente(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorCorriente, "corriente_motor", DEFAULT_SENSORES_CORRIENTE)

@router.get("/salida-agua")
async def get_sensores_salida_agua(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorSalidaAgua, "salida_bomba", DEFAULT_SENSORES_SALIDA_AGUA)

@router.get("/presion-agua")
async def get_sensores_presion_agua(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorPresionAgua, "presion_agua", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/generacion-gas")
async def get_sensores_generacion_gas(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorMw_brutos_generacion_gas, "mw_brutos_gas", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/temperatura-ambiental")
async def get_sensores_temperatura_ambiental(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorTemperatura_Ambiental, "temperatura_ambiental", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/temperatura-interna-empuje")
async def get_sensores_temp_interna_empuje(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_empuje_bomba_1aa, "temp_descanso_empuje_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/temperatura-descanso-motor")
async def get_sensores_temp_descanso_motor(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_motor_bomba_1a, "temp_descanso_motor_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/temperatura-descanso-bomba")
async def get_sensores_temp_descanso_bomba(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorTemperatura_descanso_interno_bomba_1a, "temp_descanso_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/vibracion-axial")
async def get_sensores_vibracion_axial(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorVibracion_axial_descanso, "vibracion_axial_empuje", DEFAULT_SENSORES_PRESION_AGUA)

@router.get("/voltaje-barra")
async def get_sensores_voltaje_barra(db: Session = Depends(get_db)):
    return await _get_and_classify(db, SensorVoltaje_barra, "voltaje_barra", DEFAULT_SENSORES_PRESION_AGUA)
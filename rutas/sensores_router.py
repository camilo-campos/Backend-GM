from fastapi import APIRouter, Depends , HTTPException
from datetime import datetime, timedelta
from datetime import datetime, timezone

from sqlalchemy import func
from esquemas.esquema import SensorInput
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import  Alerta, SensorCorriente, SensorPresionAgua, SensorSalidaAgua , SensorMw_brutos_generacion_gas , SensorTemperatura_Ambiental , SensorTemperatura_descanso_interna_empuje_bomba_1aa , SensorTemperatura_descanso_interna_motor_bomba_1a , SensorTemperatura_descanso_interno_bomba_1a ,SensorVibracion_axial_descanso ,SensorVoltaje_barra

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

def predecir_sensores(datos, modelo):
    """
    Convierte datos en DataFrame y aplica modelo para predecir 1 o -1.
    """
    df_nuevo = pd.DataFrame(datos, columns=["valor"])
    return modelo.predict(df_nuevo).tolist()


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


# ——— Configuración de umbrales por sensor ———
UMBRAL_SENSORES = {
    'prediccion_corriente': {
        "umbral_minimo": 202,
        "umbral_alerta": 252,
        "umbral_critica": 302,
    },
    'prediccion_salida-agua': {
        "umbral_minimo": 97,
        "umbral_alerta": 147,
        "umbral_critica": 197,
    },
    'prediccion_presion-agua': {
        "umbral_minimo": 235,
        "umbral_alerta": 285,
        "umbral_critica": 335,
    },
    'prediccion_mw-brutos-gas': {
        "umbral_minimo": 112,
        "umbral_alerta": 162,
        "umbral_critica": 212,
    },
    'prediccion_temperatura-ambiental': {
        "umbral_minimo": 28,
        "umbral_alerta": 78,
        "umbral_critica": 128,
    },
    'prediccion_temp-descanso-bomba-1a': {
        "umbral_minimo": 171,
        "umbral_alerta": 221,
        "umbral_critica": 271,
    },
    'prediccion_temp-empuje-bomba-1a': {
        "umbral_minimo": 110,
        "umbral_alerta": 160,
        "umbral_critica": 210,
    },
    'prediccion_temp-motor-bomba-1a': {
        "umbral_minimo": 25,
        "umbral_alerta": 75,
        "umbral_critica": 125,
    },
    'prediccion_vibracion-axial': {
        "umbral_minimo": 58,
        "umbral_alerta": 108,
        "umbral_critica": 158,
    },
    'prediccion_voltaje-barra': {
        "umbral_minimo": 36,
        "umbral_alerta": 86,
        "umbral_critica": 136,
    }
}

async def predecir_generico(sensor: SensorInput, db: Session, modelo_key: str, tipo_sensor: str, umbral_sensor_key: str):
    try:
        prediccion = predecir_sensores([[sensor.valor]], modelos[modelo_key])
        clase = int(prediccion[0])
        descripcion = "Normal" if clase == 1 else "Anomalía"

        lectura = db.query(SensorCorriente).get(sensor.id_sensor)
        if not lectura:
            raise HTTPException(404, "Lectura no encontrada")

        lectura.clasificacion = clase
        lectura.tiempo_ejecucion = datetime.now(timezone.utc)
        db.commit()

        if clase == -1:
            conteo = contar_anomalias(db)
            nuevo_nivel = determinar_alerta(conteo, tipo_sensor=umbral_sensor_key)
            if nuevo_nivel:
                device_id = 1  # Cambiar si tienes distintos IDs para cada tipo de sensor
                nivel_num = nivel_numerico(nuevo_nivel)
                ultima_alerta = (
                    db.query(Alerta)
                      .filter(
                          Alerta.sensor_id == device_id,
                          Alerta.tipo_sensor == tipo_sensor
                      )
                      .order_by(Alerta.id.desc())
                      .first()
                )
                prev_nivel = nivel_numerico(ultima_alerta.descripcion.split(":")[0]) if ultima_alerta else 0
                if nivel_num > prev_nivel:
                    alerta = Alerta(
                        sensor_id=device_id,
                        tipo_sensor=tipo_sensor,
                        descripcion=f"{nuevo_nivel}: {conteo} anomalías en {VENTANA_HORAS}h"
                    )
                    db.add(alerta)
                    db.commit()

        return {
            "id_sensor": sensor.id_sensor,
            "valor": sensor.valor,
            "prediccion": clase,
            "descripcion": descripcion,
            "mensaje": "Proceso completado"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


VENTANA_HORAS = 8  # ventana de tiempo (horas)
# ———————————————————————————————————————————

def contar_anomalias(db: Session) -> int:
    """
    Cuenta cuántas filas en sensores_corriente tienen clasificacion == -1
    en las últimas VENTANA_HORAS horas.
    """
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(hours=VENTANA_HORAS)
    print(f"[DEBUG] Conteo anomalías entre {inicio.isoformat()} y {ahora.isoformat()}")
    return (
        db.query(func.count(SensorCorriente.id))
          .filter(SensorCorriente.clasificacion == -1)
          .filter(
              SensorCorriente.tiempo_ejecucion.between(inicio, ahora)
          )
          .scalar()
    )


def determinar_alerta(conteo: int, tipo_sensor: str) -> str:
    """
    Devuelve 'AVISO', 'ALERTA' o 'CRÍTICA' según el umbral configurado.
    """
    umbrales = UMBRAL_SENSORES.get(tipo_sensor, {})
    if conteo >= umbrales.get("umbral_critica", float('inf')):
        return "CRÍTICA"
    if conteo >= umbrales.get("umbral_alerta", float('inf')):
        return "ALERTA"
    if conteo >= umbrales.get("umbral_minimo", float('inf')):
        return "AVISO"
    return None


def nivel_numerico(nivel: str) -> int:
    """Convierte nivel de alerta a número para comparación."""
    return {"AVISO": 1, "ALERTA": 2, "CRÍTICA": 3}.get(nivel, 0)



# ———— Ruta para predicción de corriente ————
@router.post("/prediccion_corriente")
async def predecir_corriente(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="corriente_motor",          # el nombre del modelo a usar
        tipo_sensor="corriente",                # tipo de sensor para registrar alerta
        umbral_sensor_key="prediccion_corriente" # clave para consultar UMBRAL_SENSORES
    )


# ———— Ruta para predicción de salida de agua ————
@router.post("/prediccion_salida-agua")
async def predecir_salida(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="salida_bomba",
        tipo_sensor="salida-agua",
        umbral_sensor_key="prediccion_salida-agua"
    )


# ———— Ruta para predicción de presión de agua ————
@router.post("/prediccion_presion-agua")
async def predecir_presion(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="presion_bomba",
        tipo_sensor="presion-agua",
        umbral_sensor_key="prediccion_presion-agua"
    )


# ———— Ruta para predicción de megavatios brutos de gas ————
@router.post("/prediccion_mw-brutos-gas")
async def predecir_mw_gas(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="mw_brutos_gas",
        tipo_sensor="mw-brutos-gas",
        umbral_sensor_key="prediccion_mw-brutos-gas"
    )


# ———— Ruta para predicción de temperatura ambiental ————
@router.post("/prediccion_temperatura-ambiental")
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="temperatura_ambiental",
        tipo_sensor="temperatura-ambiental",
        umbral_sensor_key="prediccion_temperatura-ambiental"
    )


# ———— Ruta para predicción de temperatura descanso bomba 1A ————
@router.post("/prediccion_temp-descanso-bomba-1a")
async def predecir_temp_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="temp_descanso_bomba_1a",
        tipo_sensor="temp-descanso-bomba-1a",
        umbral_sensor_key="prediccion_temp-descanso-bomba-1a"
    )


# ———— Ruta para predicción de temperatura empuje bomba 1A ————
@router.post("/prediccion_temp-empuje-bomba-1a")
async def predecir_temp_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="temp_empuje_bomba_1a",
        tipo_sensor="temp-empuje-bomba-1a",
        umbral_sensor_key="prediccion_temp-empuje-bomba-1a"
    )


# ———— Ruta para predicción de temperatura motor bomba 1A ————
@router.post("/prediccion_temp-motor-bomba-1a")
async def predecir_temp_motor(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="temp_motor_bomba_1a",
        tipo_sensor="temp-motor-bomba-1a",
        umbral_sensor_key="prediccion_temp-motor-bomba-1a"
    )


# ———— Ruta para predicción de vibración axial ————
@router.post("/prediccion_vibracion-axial")
async def predecir_vibracion(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="vibracion_axial",
        tipo_sensor="vibracion-axial",
        umbral_sensor_key="prediccion_vibracion-axial"
    )


# ———— Ruta para predicción de voltaje barra ————
@router.post("/prediccion_voltaje-barra")
async def predecir_voltaje(sensor: SensorInput, db: Session = Depends(get_db)):
    return await predecir_generico(
        sensor=sensor,
        db=db,
        modelo_key="voltaje_barra",
        tipo_sensor="voltaje-barra",
        umbral_sensor_key="prediccion_voltaje-barra"
    )



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
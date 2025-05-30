from fastapi import APIRouter, Depends , HTTPException
from datetime import datetime, timedelta
from datetime import datetime, timezone
import numpy as np
from typing import Optional , List
from fastapi import Query
from datetime import datetime
from sqlalchemy import func
from esquemas.esquema import SensorInput, PrediccionBombaResponse, PrediccionBombaBInput, PrediccionBombaBOutput
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos_b.modelos_b import (Alerta, SensorCorriente, SensorExcentricidadBomba, SensorFlujoDescarga,
    SensorFlujoAguaDomoAP, SensorFlujoAguaDomoMP, SensorFlujoAguaRecalentador, SensorFlujoAguaVaporAlta,
    SensorPresionAgua, SensorTemperaturaAmbiental, SensorTemperaturaAguaAlim, SensorTemperaturaEstator,
    SensorVibracionAxialEmpuje, SensorVibracionXDescanso, SensorVibracionYDescanso, SensorVoltajeBarra,
    PrediccionBombaB )

router_b = APIRouter(prefix="/sensores_b", tags=["Sensores_b"])



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

# Valores por defecto para los nuevos sensores (usando el mismo patrón)
DEFAULT_SENSORES_EXCENTRICIDAD = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 5.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 6.1, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 5.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 6.2, "clasificacion": -1}
]

DEFAULT_SENSORES_FLUJO_DESCARGA = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 45.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 46.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 45.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 46.9, "clasificacion": -1}
]

DEFAULT_SENSORES_FLUJO_AGUA_DOMO_AP = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 35.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 36.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 35.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 36.9, "clasificacion": -1}
]

DEFAULT_SENSORES_FLUJO_AGUA_DOMO_MP = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 38.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 39.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 38.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 39.9, "clasificacion": -1}
]

DEFAULT_SENSORES_FLUJO_AGUA_RECALENTADOR = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 42.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 43.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 42.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 43.9, "clasificacion": -1}
]

DEFAULT_SENSORES_FLUJO_AGUA_VAPOR_ALTA = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 52.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 53.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 52.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 53.9, "clasificacion": -1}
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

DEFAULT_SENSORES_TEMPERATURA_AMBIENTAL = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 25.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 26.1, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 25.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 26.2, "clasificacion": -1}
]

DEFAULT_SENSORES_TEMPERATURA_AGUA_ALIM = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 65.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 66.1, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 65.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 66.2, "clasificacion": -1}
]

DEFAULT_SENSORES_TEMPERATURA_ESTATOR = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 75.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 76.1, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 75.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 76.2, "clasificacion": -1}
]

DEFAULT_SENSORES_VIBRACION_AXIAL_EMPUJE = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 2.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 2.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 2.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 2.9, "clasificacion": -1}
]

DEFAULT_SENSORES_VIBRACION_X_DESCANSO = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 1.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 1.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 1.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 1.9, "clasificacion": -1}
]

DEFAULT_SENSORES_VIBRACION_Y_DESCANSO = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 1.5, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 1.9, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 1.6, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 2.0, "clasificacion": -1}
]

DEFAULT_SENSORES_VOLTAJE_BARRA = [
    {"id": 1, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:00", "valor_sensor": 220.2, "clasificacion": 1},
    {"id": 2, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:01", "valor_sensor": 221.8, "clasificacion": -1},
    {"id": 3, "tiempo_ejecucion": "2024-07-30 12:00:00", "tiempo_sensor": "12:02", "valor_sensor": 220.3, "clasificacion": 1},
    {"id": 4, "tiempo_ejecucion": "2024-07-30 12:05:00", "tiempo_sensor": "12:03", "valor_sensor": 221.9, "clasificacion": -1}
]


import os
import joblib
import pandas as pd
import time
import logging
from functools import lru_cache

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del archivo actual
MODELS_DIR = os.path.join(BASE_DIR, "..", "modelos_prediccion_b")  # Ruta absoluta a la carpeta de modelos

# Mapa de claves de modelo a rutas de archivo
MODEL_PATHS = {
    "corriente_motor": "Corriente_MTR_BBA_Agua_Alim_1B_B.pkl",
    "excentricidad_bomba": "Excentricidad_Bomba_1B_B.pkl",
    "flujo_descarga": "Flujo_Descarga_AP_BAA_AE01B_B.pkl",
    "flujo_agua_domo_ap": "Flujo_de_Agua_Alimentaci_n_Domo_AP_Compensated_B.pkl",
    "flujo_agua_domo_mp": "Flujo_de_Agua_Alimentaci_n_Domo_MP_Compensated_B.pkl",
    "flujo_agua_recalentador": "Flujo_de_Agua_Atemp_Recale_Calient_RH_B.pkl",
    "flujo_agua_vapor_alta": "Flujo_de_Agua_Atemp_Vapor_Alta_AP_SH_B.pkl",
    "presion_agua": "Presi_n_Agua_Alimentaci_n_Econ._AP_B.pkl",
    "temperatura_ambiental": "Temp_Ambiental_B.pkl",
    "temperatura_agua_alim": "Temperatura_Agua_Alim_AP_B.pkl",
    "temperatura_estator": "Temperatura_Estator_MTR_BBA_AA_1B_A_B.pkl",
    "vibracion_axial_empuje": "Vibraci_n_Axial_Descanso_Emp_Bomba_1B_B.pkl",
    "vibracion_x_descanso": "Vibraci_n_X_Descanso_Interno_Bomba_1B_B.pkl",
    "vibracion_y_descanso": "Vibraci_n_Y_Descanso_Interno_Bomba_1B_B.pkl",
    "voltaje_barra": "Voltaje_Barra_6_6KV_B.pkl",
}

class ModelRegistry:
    """Registro de modelos con carga perezosa (lazy loading)"""
    _models = {}
    _load_times = {}
    _access_count = {}
    
    @classmethod
    def get_model(cls, model_key):
        """Obtiene un modelo, cargándolo si es necesario"""
        if model_key not in MODEL_PATHS:
            raise KeyError(f"Modelo no reconocido: {model_key}")
        
        # Cargar el modelo si aún no está en memoria
        if model_key not in cls._models:
            start_time = time.time()
            logger.info(f"Cargando modelo {model_key}...")
            
            model_path = os.path.join(MODELS_DIR, MODEL_PATHS[model_key])
            cls._models[model_key] = joblib.load(model_path)
            
            load_time = time.time() - start_time
            cls._load_times[model_key] = load_time
            cls._access_count[model_key] = 0
            
            logger.info(f"Modelo {model_key} cargado en {load_time:.4f} segundos")
        
        # Incrementar el contador de accesos
        cls._access_count[model_key] = cls._access_count.get(model_key, 0) + 1
        
        return cls._models[model_key]
    
    @classmethod
    def get_stats(cls):
        """Devuelve estadísticas de uso de los modelos"""
        return {
            "loaded_models": list(cls._models.keys()),
            "load_times": cls._load_times,
            "access_count": cls._access_count
        }

# Para mantener compatibilidad con código existente, creamos un objeto modelos que simula el diccionario original
class ModelsDict:
    def __getitem__(self, key):
        return ModelRegistry.get_model(key)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def keys(self):
        return MODEL_PATHS.keys()
    
    def items(self):
        for key in MODEL_PATHS.keys():
            yield key, ModelRegistry.get_model(key)

# Reemplaza el diccionario de modelos con nuestro diccionario de carga perezosa
modelos = ModelsDict()

def predecir_sensores(datos, modelo):
    """
    Convierte datos en DataFrame y aplica modelo para predecir 1 o -1.
    """
    df_nuevo = pd.DataFrame(datos, columns=["valor"])
    return modelo.predict(df_nuevo).tolist()

# Versión optimizada para predicción de un solo valor con caché
@lru_cache(maxsize=128)
def predecir_sensores_optimizado(modelo_key, valor_tuple):
    """
    Versión optimizada con caché para predecir valores (debe recibir valores como tuplas)
    """
    modelo = ModelRegistry.get_model(modelo_key)
    X = pd.DataFrame([valor_tuple], columns=["valor"])
    return modelo.predict(X)[0]

VENTANA_HORAS = 8  # horas

# ——— Configuración de umbrales por sensor ———
UMBRAL_SENSORES = {
    # Sensores existentes con nombres corregidos
    'prediccion_corriente': {
        "umbral_minimo": 54,  # 50% de 108
        "umbral_alerta": 86,   # 80% de 108
        "umbral_critica": 108,
    },
    'prediccion_presion_agua': {  # Corregido de prediccion_presion-agua
        "umbral_minimo": 25,  # 50% de 51
        "umbral_alerta": 41,  # 80% de 51
        "umbral_critica": 51,
    },
    'prediccion_temperatura_ambiental': {  # Corregido de prediccion_temperatura-ambiental
        "umbral_minimo": 1,   # 50% de 2
        "umbral_alerta": 2,  # 80% de 2
        "umbral_critica": 2,
    },
    
    # Nuevos sensores
    'prediccion_excentricidad_bomba': {
        "umbral_minimo": 0,   # 50% de 0
        "umbral_alerta": 0,   # 80% de 0
        "umbral_critica": 0,
    },
    'prediccion_flujo_descarga': {
        "umbral_minimo": 66,   # 50% de 132
        "umbral_alerta": 105,   # 80% de 132
        "umbral_critica": 132,
    },
    'prediccion_flujo_agua_domo_ap': {
        "umbral_minimo": 39,   # 50% de 78
        "umbral_alerta": 63,   # 80% de 78
        "umbral_critica": 78,
    },
    'prediccion_flujo_agua_domo_mp': {
        "umbral_minimo": 22,   # 50% de 45
        "umbral_alerta": 36,   # 80% de 45
        "umbral_critica": 45,
    },
    'prediccion_flujo_agua_recalentador': {
        "umbral_minimo": 45,   # 50% de 91
        "umbral_alerta": 73,   # 80% de 91
        "umbral_critica": 91,
    },
    'prediccion_flujo_agua_vapor_alta': {
        "umbral_minimo": 13,   # 50% de 26
        "umbral_alerta": 21,   # 80% de 26
        "umbral_critica": 26,
    },
    'prediccion_temperatura_agua_alim': {
        "umbral_minimo": 16,   # 50% de 32
        "umbral_alerta": 26,   # 80% de 32
        "umbral_critica": 32,
    },
    'prediccion_temperatura_estator': {
        "umbral_minimo": 36,   # 50% de 73
        "umbral_alerta": 58,   # 80% de 73
        "umbral_critica": 73,
    },
    'prediccion_vibracion_axial_empuje': {
        "umbral_minimo": 52,   # 50% de 104
        "umbral_alerta": 83,   # 80% de 104
        "umbral_critica": 104,
    },
    'prediccion_vibracion_x_descanso': {
        "umbral_minimo": 67,   # 50% de 133
        "umbral_alerta": 106,   # 80% de 133
        "umbral_critica": 133,
    },
    'prediccion_vibracion_y_descanso': {
        "umbral_minimo": 54,   # 50% de 107
        "umbral_alerta": 86,   # 80% de 107
        "umbral_critica": 107,
    },
    'prediccion_voltaje_barra': {
        "umbral_minimo": 18,  # 50% de 35
        "umbral_alerta": 28,  # 80% de 35
        "umbral_critica": 35,
    },
    'prediccion_temp-descanso-bomba-1a': {
        "umbral_minimo": 86,  # 50% de 171
        "umbral_alerta": 137,  # 80% de 171
        "umbral_critica": 171,
    },
    'prediccion_temp-empuje-bomba-1a': {
        "umbral_minimo": 55,  # 50% de 110
        "umbral_alerta": 88,  # 80% de 110
        "umbral_critica": 110,
    },
    'prediccion_temp-motor-bomba-1a': {
        "umbral_minimo": 13,   # 50% de 25
        "umbral_alerta": 20,  # 80% de 25
        "umbral_critica": 25,
    },
    'prediccion_vibracion-axial': {
        "umbral_minimo": 29,   # 50% de 58
        "umbral_alerta": 46,  # 80% de 58
        "umbral_critica": 58,
    },
    'prediccion_voltaje-barra': {
        "umbral_minimo": 18,   # 50% de 35
        "umbral_alerta": 28,  # 80% de 35
        "umbral_critica": 35,
    }
}

def predecir_sensores_np(modelo, valor):
    """
    Recibe el modelo y un único valor, devuelve la predicción (1 o -1) como entero.
    """
    X = np.array([[valor]])
    return int(modelo.predict(X)[0])


def contar_anomalias(db: Session, model_class, sensor_id: int) -> int:
    """
    Cuenta anomalías (clasificacion == -1) para un modelo de sensor específico
    en la ventana de tiempo.
    
    Nota: No filtramos por sensor_id específico porque queremos contar todas las
    anomalías del mismo tipo de sensor (misma tabla) en la ventana de tiempo.
    """
    try:
        ahora = datetime.now(timezone.utc)
        inicio = ahora - timedelta(hours=VENTANA_HORAS)
        count = db.query(func.count(model_class.id)) \
            .filter(model_class.clasificacion == -1) \
            .filter(model_class.tiempo_ejecucion.between(inicio, ahora)) \
            .scalar()
        return count if count is not None else 0
    except Exception as e:
        logger.error(f"Error al contar anomalías: {str(e)}")
        return 0  # En caso de error, devolvemos 0 para evitar interrumpir el flujo


# Información detallada de cada sensor para mensajes más descriptivos
SENSOR_INFO = {
    'prediccion_corriente': {
        'nombre': 'Corriente eléctrica',
        'descripcion': 'Medición de corriente eléctrica del sistema',
        'acciones': {
            'AVISO': 'Verificar niveles de carga y distribución eléctrica',
            'ALERTA': 'Revisar sobrecarga en sistemas eléctricos y reducir consumo si es posible',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla eléctrica. Activar protocolos de seguridad'
        }
    },
    'prediccion_salida-agua': {
        'nombre': 'Salida de agua',
        'descripcion': 'Flujo de salida de agua del sistema',
        'acciones': {
            'AVISO': 'Verificar sistema de bombeo y niveles de presión',
            'ALERTA': 'Revisar posibles obstrucciones y funcionamiento de válvulas',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema hidráulico'
        }
    },
    'prediccion_presion_agua': {
        'nombre': 'Presión de agua',
        'descripcion': 'Nivel de presión en el sistema hidráulico',
        'acciones': {
            'AVISO': 'Verificar sistema de regulación de presión',
            'ALERTA': 'Revisar posibles fugas o fallos en el sistema de presión',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrepresión en el sistema hidráulico'
        }
    },
    'prediccion_temperatura_ambiental': {
        'nombre': 'Temperatura ambiental',
        'descripcion': 'Temperatura ambiente en la zona de operación',
        'acciones': {
            'AVISO': 'Verificar sistemas de ventilación y refrigeración',
            'ALERTA': 'Activar sistemas adicionales de enfriamiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrecalentamiento de equipos'
        }
    },
    'prediccion_excentricidad_bomba': {
        'nombre': 'Excentricidad de bomba',
        'descripcion': 'Nivel de excentricidad en el eje de la bomba',
        'acciones': {
            'AVISO': 'Verificar alineación y balanceo',
            'ALERTA': 'Programar mantenimiento preventivo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño mecánico por desalineación'
        }
    },
    'prediccion_flujo_descarga': {
        'nombre': 'Flujo de descarga',
        'descripcion': 'Nivel de flujo en la descarga del sistema',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Revisar posibles obstrucciones o fallos',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de descarga'
        }
    },
    'prediccion_flujo_agua_domo_ap': {
        'nombre': 'Flujo de agua domo AP',
        'descripcion': 'Nivel de flujo de agua en el domo de alta presión',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Revisar sistema de control de flujo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de alta presión'
        }
    },
    'prediccion_flujo_agua_domo_mp': {
        'nombre': 'Flujo de agua domo MP',
        'descripcion': 'Nivel de flujo de agua en el domo de media presión',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Revisar sistema de control de flujo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de media presión'
        }
    },
    'prediccion_flujo_agua_recalentador': {
        'nombre': 'Flujo de agua recalentador',
        'descripcion': 'Nivel de flujo de agua en el sistema de recalentamiento',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Revisar sistema de recalentamiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de recalentamiento'
        }
    },
    'prediccion_flujo_agua_vapor_alta': {
        'nombre': 'Flujo de agua vapor alta',
        'descripcion': 'Nivel de flujo de agua/vapor en sistema de alta presión',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Revisar sistema de generación de vapor',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de vapor de alta presión'
        }
    },
    'prediccion_temperatura_agua_alim': {
        'nombre': 'Temperatura agua alimentación',
        'descripcion': 'Temperatura del agua de alimentación',
        'acciones': {
            'AVISO': 'Verificar sistema de precalentamiento',
            'ALERTA': 'Revisar sistema de control térmico',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño por temperatura inadecuada'
        }
    },
    'prediccion_temperatura_estator': {
        'nombre': 'Temperatura estator',
        'descripcion': 'Temperatura en el estator del generador',
        'acciones': {
            'AVISO': 'Verificar sistema de refrigeración',
            'ALERTA': 'Revisar cargas y sistema de enfriamiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en el estator por sobrecalentamiento'
        }
    },
    'prediccion_vibracion_axial_empuje': {
        'nombre': 'Vibración axial de empuje',
        'descripcion': 'Nivel de vibración axial en el sistema de empuje',
        'acciones': {
            'AVISO': 'Verificar alineación y balanceo',
            'ALERTA': 'Programar revisión mecánica',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en sistema de empuje'
        }
    },
    'prediccion_vibracion_x_descanso': {
        'nombre': 'Vibración X descanso',
        'descripcion': 'Nivel de vibración en eje X del descanso',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Programar revisión mecánica',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en descanso por vibraciones'
        }
    },
    'prediccion_vibracion_y_descanso': {
        'nombre': 'Vibración Y descanso',
        'descripcion': 'Nivel de vibración en eje Y del descanso',
        'acciones': {
            'AVISO': 'Verificar condiciones de operación',
            'ALERTA': 'Programar revisión mecánica',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en descanso por vibraciones'
        }
    },
    'prediccion_voltaje_barra': {
        'nombre': 'Voltaje de barra',
        'descripcion': 'Nivel de voltaje en las barras de distribución',
        'acciones': {
            'AVISO': 'Verificar estabilidad del suministro eléctrico',
            'ALERTA': 'Revisar regulación de voltaje y protecciones',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en equipos por fluctuaciones de voltaje'
        }
    },
    'prediccion_temp-descanso-bomba-1a': {
        'nombre': 'Temperatura de descanso Bomba 1A',
        'descripcion': 'Temperatura en rodamientos/descansos de la bomba 1A',
        'acciones': {
            'AVISO': 'Verificar sistema de lubricación y enfriamiento',
            'ALERTA': 'Revisar desgaste y programar mantenimiento preventivo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla mecánica en bomba 1A'
        }
    },
    'prediccion_temp-empuje-bomba-1a': {
        'nombre': 'Temperatura de empuje Bomba 1A',
        'descripcion': 'Temperatura en el cojinete de empuje de la bomba 1A',
        'acciones': {
            'AVISO': 'Verificar alineación y lubricación',
            'ALERTA': 'Revisar carga axial y sistema de enfriamiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de empuje'
        }
    },
    'prediccion_temp-motor-bomba-1a': {
        'nombre': 'Temperatura del motor Bomba 1A',
        'descripcion': 'Temperatura de operación del motor de la bomba 1A',
        'acciones': {
            'AVISO': 'Verificar ventilación y cargas de operación',
            'ALERTA': 'Revisar sistema eléctrico y refrigeración del motor',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla del motor por sobrecalentamiento'
        }
    },
    'prediccion_vibracion-axial': {
        'nombre': 'Vibración axial',
        'descripcion': 'Nivel de vibración axial en equipos rotativos',
        'acciones': {
            'AVISO': 'Verificar balanceo y alineación',
            'ALERTA': 'Programar revisión mecánica por posible desbalanceo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño estructural por vibraciones'
        }
    },
    'prediccion_voltaje-barra': {
        'nombre': 'Voltaje de barra',
        'descripcion': 'Nivel de voltaje en las barras de distribución',
        'acciones': {
            'AVISO': 'Verificar estabilidad del suministro eléctrico',
            'ALERTA': 'Revisar regulación de voltaje y protecciones',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en equipos por fluctuaciones de voltaje'
        }
    }
}

def determinar_alerta(conteo: int, umbral_sensor_key: str) -> dict:
    """
    Devuelve un diccionario con información completa de la alerta.
    """
    u = UMBRAL_SENSORES.get(umbral_sensor_key, {})
    sensor_info = SENSOR_INFO.get(umbral_sensor_key, {
        'nombre': umbral_sensor_key,
        'descripcion': 'Sensor de monitoreo',
        'acciones': {'AVISO': 'Verificar', 'ALERTA': 'Revisar', 'CRÍTICA': 'Intervenir'}
    })
    
    nivel = None
    porcentaje = 0
    
    if conteo >= u.get("umbral_critica", float('inf')):
        nivel = "CRÍTICA"
        porcentaje = 100
    elif conteo >= u.get("umbral_alerta", float('inf')):
        nivel = "ALERTA"
        porcentaje = 80
    elif conteo >= u.get("umbral_minimo", float('inf')):
        nivel = "AVISO"
        porcentaje = 50
    
    if nivel:
        return {
            "nivel": nivel,
            "nombre_sensor": sensor_info['nombre'],
            "descripcion_sensor": sensor_info['descripcion'],
            "accion_recomendada": sensor_info['acciones'].get(nivel, ""),
            "porcentaje_umbral": porcentaje,
            "conteo_anomalias": conteo
        }
    
    return None


def nivel_numerico(nivel: str) -> int:
    """Convierte el nivel textual a un valor numérico para comparaciones"""
    if nivel and ':' in nivel:
        nivel = nivel.split(':')[0].strip()
    return {"AVISO": 1, "ALERTA": 2, "CRÍTICA": 3}.get(nivel, 0)


def procesar(sensor: SensorInput, db: Session, modelo_key: str, umbral_key: str, model_class):
    """
    Lógica común de clasificación, conteo incremental/decremental y generación de alertas.
    """
    try:
        clase = predecir_sensores_np(modelos[modelo_key], sensor.valor)
        descripcion = "Normal" if clase == 1 else "Anomalía"

        # Intentar recuperar la lectura con manejo de excepciones
        try:
            lectura = db.query(model_class).get(sensor.id_sensor)
            if not lectura:
                logger.warning(f"Lectura no encontrada para sensor_id: {sensor.id_sensor}. Creando nuevo registro.")
                # Crear un nuevo registro si no existe
                lectura = model_class(
                    id=sensor.id_sensor,
                    tiempo_ejecucion=datetime.now(timezone.utc),
                    tiempo_sensor=sensor.tiempo_sensor,
                    valor_sensor=sensor.valor,
                    clasificacion=clase,
                    contador_anomalias=0
                )
                db.add(lectura)
                contador_anterior = 0
            else:
                # Guardar el contador anterior para poder decrementarlo si es necesario
                contador_anterior = lectura.contador_anomalias if hasattr(lectura, 'contador_anomalias') else 0
        except Exception as db_error:
            logger.error(f"Error al acceder a la base de datos: {str(db_error)}")
            # Crear un objeto temporal en memoria sin persistirlo
            lectura = model_class(
                id=sensor.id_sensor,
                tiempo_ejecucion=datetime.now(timezone.utc),
                tiempo_sensor=sensor.tiempo_sensor,
                valor_sensor=sensor.valor,
                clasificacion=clase,
                contador_anomalias=0
            )
            contador_anterior = 0

        # Actualizar la clasificación y tiempo de ejecución
        lectura.clasificacion = clase
        lectura.tiempo_ejecucion = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Error general en procesar(): {str(e)}")
        raise HTTPException(500, f"Error al procesar datos del sensor: {str(e)}")
        
    
    # Obtenemos el conteo de anomalías en la ventana de tiempo
    anomalias_ventana = contar_anomalias(db, model_class, sensor.id_sensor)
    
    # Ajustar contador según la clasificación
    if clase == 1:  # Si es normal
        # Decrementamos el contador previo en 1, pero nunca por debajo de 0
        nuevo_contador = max(0, contador_anterior - 1)
        lectura.contador_anomalias = nuevo_contador
        print(f"[{umbral_key}] Valor normal. Contador decrementado de {contador_anterior} a {nuevo_contador}")
    else:  # Si es anomalía
        # Para anomalías usamos el conteo real de la ventana de tiempo
        lectura.contador_anomalias = anomalias_ventana
        print(f"[{umbral_key}] Anomalía detectada. Anomalías en ventana de tiempo: {anomalias_ventana}")
    
    # Hacer commit para guardar cambios
    db.commit()
    
    # Por si acaso, recargar el objeto desde la BD para asegurar consistencia
    db.refresh(lectura)


    # Si es anomalía, evaluamos niveles de alerta en base al contador actualizado
    if clase == -1:
        # Utilizamos el contador actualizado que está en la variable lectura
        conteo = lectura.contador_anomalias
        alerta_info = determinar_alerta(conteo, umbral_key)
        if alerta_info:
            # Buscar alerta previa para comparar nivel
            prev = db.query(Alerta) \
                     .filter(Alerta.sensor_id == sensor.id_sensor, Alerta.tipo_sensor == umbral_key) \
                     .order_by(Alerta.id.desc()) \
                     .first()
            
            # Obtener nivel numérico de alerta previa y actual
            prev_n = nivel_numerico(prev.descripcion) if prev else 0
            curr_n = nivel_numerico(alerta_info["nivel"])
            
            # Solo generar nueva alerta si el nivel ha aumentado
            if curr_n > prev_n:
                # Construir mensaje descriptivo
                mensaje = f"{alerta_info['nivel']}: {alerta_info['nombre_sensor']} - {alerta_info['conteo_anomalias']} anomalías consecutivas ({alerta_info['porcentaje_umbral']}% del umbral crítico)\n"
                mensaje += f"Descripción: {alerta_info['descripcion_sensor']}\n"
                mensaje += f"Acción recomendada: {alerta_info['accion_recomendada']}"
                
                alerta = Alerta(
                    sensor_id=sensor.id_sensor,
                    tipo_sensor=umbral_key,
                    descripcion=mensaje,
                    contador_anomalias=conteo  # Guardar el contador actual en la alerta
                )
                db.add(alerta)
                db.commit()

    return {
        "id_sensor": sensor.id_sensor,
        "valor": sensor.valor,
        "prediccion": clase,
        "descripcion": descripcion,
        "contador_anomalias": lectura.contador_anomalias
    }


# ————— Rutas Post —————

@router_b.post("/prediccion_corriente")
async def predecir_corriente(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="corriente_motor", umbral_key="prediccion_corriente", model_class=SensorCorriente)

@router_b.post("/prediccion_excentricidad_bomba")
async def predecir_excentricidad_bomba(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="excentricidad_bomba", umbral_key="prediccion_excentricidad_bomba", model_class=SensorExcentricidadBomba)

@router_b.post("/prediccion_flujo_descarga")
async def predecir_flujo_descarga(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_descarga", umbral_key="prediccion_flujo_descarga", model_class=SensorFlujoDescarga)

@router_b.post("/prediccion_flujo_agua_domo_ap")
async def predecir_flujo_agua_domo_ap(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_ap", umbral_key="prediccion_flujo_agua_domo_ap", model_class=SensorFlujoAguaDomoAP)

@router_b.post("/prediccion_flujo_agua_domo_mp")
async def predecir_flujo_agua_domo_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_mp", umbral_key="prediccion_flujo_agua_domo_mp", model_class=SensorFlujoAguaDomoMP)

@router_b.post("/prediccion_flujo_agua_recalentador")
async def predecir_flujo_agua_recalentador(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_recalentador", umbral_key="prediccion_flujo_agua_recalentador", model_class=SensorFlujoAguaRecalentador)

@router_b.post("/prediccion_flujo_agua_vapor_alta")
async def predecir_flujo_agua_vapor_alta(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_vapor_alta", umbral_key="prediccion_flujo_agua_vapor_alta", model_class=SensorFlujoAguaVaporAlta)

@router_b.post("/prediccion_presion_agua")
async def predecir_presion_agua(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua", umbral_key="prediccion_presion_agua", model_class=SensorPresionAgua)

@router_b.post("/prediccion_temperatura_ambiental")
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_ambiental", umbral_key="prediccion_temperatura_ambiental", model_class=SensorTemperaturaAmbiental)

@router_b.post("/prediccion_temperatura_agua_alim")
async def predecir_temperatura_agua_alim(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_agua_alim", umbral_key="prediccion_temperatura_agua_alim", model_class=SensorTemperaturaAguaAlim)

@router_b.post("/prediccion_temperatura_estator")
async def predecir_temperatura_estator(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_estator", umbral_key="prediccion_temperatura_estator", model_class=SensorTemperaturaEstator)

@router_b.post("/prediccion_vibracion_axial_empuje")
async def predecir_vibracion_axial_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_axial_empuje", umbral_key="prediccion_vibracion_axial_empuje", model_class=SensorVibracionAxialEmpuje)

@router_b.post("/prediccion_vibracion_x_descanso")
async def predecir_vibracion_x_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_x_descanso", umbral_key="prediccion_vibracion_x_descanso", model_class=SensorVibracionXDescanso)

@router_b.post("/prediccion_vibracion_y_descanso")
async def predecir_vibracion_y_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_y_descanso", umbral_key="prediccion_vibracion_y_descanso", model_class=SensorVibracionYDescanso)

@router_b.post("/prediccion_voltaje_barra")
async def predecir_voltaje_barra(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="voltaje_barra", umbral_key="prediccion_voltaje_barra", model_class=SensorVoltajeBarra)




# Ruta para obtener datos de sensores de corriente
# — Helper genérica actualizada — 
async def _get_and_classify(
    db: Session,
    SensorModel,
    model_key,
    default_data,
    inicio: Optional[str] = None,
    termino: Optional[str] = None
):
    # Convertir strings a datetime si están presentes
    try:
        fecha_inicio = datetime.fromisoformat(inicio) if inicio else None
        fecha_termino = datetime.fromisoformat(termino) if termino else None
    except ValueError:
        return {"message": "Formato de fecha inválido. Use ISO 8601: YYYY-MM-DDTHH:MM:SS"}

    # Si se proporcionan fechas, filtrar por rango
    if fecha_inicio and fecha_termino:
        sensores = (
            db.query(SensorModel)
              .filter(SensorModel.tiempo_ejecucion >= fecha_inicio)
              .filter(SensorModel.tiempo_ejecucion <= fecha_termino)
              .order_by(SensorModel.tiempo_ejecucion.asc())
              .all()
        )
    else:
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


# ————— Rutas Post para Predicción de Bomba B —————

@router_b.post("/predecir-bomba-b", response_model=PrediccionBombaBOutput)
async def predecir_bomba_b(
    datos: PrediccionBombaBInput,
    db: Session = Depends(get_db)
):
    """
    Realiza una predicción utilizando el modelo Random Forest para la bomba B.
    
    Parámetros:
    - datos: Objeto con los valores de entrada para el modelo
    
    Retorna:
    - prediccion: Valor predicho por el modelo (probabilidad)
    - status: Estado de la operación
    """
    try:
        # Obtener el modelo usando ModelRegistry
        logger.info("Obteniendo modelo para predicción de bomba B")
        # La clave que usaremos es una especial, ya que este modelo no está en el diccionario normal
        # Así que tendremos que cargar el archivo directamente
        model_path = os.path.join(MODELS_DIR, "bm_randomforest_bomba_b.pkl")
        model = joblib.load(model_path)
        
        # Preparar los datos en el orden correcto para el modelo
        input_data = pd.DataFrame([{
            # Campos para la bomba B
            'Corriente Motor Bomba Agua Alimentacion 1B': datos.corriente_motor,
            'Excentricidad Bomba 1B': datos.excentricidad_bomba,
            'Flujo Descarga AP BAA AE01B': datos.flujo_descarga_ap,
            'Flujo de Agua Alimentación Domo AP Compensated': datos.flujo_agua_domo_ap,
            'Flujo de Agua Alimentación Domo MP Compensated': datos.flujo_agua_domo_mp,
            'Flujo de Agua Atemperación Recalentador': datos.flujo_agua_recalentador,
            'Flujo de Agua Atemperación Vapor Alta AP SH': datos.flujo_agua_vapor_alta,
            'Presión Agua Alimentación Economizador AP': datos.presion_agua_ap,
            'Temperatura Ambiental': datos.temperatura_ambiental,
            'Temperatura Agua Alimentación AP': datos.temperatura_agua_alim_ap,
            'Temperatura Estator Motor Bomba AA 1B': datos.temperatura_estator,
            'Vibración Axial Descanso Empuje Bomba 1B': datos.vibracion_axial,
            'Vibración X Descanso Interno Bomba 1B': datos.vibracion_x_descanso,
            'Vibración Y Descanso Interno Bomba 1B': datos.vibracion_y_descanso,
            'Voltaje Barra 6.6KV': datos.voltaje_barra
        }])
        
        logger.info(f"DataFrame de entrada preparado con shape: {input_data.shape}")
        
        # Realizar la predicción y obtener probabilidades
        prediccion = model.predict(input_data)
        # Obtener probabilidades para cada clase
        probabilidades = model.predict_proba(input_data)
        
        # Obtenemos siempre la probabilidad de falla (clase 1)
        # En modelos binarios predict_proba devuelve probabilidades para [clase 0, clase 1]
        prob_no_falla = float(probabilidades[0][0])  # Probabilidad de no falla (clase 0)
        prob_falla = 1 - prob_no_falla  # Probabilidad de falla (clase 1)
        
        # Convertir la probabilidad a porcentaje con dos decimales
        porcentaje_prediccion = round(prob_falla * 100, 2)
        
        logger.info(f"Predicción realizada: {prediccion[0]} con probabilidad de falla: {porcentaje_prediccion:.2f}%")
        
        # Obtener la hora y fecha actual
        ahora = datetime.now(timezone.utc)
        hora_actual = ahora.strftime("%H:%M:%S")
        dia_actual = ahora.strftime("%Y-%m-%d")
        
        # Guardar la predicción en la base de datos
        # Usamos el porcentaje de probabilidad como valor de predicción
        nueva_prediccion = PrediccionBombaB(
            valor_prediccion=porcentaje_prediccion,  # Guardamos el porcentaje de probabilidad
            hora_ejecucion=hora_actual,
            dia_ejecucion=dia_actual
        )
        
        db.add(nueva_prediccion)
        db.commit()
        
        # Retornar la predicción con el porcentaje de probabilidad
        return {
            "prediccion": porcentaje_prediccion,  # Devolvemos el porcentaje de probabilidad como predicción
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error al realizar la predicción para bomba B: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar la predicción: {str(e)}"
        )


# Rutas
@router_b.get("/predicciones-bomba-b", response_model=List[PrediccionBombaResponse])
async def obtener_predicciones_bomba(
    db: Session = Depends(get_db),
    limite: int = Query(40, description="Número de registros a devolver (máx 100)", le=100, ge=1)
):
    """
    Obtiene las últimas predicciones de la bomba.
    """
    try:
        # Consulta directa con ordenamiento y límite
        predicciones = db.query(PrediccionBombaB)\
                        .order_by(PrediccionBombaB.id.desc())\
                        .limit(limite)\
                        .all()
        predicciones = list(reversed(predicciones))  # Ahora los más antiguos primero
        logger.info(f"Registros encontrados: {len(predicciones)}")
        return predicciones
        
    except Exception as e:
        logger.error(f"Error al obtener predicciones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))










@router_b.get("/corriente")
async def get_sensores_corriente(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorCorriente, "corriente_motor", DEFAULT_SENSORES_CORRIENTE, inicio, termino)

@router_b.get("/excentricidad_bomba")
async def get_sensores_excentricidad_bomba(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorExcentricidadBomba, "excentricidad_bomba", DEFAULT_SENSORES_EXCENTRICIDAD, inicio, termino)

@router_b.get("/flujo_descarga")
async def get_sensores_flujo_descarga(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoDescarga, "flujo_descarga", DEFAULT_SENSORES_FLUJO_DESCARGA, inicio, termino)

@router_b.get("/flujo_agua_domo_ap")
async def get_sensores_flujo_agua_domo_ap(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoAP, "flujo_agua_domo_ap", DEFAULT_SENSORES_FLUJO_AGUA_DOMO_AP, inicio, termino)

@router_b.get("/flujo_agua_domo_mp")
async def get_sensores_flujo_agua_domo_mp(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoMP, "flujo_agua_domo_mp", DEFAULT_SENSORES_FLUJO_AGUA_DOMO_MP, inicio, termino)

@router_b.get("/flujo_agua_recalentador")
async def get_sensores_flujo_agua_recalentador(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaRecalentador, "flujo_agua_recalentador", DEFAULT_SENSORES_FLUJO_AGUA_RECALENTADOR, inicio, termino)

@router_b.get("/flujo_agua_vapor_alta")
async def get_sensores_flujo_agua_vapor_alta(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaVaporAlta, "flujo_agua_vapor_alta", DEFAULT_SENSORES_FLUJO_AGUA_VAPOR_ALTA, inicio, termino)

@router_b.get("/presion_agua")
async def get_sensores_presion_agua(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAgua, "presion_agua", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router_b.get("/temperatura_ambiental")
async def get_sensores_temperatura_ambiental(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaAmbiental, "temperatura_ambiental", DEFAULT_SENSORES_TEMPERATURA_AMBIENTAL, inicio, termino)

@router_b.get("/temperatura_agua_alim")
async def get_sensores_temperatura_agua_alim(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaAguaAlim, "temperatura_agua_alim", DEFAULT_SENSORES_TEMPERATURA_AGUA_ALIM, inicio, termino)

@router_b.get("/temperatura_estator")
async def get_sensores_temperatura_estator(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaEstator, "temperatura_estator", DEFAULT_SENSORES_TEMPERATURA_ESTATOR, inicio, termino)

@router_b.get("/vibracion_axial_empuje")
async def get_sensores_vibracion_axial_empuje(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionAxialEmpuje, "vibracion_axial_empuje", DEFAULT_SENSORES_VIBRACION_AXIAL_EMPUJE, inicio, termino)

@router_b.get("/vibracion_x_descanso")
async def get_sensores_vibracion_x_descanso(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionXDescanso, "vibracion_x_descanso", DEFAULT_SENSORES_VIBRACION_X_DESCANSO, inicio, termino)

@router_b.get("/vibracion_y_descanso")
async def get_sensores_vibracion_y_descanso(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionYDescanso, "vibracion_y_descanso", DEFAULT_SENSORES_VIBRACION_Y_DESCANSO, inicio, termino)

@router_b.get("/voltaje_barra")
async def get_sensores_voltaje_barra(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVoltajeBarra, "voltaje_barra", DEFAULT_SENSORES_VOLTAJE_BARRA, inicio, termino)




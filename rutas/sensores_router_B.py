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
    PrediccionBombaB, SensorVibracionXDescansoExternoB, SensorVibracionYDescansoExternoB,
    SensorPresionSuccionBAAB, SensorPosicionValvulaRecircB)
# Importar modelos de Bomba A para tablas compartidas (gm_influx inserta sin sufijo _b)
from modelos.modelos import (
    SensorFlujoAguaRecalentador as SensorFlujoAguaRecalentadorA,
    SensorFlujoAguaVaporAlta as SensorFlujoAguaVaporAltaA,
    SensorTemperatura_Ambiental as SensorTemperaturaAmbientalA,
    SensorVoltaje_barra as SensorVoltajeBarraA,
    SensorMw_brutos_generacion_gas as SensorMwBrutosGeneracionGas,
    SensorPresionAguaAlimentacionEconAP,
    SensorFlujoDeAguaAtempVaporAltaAP,
)

router_b = APIRouter(prefix="/sensores_b", tags=["Sensores Bomba B"])



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

# ==========================================
# CACHE PARA CONTAR_ANOMALIAS
# ==========================================
CACHE_ANOMALIAS = {}
CACHE_TIMEOUT = 30  # segundos - ajustar según necesidad

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del archivo actual
MODELS_DIR = os.path.join(BASE_DIR, "..", "modelos_prediccion_b")  # Ruta absoluta a la carpeta de modelos
MODELS_DIR_FALLBACK = os.path.join(BASE_DIR, "..", "modelos_prediccion")  # Fallback: modelos de Bomba A

# Mapa de claves de modelo a rutas de archivo
MODEL_PATHS = {
    "corriente_motor": "Corriente_MTR_BBA_Agua_Alim_1B_B.pkl",
    "excentricidad_bomba": "Excentricidad_Bomba_1B_B.pkl",
    "flujo_descarga": "Flujo_Descarga_AP_BAA_AE01B_B.pkl",
    "flujo_agua_domo_ap": "Flujo_de_Agua_Alimentacion_Domo_AP_Compensated_18B.pkl",  # Compartido con Bomba A
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

    # Modelos nuevos agregados
    "temp_descanso_bomba": "Temperatura_Descanso_Interno_Bomba_1B_B.pkl",
    "temp_descanso_empuje": "Temperatura_Descanso_Interno_Empuje_Bomba_1B_A_B.pkl",
    "temp_descanso_motor": "Temperatura_Descanso_Interno_MTR_Bomba_1B_G_B.pkl",

    # Señales faltantes Bomba B (2025-02-23) - Usando modelos de Bomba A como fallback
    "vibracion_x_descanso_externo": "Vibracion_X_Descanso_Externo_Bomba_1A_A.pkl",  # Modelo Bomba A
    "vibracion_y_descanso_externo": "Vibracion_Y_Descanso_Externo_Bomba_1A_B.pkl",  # Modelo Bomba A
    "presion_succion_baa": "Presion_succion_BAA_AE01A.pkl",  # Modelo Bomba A
    "posicion_valvula_recirc": "Posicion_v_lvula_recirc_BAA_AE01A.pkl",  # Modelo Bomba A
    "mw_brutos_generacion_gas": "Medicion_de_Pot_Bruta_Planta_B.pkl",
    "presion_agua_econ_ap": "Presi_n_Agua_Alimentacion_Econ._AP.pkl",
    # Tabla compartida Bomba A - nueva ruta en Bomba B
    "flujo_atemp_vapor_alta_ap": "Flujo_de_Agua_Atemp_Vapor_Alta_AP_SH.pkl",  # Modelo Bomba A
    "flujo_domo_ap_compensated": "Flujo_de_Agua_Alimentacion_Domo_AP_Compensated_18B.pkl",  # Misma tabla flujo_agua_domo_ap_b
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

        # Si el modelo está definido como None, retornar None
        if MODEL_PATHS[model_key] is None:
            logger.warning(f"Modelo {model_key} no disponible (definido como None)")
            return None

        # Cargar el modelo si aún no está en memoria
        if model_key not in cls._models:
            start_time = time.time()
            logger.info(f"Cargando modelo {model_key}...")

            model_path = os.path.join(MODELS_DIR, MODEL_PATHS[model_key])

            # Si no existe en modelos_prediccion_b, buscar en modelos_prediccion (fallback Bomba A)
            if not os.path.exists(model_path):
                fallback_path = os.path.join(MODELS_DIR_FALLBACK, MODEL_PATHS[model_key])
                if os.path.exists(fallback_path):
                    logger.info(f"Modelo {model_key} no encontrado en Bomba B, usando fallback de Bomba A: {fallback_path}")
                    model_path = fallback_path
                else:
                    logger.error(f"Archivo de modelo no encontrado en ninguna carpeta: {MODEL_PATHS[model_key]}")
                    return None

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
    return modelo.predict(df_nuevo.values).tolist()

# Versión optimizada para predicción de un solo valor con caché
@lru_cache(maxsize=128)
def predecir_sensores_optimizado(modelo_key, valor_tuple):
    """
    Versión optimizada con caché para predecir valores (debe recibir valores como tuplas)
    """
    modelo = ModelRegistry.get_model(modelo_key)
    X = pd.DataFrame([valor_tuple], columns=["valor"])
    return modelo.predict(X.values)[0]

VENTANA_HORAS = 8  # horas

# ——— Configuracion de umbrales por sensor ———
# Umbrales calculados basados en análisis de datos históricos Bomba B
# Fórmula: minimo ≈ 50% crítica, alerta ≈ 80% crítica
UMBRAL_SENSORES = {
    # === Sensores principales Bomba B ===
    'prediccion_corriente': {
        "umbral_minimo": 54,    # 50% de 108
        "umbral_alerta": 86,    # 80% de 108
        "umbral_critica": 108,  # Corriente MTR BBA Agua Alim 1B
    },
    'prediccion_presion_agua': {
        "umbral_minimo": 25,    # 50% de 51
        "umbral_alerta": 41,    # 80% de 51
        "umbral_critica": 51,   # Presión Agua Alimentación Econ. AP
    },
    'prediccion_temperatura_ambiental': {
        "umbral_minimo": 14,    # Similar a Bomba A
        "umbral_alerta": 22,
        "umbral_critica": 28,
    },
    'prediccion_excentricidad_bomba': {
        "umbral_minimo": 5,     # Valor mínimo (original era 0)
        "umbral_alerta": 8,
        "umbral_critica": 10,
    },
    'prediccion_flujo_descarga': {
        "umbral_minimo": 66,    # 50% de 132
        "umbral_alerta": 106,   # 80% de 132
        "umbral_critica": 132,  # Flujo Descarga AP BAA AE01B
    },
    'prediccion_flujo_agua_domo_ap': {
        "umbral_minimo": 39,    # 50% de 78
        "umbral_alerta": 62,    # 80% de 78
        "umbral_critica": 78,   # Flujo de Agua Alimentación Domo AP Compensated
    },
    'prediccion_flujo_domo_ap_compensated': {
        "umbral_minimo": 39,
        "umbral_alerta": 62,
        "umbral_critica": 78,
    },
    'prediccion_flujo_agua_domo_mp': {
        "umbral_minimo": 22,    # 50% de 45
        "umbral_alerta": 36,    # 80% de 45
        "umbral_critica": 45,   # Flujo de Agua Alimentación Domo MP Compensated
    },
    'prediccion_flujo_agua_recalentador': {
        "umbral_minimo": 45,    # 50% de 91
        "umbral_alerta": 73,    # 80% de 91
        "umbral_critica": 91,   # Flujo de Agua/Atemp Recale Calient RH
    },
    'prediccion_flujo_agua_vapor_alta': {
        "umbral_minimo": 13,    # 50% de 26
        "umbral_alerta": 21,    # 80% de 26
        "umbral_critica": 26,   # Flujo de Agua/Atemp Vapor Alta AP SH
    },
    'prediccion_temperatura_agua_alim': {
        "umbral_minimo": 16,    # 50% de 32
        "umbral_alerta": 26,    # 80% de 32
        "umbral_critica": 32,   # Temperatura Agua Alim AP
    },
    'prediccion_temperatura_estator': {
        "umbral_minimo": 36,    # 50% de 73
        "umbral_alerta": 58,    # 80% de 73
        "umbral_critica": 73,   # Temperatura Estator MTR BBA AA 1B A
    },
    'prediccion_vibracion_axial_empuje': {
        "umbral_minimo": 52,    # 50% de 104
        "umbral_alerta": 83,    # 80% de 104
        "umbral_critica": 104,  # Vibración Axial Descanso Emp Bomba 1B
    },
    'prediccion_vibracion_x_descanso': {
        "umbral_minimo": 67,    # 50% de 133
        "umbral_alerta": 106,   # 80% de 133
        "umbral_critica": 133,  # Vibración X Descanso Interno Bomba 1B
    },
    'prediccion_vibracion_y_descanso': {
        "umbral_minimo": 54,    # 50% de 107
        "umbral_alerta": 86,    # 80% de 107
        "umbral_critica": 107,  # Vibración Y Descanso Interno Bomba 1B
    },
    'prediccion_voltaje_barra': {
        "umbral_minimo": 18,    # 50% de 35
        "umbral_alerta": 28,    # 80% de 35
        "umbral_critica": 35,   # Voltaje Barra 6,6KV
    },
    # === Aliases para compatibilidad ===
    'prediccion_temp-descanso-bomba-1a': {
        "umbral_minimo": 86,
        "umbral_alerta": 137,
        "umbral_critica": 171,
    },
    'prediccion_temp-empuje-bomba-1a': {
        "umbral_minimo": 55,
        "umbral_alerta": 88,
        "umbral_critica": 110,
    },
    'prediccion_temp-motor-bomba-1a': {
        "umbral_minimo": 13,
        "umbral_alerta": 20,
        "umbral_critica": 25,
    },
    'prediccion_vibracion-axial': {
        "umbral_minimo": 52,
        "umbral_alerta": 83,
        "umbral_critica": 104,
    },
    'prediccion_voltaje-barra': {
        "umbral_minimo": 18,
        "umbral_alerta": 28,
        "umbral_critica": 35,
    },
    # === Temperaturas descanso Bomba B ===
    'prediccion_temp_descanso_bomba': {
        "umbral_minimo": 86,
        "umbral_alerta": 137,
        "umbral_critica": 171,
    },
    'prediccion_temp_descanso_empuje': {
        "umbral_minimo": 55,
        "umbral_alerta": 88,
        "umbral_critica": 110,
    },
    'prediccion_temp_descanso_motor': {
        "umbral_minimo": 13,
        "umbral_alerta": 20,
        "umbral_critica": 25,
    },
    # === Vibraciones externas ===
    'prediccion_vibracion_x_descanso_externo': {
        "umbral_minimo": 60,
        "umbral_alerta": 96,
        "umbral_critica": 120,
    },
    'prediccion_vibracion_y_descanso_externo': {
        "umbral_minimo": 50,
        "umbral_alerta": 80,
        "umbral_critica": 100,
    },
    # === Nuevos sensores ===
    'prediccion_presion_succion_baa': {
        "umbral_minimo": 25,
        "umbral_alerta": 40,
        "umbral_critica": 50,
    },
    'prediccion_posicion_valvula_recirc': {
        "umbral_minimo": 25,
        "umbral_alerta": 40,
        "umbral_critica": 50,
    },
    'prediccion_mw_brutos_generacion_gas': {
        "umbral_minimo": 56,
        "umbral_alerta": 90,
        "umbral_critica": 112,
    },
    'prediccion_presion_agua_econ_ap': {
        "umbral_minimo": 25,
        "umbral_alerta": 41,
        "umbral_critica": 51,
    },
    'prediccion_flujo_atemp_vapor_alta_ap': {
        "umbral_minimo": 13,    # Igual a flujo vapor alta AP Bomba A
        "umbral_alerta": 21,
        "umbral_critica": 26,
    },
}

def predecir_sensores_np(modelo, valor):
    """
    Recibe el modelo y un único valor, devuelve la predicción (1 o -1) como entero.
    """
    X = np.array([[valor]])
    return int(modelo.predict(X)[0])


def contar_anomalias_cached(db: Session, model_class, tiempo_base: datetime) -> dict:
    """
    Versión con cache de contar_anomalias().
    Reduce queries a BD cuando múltiples sensores llegan en poco tiempo.
    """
    # Clave de cache: nombre de tabla + hora redondeada al minuto
    cache_key = (
        model_class.__tablename__,
        tiempo_base.replace(second=0, microsecond=0)
    )

    # Verificar si está en cache y es reciente
    if cache_key in CACHE_ANOMALIAS:
        cached_data, timestamp = CACHE_ANOMALIAS[cache_key]
        elapsed = (datetime.now() - timestamp).total_seconds()

        if elapsed < CACHE_TIMEOUT:
            logger.info(f"✅ Cache HIT para {model_class.__tablename__} (edad: {elapsed:.1f}s)")
            return cached_data

    # Cache miss - calcular
    logger.info(f"❌ Cache MISS para {model_class.__tablename__}, consultando BD...")
    resultado = contar_anomalias(db, model_class, tiempo_base)

    # Guardar en cache
    CACHE_ANOMALIAS[cache_key] = (resultado, datetime.now())

    # Limpieza de cache antiguo (mantener solo últimos 100)
    if len(CACHE_ANOMALIAS) > 100:
        # Ordenar por timestamp y eliminar los 50 más antiguos
        items_ordenados = sorted(CACHE_ANOMALIAS.items(), key=lambda x: x[1][1])
        for key, _ in items_ordenados[:50]:
            del CACHE_ANOMALIAS[key]
        logger.info(f"🧹 Cache limpiado: {len(CACHE_ANOMALIAS)} entradas restantes")

    return resultado


def contar_anomalias(db: Session, model_class, tiempo_base: datetime) -> dict:
    """
    Cuenta anomalías (clasificacion == -1) para un modelo de sensor específico.
    Usa COUNT directo para el conteo (robusto) y análisis temporal separado (opcional).
    """
    inicio = tiempo_base - timedelta(hours=VENTANA_HORAS)

    # ── 1. COUNT robusto: nunca puede fallar por análisis temporal ──
    try:
        conteo = db.query(func.count(model_class.id)).filter(
            model_class.clasificacion == -1,
            model_class.tiempo_ejecucion.isnot(None),
            model_class.tiempo_ejecucion >= inicio,
            model_class.tiempo_ejecucion <= tiempo_base
        ).scalar() or 0
        logger.info(f"[CONTAR_ANOMALIAS_B] {model_class.__tablename__}: {conteo} anomalías en ventana")
    except Exception as e:
        logger.error(f"[CONTAR_ANOMALIAS_B] Error en COUNT: {e}")
        conteo = 0

    if conteo == 0:
        return {
            'conteo': 0,
            'primera_anomalia': None,
            'ultima_anomalia': None,
            'duracion_total': 0,
            'anomalias_consecutivas': 0,
            'frecuencia_por_hora': 0.0,
            'distribucion_temporal': {},
            'patron_consecutivo': False
        }

    # ── 2. Análisis temporal (opcional, no afecta el conteo) ──
    primera_anomalia = None
    ultima_anomalia = None
    duracion_total = 0
    anomalias_consecutivas = 0
    patron_consecutivo = False
    distribucion_temporal = {}
    frecuencia_por_hora = round(conteo / VENTANA_HORAS, 2) if VENTANA_HORAS > 0 else 0.0

    try:
        filas = db.query(model_class.tiempo_ejecucion, model_class.valor_sensor).filter(
            model_class.clasificacion == -1,
            model_class.tiempo_ejecucion.isnot(None),
            model_class.tiempo_ejecucion >= inicio,
            model_class.tiempo_ejecucion <= tiempo_base
        ).order_by(model_class.tiempo_ejecucion).all()

        anomalias = [{'tiempo_ejecucion': f.tiempo_ejecucion, 'valor_sensor': f.valor_sensor}
                     for f in filas if f.tiempo_ejecucion is not None]
        timestamps_validos = [a['tiempo_ejecucion'] for a in anomalias]

        if timestamps_validos:
            primera_anomalia = min(timestamps_validos)
            ultima_anomalia = max(timestamps_validos)
            duracion_total = (ultima_anomalia - primera_anomalia).total_seconds()
            anomalias_consecutivas = calcular_anomalias_consecutivas(anomalias)
            patron_consecutivo = anomalias_consecutivas > 3
            distribucion_temporal = crear_distribucion_temporal(anomalias)
    except Exception as e:
        logger.warning(f"[CONTAR_ANOMALIAS_B] Error en análisis temporal (conteo={conteo} sigue siendo válido): {e}")

    return {
        'conteo': conteo,
        'primera_anomalia': primera_anomalia,
        'ultima_anomalia': ultima_anomalia,
        'duracion_total': duracion_total,
        'anomalias_consecutivas': anomalias_consecutivas,
        'frecuencia_por_hora': frecuencia_por_hora,
        'distribucion_temporal': distribucion_temporal,
        'patron_consecutivo': patron_consecutivo
    }


# Funciones auxiliares para análisis temporal
def calcular_anomalias_consecutivas(anomalias):
    """Calcula el número máximo de anomalías consecutivas"""
    if not anomalias:
        return 0
    
    max_consecutivas = 0
    consecutivas_actuales = 0
    
    for i in range(len(anomalias) - 1):
        tiempo_actual = anomalias[i]['tiempo_ejecucion']
        tiempo_siguiente = anomalias[i + 1]['tiempo_ejecucion']
        
        # Convertir a datetime si son strings
        if isinstance(tiempo_actual, str):
            tiempo_actual = datetime.fromisoformat(tiempo_actual.replace('Z', '+00:00'))
        if isinstance(tiempo_siguiente, str):
            tiempo_siguiente = datetime.fromisoformat(tiempo_siguiente.replace('Z', '+00:00'))
        
        # Si la diferencia es menor a 10 minutos, consideramos consecutivas
        diferencia = abs((tiempo_siguiente - tiempo_actual).total_seconds())
        if diferencia <= 600:  # 10 minutos
            consecutivas_actuales += 1
        else:
            max_consecutivas = max(max_consecutivas, consecutivas_actuales)
            consecutivas_actuales = 0
    
    return max(max_consecutivas, consecutivas_actuales)

def crear_distribucion_temporal(anomalias):
    """Crea una distribución temporal de las anomalías por hora"""
    distribucion = {}
    
    for anomalia in anomalias:
        tiempo = anomalia['tiempo_ejecucion']
        if isinstance(tiempo, str):
            tiempo = datetime.fromisoformat(tiempo.replace('Z', '+00:00'))
        
        hora = tiempo.hour
        distribucion[hora] = distribucion.get(hora, 0) + 1
    
    return distribucion

def formatear_duracion(duracion_segundos):
    """Formatea la duración en un formato legible"""
    if duracion_segundos < 60:
        return f"{int(duracion_segundos)} segundos"
    elif duracion_segundos < 3600:
        minutos = int(duracion_segundos / 60)
        return f"{minutos} minutos"
    else:
        horas = int(duracion_segundos / 3600)
        minutos = int((duracion_segundos % 3600) / 60)
        return f"{horas}h {minutos}m"


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
    'prediccion_flujo_domo_ap_compensated': {
        'nombre': 'Flujo Domo AP Compensado',
        'descripcion': 'Flujo de agua alimentación domo AP compensado',
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

def _crear_mensaje_temporal(info_anomalias: dict, nivel: str) -> str:
    """
    Crea un mensaje descriptivo basado en la información temporal de las anomalías.
    """
    if info_anomalias['conteo'] == 0:
        return ""
    
    mensaje_partes = []
    
    # Información básica
    if info_anomalias['conteo'] == 1:
        mensaje_partes.append("Se detectó 1 anomalía")
    else:
        mensaje_partes.append(f"Se detectaron {info_anomalias['conteo']} anomalías")
    
    # Información temporal
    if info_anomalias['primera_anomalia'] and info_anomalias['ultima_anomalia']:
        primera = info_anomalias['primera_anomalia'].strftime("%H:%M")
        ultima = info_anomalias['ultima_anomalia'].strftime("%H:%M")
        
        if info_anomalias['conteo'] == 1:
            mensaje_partes.append(f"a las {primera}")
        else:
            mensaje_partes.append(f"entre {primera} y {ultima}")
    
    # Información de consecutividad
    if info_anomalias['anomalias_consecutivas'] > 1:
        mensaje_partes.append(f"con {info_anomalias['anomalias_consecutivas']} anomalías consecutivas")
    
    # Frecuencia
    if info_anomalias['frecuencia_por_hora'] > 0:
        mensaje_partes.append(f"(frecuencia: {info_anomalias['frecuencia_por_hora']}/hora)")
    
    # Patrón crítico
    if nivel == "CRÍTICA" and info_anomalias['patron_consecutivo']:
        mensaje_partes.append("- PATRÓN CRÍTICO DETECTADO")
    
    return ". ".join(mensaje_partes) + "."


def determinar_alerta(info_anomalias: dict, umbral_sensor_key: str, bomba_id: str = "B") -> dict:
    """
    Determina el nivel de alerta basado en la información de anomalías y los umbrales configurados.
    
    Args:
        info_anomalias: Diccionario con información detallada de anomalías
        umbral_sensor_key: Clave del sensor en UMBRAL_SENSORES
        bomba_id: Identificador de la bomba (A o B)
        
    Returns:
        dict: Información completa de la alerta o None si no hay alerta
    """
    conteo = info_anomalias.get('conteo', 0)
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
        # Agregar identificación de bomba al nombre del sensor
        nombre_sensor_con_bomba = f"{sensor_info['nombre']} - BOMBA {bomba_id}"

        # Descripción simplificada (sin información técnica de anomalías)
        descripcion_simplificada = sensor_info['descripcion']

        return {
            "nivel": nivel,
            "nombre_sensor": nombre_sensor_con_bomba,
            "descripcion_sensor": descripcion_simplificada,
            "accion_recomendada": sensor_info['acciones'].get(nivel, ""),
            "porcentaje_umbral": porcentaje,
            "conteo_anomalias": conteo,
            "bomba_id": bomba_id,
            # Información temporal detallada
            "timestamp_alerta": datetime.now(),
            "primera_anomalia": info_anomalias.get('primera_anomalia'),
            "ultima_anomalia": info_anomalias.get('ultima_anomalia'),
            "duracion_total": formatear_duracion(info_anomalias.get('duracion_total', 0)),
            "anomalias_consecutivas": info_anomalias.get('anomalias_consecutivas', 0),
            "frecuencia_por_hora": info_anomalias.get('frecuencia_por_hora', 0.0),
            "distribucion_temporal": info_anomalias.get('distribucion_temporal', {}),
            "patron_consecutivo": info_anomalias.get('patron_consecutivo', False)
        }
    
    return None


def nivel_numerico(nivel: str) -> int:
    """Convierte el nivel textual a un valor numérico para comparaciones"""
    if nivel and ':' in nivel:
        nivel = nivel.split(':')[0].strip()
    return {"AVISO": 1, "ALERTA": 2, "CRÍTICA": 3}.get(nivel, 0)


def procesar(sensor: SensorInput, db: Session, modelo_key: str, umbral_key: str, model_class):
    """
    Lógica de clasificación, conteo de anomalías en ventana 8h y generación de alertas.

    Flujo:
    1. Clasificar valor con modelo ML
    2. Contar anomalías existentes en ventana de 8 horas
    3. UPDATE atómico: clasificacion + contador_anomalias
    4. Evaluar alertas según umbrales
    """
    try:
        # Verificar si el modelo está disponible
        modelo = modelos.get(modelo_key)
        if modelo is None:
            logger.warning(f"Modelo {modelo_key} no disponible. Datos guardados sin clasificación.")
            return {
                "clasificacion": None,
                "descripcion": "Sin modelo ML disponible",
                "mensaje": f"Sensor {model_class.__tablename__}: datos recibidos pero modelo {modelo_key} no disponible",
                "valor": sensor.valor,
                "id_sensor": sensor.id_sensor
            }

        # ── PASO 1: Clasificar el valor del sensor ──
        clase = predecir_sensores_np(modelo, sensor.valor)
        descripcion = "Normal" if clase == 1 else "Anomalía"
        tiempo_actual = datetime.now()

        # ── PASO 2: Contar anomalías en ventana de 8 horas ──
        tiempo_inicio = tiempo_actual - timedelta(hours=VENTANA_HORAS)
        try:
            conteo_ventana = db.query(func.count(model_class.id)).filter(
                model_class.clasificacion == -1,
                model_class.tiempo_ejecucion.isnot(None),
                model_class.tiempo_ejecucion >= tiempo_inicio,
                model_class.tiempo_ejecucion <= tiempo_actual
            ).scalar() or 0
        except Exception as e:
            logger.error(f"Error en COUNT ventana 8h: {e}")
            conteo_ventana = 0

        # Si el registro actual es anomalía, sumar 1 al conteo (aún no está clasificado en BD)
        if clase == -1:
            conteo_ventana += 1

        logger.info(f"[{umbral_key}] ID={sensor.id_sensor}: clase={clase}, conteo_ventana_8h={conteo_ventana}")

        # ── PASO 3: UPDATE ATÓMICO - clasificación + contador en UNA operación ──
        if sensor.id_sensor:
            # Verificar que el registro existe
            existe = db.query(model_class.id).filter(
                model_class.id == sensor.id_sensor
            ).first()
            if not existe:
                raise HTTPException(404, f"Registro con id {sensor.id_sensor} no encontrado")

            rows_updated = db.query(model_class).filter(
                model_class.id == sensor.id_sensor
            ).update({
                'clasificacion': clase,
                'contador_anomalias': conteo_ventana
            }, synchronize_session=False)

            if rows_updated == 0:
                raise HTTPException(404, f"No se pudo actualizar registro {sensor.id_sensor}")

            db.commit()
            logger.info(f"UPDATE OK ID {sensor.id_sensor}: clasificacion={clase}, contador={conteo_ventana}")

            # Cargar el objeto para uso posterior
            lectura = db.query(model_class).filter(
                model_class.id == sensor.id_sensor
            ).first()

        else:
            # Comportamiento sin id_sensor: buscar o crear registro
            lectura = db.query(model_class).filter(
                model_class.tiempo_sensor == sensor.tiempo_sensor
            ).first()

            if lectura:
                lectura.clasificacion = clase
                lectura.valor_sensor = sensor.valor
                lectura.tiempo_ejecucion = sensor.tiempo_sensor
                lectura.tiempo_sensor = sensor.tiempo_sensor
                lectura.contador_anomalias = conteo_ventana
            else:
                lectura = model_class(
                    tiempo_ejecucion=sensor.tiempo_sensor,
                    tiempo_sensor=sensor.tiempo_sensor,
                    valor_sensor=sensor.valor,
                    clasificacion=clase,
                    contador_anomalias=conteo_ventana
                )
                db.add(lectura)

            db.commit()
            db.refresh(lectura)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error general en procesar(): {str(e)}")
        db.rollback()
        raise HTTPException(500, f"Error al procesar datos del sensor: {str(e)}")

    # ── PASO 4: Info de anomalías para alertas ──
    try:
        tiempo_base = lectura.tiempo_ejecucion if lectura.tiempo_ejecucion is not None else tiempo_actual
        info_anomalias = contar_anomalias_cached(db, model_class, tiempo_base)
    except Exception as e:
        logger.warning(f"Error en contar_anomalias_cached: {e}")
        db.rollback()
        info_anomalias = {'conteo': conteo_ventana, 'primera_anomalia': None, 'ultima_anomalia': None,
                          'anomalias_consecutivas': 0, 'frecuencia_por_hora': 0, 'patron_consecutivo': False,
                          'distribucion_temporal': {}, 'duracion_total': 0}

    # ── PASO 5: Evaluar alertas según conteo_ventana vs umbrales ──
    if clase == -1 and conteo_ventana > 0:
        info_para_alerta = dict(info_anomalias)
        info_para_alerta['conteo'] = conteo_ventana
        alerta_info = determinar_alerta(info_para_alerta, umbral_key, "B")
        if alerta_info:
            prev = db.query(Alerta) \
                     .filter(Alerta.tipo_sensor == umbral_key) \
                     .order_by(Alerta.id.desc()) \
                     .first()

            prev_n = nivel_numerico(prev.descripcion) if prev else 0
            curr_n = nivel_numerico(alerta_info["nivel"])

            es_nuevo_ciclo_critica = (curr_n == 3 and prev_n == 3)
            debe_crear_alerta = (curr_n > prev_n) or es_nuevo_ciclo_critica

            if debe_crear_alerta:
                inicio_anomalia = info_anomalias.get('primera_anomalia')
                fin_anomalia = info_anomalias.get('ultima_anomalia')
                if inicio_anomalia and fin_anomalia:
                    intervalo = f"{inicio_anomalia.strftime('%Y-%m-%d %H:%M')} - {fin_anomalia.strftime('%Y-%m-%d %H:%M')}"
                else:
                    intervalo = "No disponible"

                mensaje = f"{alerta_info['nivel']}: {alerta_info['nombre_sensor']}\n"
                mensaje += f"Bomba: B\n"
                mensaje += f"Descripción: {alerta_info['descripcion_sensor']}\n"
                mensaje += f"Intervalo: {intervalo}\n"
                mensaje += f"Acción recomendada: {alerta_info['accion_recomendada']}"

                alerta = Alerta(
                    sensor_id=lectura.id,
                    tipo_sensor=umbral_key,
                    descripcion=mensaje,
                    timestamp=sensor.tiempo_sensor,
                    contador_anomalias=conteo_ventana,
                    timestamp_inicio_anomalia=info_anomalias.get('primera_anomalia'),
                    timestamp_fin_anomalia=info_anomalias.get('ultima_anomalia')
                )
                db.add(alerta)
                db.commit()
                logger.info(f"[{umbral_key}] Nueva alerta {alerta_info['nivel']} (conteo={conteo_ventana})")

    return {
        "id_registro": lectura.id,
        "valor": sensor.valor,
        "prediccion": clase,
        "descripcion": descripcion,
        "contador_anomalias": conteo_ventana
    }


# ————— Rutas Post —————

@router_b.post(
    "/prediccion_corriente",
    summary="Detectar anomalía - Corriente motor B",
    description="""
Analiza el valor de corriente eléctrica del motor de la Bomba B para detectar anomalías.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de corriente (Amperios)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_corriente(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="corriente_motor", umbral_key="prediccion_corriente", model_class=SensorCorriente)

@router_b.post(
    "/prediccion_excentricidad_bomba",
    summary="Detectar anomalía - Excentricidad bomba B",
    description="""
Analiza la excentricidad del rotor de la Bomba 1B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de excentricidad (mm o mils)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Valores elevados indican posible desalineación o desgaste en cojinetes.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_excentricidad_bomba(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="excentricidad_bomba", umbral_key="prediccion_excentricidad_bomba", model_class=SensorExcentricidadBomba)

@router_b.post(
    "/prediccion_flujo_descarga",
    summary="Detectar anomalía - Flujo descarga AP",
    description="""
Analiza el flujo de descarga de alta presión de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Variaciones indican problemas en el sistema de bombeo.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_descarga(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_descarga", umbral_key="prediccion_flujo_descarga", model_class=SensorFlujoDescarga)

@router_b.post(
    "/prediccion_flujo_agua_domo_ap",
    summary="Detectar anomalía - Flujo agua domo AP",
    description="""
Analiza el flujo de agua de alimentación al domo de alta presión de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_domo_ap(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_ap", umbral_key="prediccion_flujo_agua_domo_ap", model_class=SensorFlujoAguaDomoAP)

@router_b.post(
    "/prediccion_flujo_domo_ap_compensated",
    summary="Detectar anomalía - Flujo domo AP compensado",
    description="""
Analiza el flujo de agua alimentación domo AP compensado de la Bomba B.
Usa la misma tabla flujo_agua_domo_ap_b.
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_domo_ap_compensated(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_domo_ap_compensated", umbral_key="prediccion_flujo_domo_ap_compensated", model_class=SensorFlujoAguaDomoAP)

@router_b.post(
    "/prediccion_flujo_agua_domo_mp",
    summary="Detectar anomalía - Flujo agua domo MP",
    description="""
Analiza el flujo de agua de alimentación al domo de media presión de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_domo_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_mp", umbral_key="prediccion_flujo_agua_domo_mp", model_class=SensorFlujoAguaDomoMP)

@router_b.post(
    "/prediccion_flujo_agua_recalentador",
    summary="Detectar anomalía - Flujo agua recalentador",
    description="""
Analiza el flujo de agua para atemperación del recalentador en la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_recalentador(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_recalentador", umbral_key="prediccion_flujo_agua_recalentador", model_class=SensorFlujoAguaRecalentadorA)

@router_b.post(
    "/prediccion_flujo_agua_vapor_alta",
    summary="Detectar anomalía - Flujo agua vapor alta",
    description="""
Analiza el flujo de agua para atemperación de vapor de alta presión en la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_vapor_alta(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_vapor_alta", umbral_key="prediccion_flujo_agua_vapor_alta", model_class=SensorFlujoAguaVaporAltaA)

@router_b.post(
    "/prediccion_presion_agua",
    summary="Detectar anomalía - Presión agua AP",
    description="""
Analiza la presión de agua de alimentación en el economizador de alta presión de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de presión (PSI o Bar)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_presion_agua(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua", umbral_key="prediccion_presion_agua", model_class=SensorPresionAgua)

@router_b.post(
    "/prediccion_temperatura_ambiental",
    summary="Detectar anomalía - Temp. ambiental",
    description="""
Analiza la temperatura ambiente en la zona de operación de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_ambiental", umbral_key="prediccion_temperatura_ambiental", model_class=SensorTemperaturaAmbientalA)

@router_b.post(
    "/prediccion_temperatura_agua_alim",
    summary="Detectar anomalía - Temp. agua alimentación",
    description="""
Analiza la temperatura del agua de alimentación de alta presión en la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temperatura_agua_alim(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_agua_alim", umbral_key="prediccion_temperatura_agua_alim", model_class=SensorTemperaturaAguaAlim)

@router_b.post(
    "/prediccion_temperatura_estator",
    summary="Detectar anomalía - Temp. estator",
    description="""
Analiza la temperatura del estator del motor de la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Sobrecalentamiento indica problemas de aislamiento o sobrecarga.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temperatura_estator(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_estator", umbral_key="prediccion_temperatura_estator", model_class=SensorTemperaturaEstator)

@router_b.post(
    "/prediccion_vibracion_axial_empuje",
    summary="Detectar anomalía - Vibración axial empuje",
    description="""
Analiza el nivel de vibración axial en el descanso de empuje de la Bomba 1B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de vibración (mm/s o g)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Vibraciones excesivas indican desbalanceo, desalineación o desgaste.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_vibracion_axial_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_axial_empuje", umbral_key="prediccion_vibracion_axial_empuje", model_class=SensorVibracionAxialEmpuje)

@router_b.post(
    "/prediccion_vibracion_x_descanso",
    summary="Detectar anomalía - Vibración X descanso",
    description="""
Analiza el nivel de vibración en el eje X del descanso interno de la Bomba 1B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de vibración (mm/s o g)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_vibracion_x_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_x_descanso", umbral_key="prediccion_vibracion_x_descanso", model_class=SensorVibracionXDescanso)

@router_b.post(
    "/prediccion_vibracion_y_descanso",
    summary="Detectar anomalía - Vibración Y descanso",
    description="""
Analiza el nivel de vibración en el eje Y del descanso interno de la Bomba 1B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de vibración (mm/s o g)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_vibracion_y_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_y_descanso", umbral_key="prediccion_vibracion_y_descanso", model_class=SensorVibracionYDescanso)

@router_b.post(
    "/prediccion_voltaje_barra",
    summary="Detectar anomalía - Voltaje barra 6.6KV",
    description="""
Analiza el nivel de voltaje en las barras de distribución de 6.6KV para la Bomba B.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de voltaje (KV)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Fluctuaciones de voltaje pueden dañar equipos eléctricos.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_voltaje_barra(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="voltaje_barra", umbral_key="prediccion_voltaje_barra", model_class=SensorVoltajeBarraA)




# Ruta para obtener datos de sensores de corriente
# — Helper genérica actualizada — 
async def _get_and_classify(
    db: Session,
    SensorModel,
    model_key,
    default_data,
    inicio: Optional[str] = None,
    termino: Optional[str] = None,
    limite: int = 40
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
              .limit(limite)
              .all()
        )

    if not sensores:
        # Devolver lista vacía para consistencia con el frontend
        return []

    # DESACTIVADO: Clasificación automática en GET para mejorar velocidad
    # La clasificación ahora solo se hace en los endpoints POST
    # no_clasificados = [s for s in sensores if s.clasificacion is None]
    # if no_clasificados:
    #     datos = [[s.valor_sensor] for s in no_clasificados]
    #     preds = predecir_sensores(datos, modelos[model_key])
    #     for obj, cl in zip(no_clasificados, preds):
    #         obj.clasificacion = int(cl)
    #         db.add(obj)
    #     db.commit()
    #     for obj in no_clasificados:
    #         db.refresh(obj)

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

@router_b.post(
    "/predecir-bomba-b",
    response_model=PrediccionBombaBOutput,
    summary="Prediccion global de falla - Bomba B",
    description="""
Realiza una prediccion de probabilidad de falla utilizando el modelo **Random Forest** entrenado para la Bomba B.

## Parametros de entrada
El modelo requiere **15 variables** de sensores:
- Corriente motor, excentricidad, flujo de descarga AP
- Flujos de agua (domo AP/MP, recalentador, vapor alta)
- Presion agua AP, temperaturas (ambiental, agua alim, estator)
- Vibraciones (axial, X descanso, Y descanso), voltaje barra

## Respuesta
- `prediccion`: Porcentaje de probabilidad de falla (0-100%)
- `status`: Estado de la operacion ("success")

## Almacenamiento
Cada prediccion se guarda en la base de datos con fecha y hora de ejecucion.
    """,
    response_description="Porcentaje de probabilidad de falla y estado de la operacion"
)
async def predecir_bomba_b(
    datos: PrediccionBombaBInput,
    db: Session = Depends(get_db)
):
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
        prediccion = model.predict(input_data.values)
        # Obtener probabilidades para cada clase
        probabilidades = model.predict_proba(input_data.values)
        
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
@router_b.get(
    "/predicciones-bomba-b",
    response_model=List[PrediccionBombaResponse],
    summary="Historico de predicciones - Bomba B",
    description="""
Obtiene el historico de las ultimas predicciones de falla realizadas para la Bomba B.

## Parametros
- `limite`: Cantidad de registros a devolver (1-100, default: 40)

## Respuesta
Lista ordenada cronologicamente (mas antiguos primero) con:
- `id`: Identificador unico de la prediccion
- `valor_prediccion`: Porcentaje de probabilidad de falla
- `hora_ejecucion`: Hora en que se realizo la prediccion
- `dia_ejecucion`: Fecha de la prediccion
    """,
    response_description="Lista de predicciones historicas de la Bomba B"
)
async def obtener_predicciones_bomba(
    db: Session = Depends(get_db),
    limite: int = Query(40, description="Numero de registros a devolver (max 100)", le=100, ge=1)
):
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










@router_b.get(
    "/corriente",
    summary="Histórico - Corriente motor B",
    description="""
Obtiene registros históricos del sensor de corriente eléctrica del motor de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de corriente medido (Amperios)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de corriente"
)
async def get_sensores_corriente(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorCorriente, "corriente_motor", DEFAULT_SENSORES_CORRIENTE, inicio, termino, limite)

@router_b.get(
    "/excentricidad_bomba",
    summary="Histórico - Excentricidad bomba B",
    description="""
Obtiene registros históricos del sensor de excentricidad de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Valores anormales indican desalineación o desgaste en el eje de la bomba.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de excentricidad medido (mm)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de excentricidad"
)
async def get_sensores_excentricidad_bomba(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorExcentricidadBomba, "excentricidad_bomba", DEFAULT_SENSORES_EXCENTRICIDAD, inicio, termino, limite)

@router_b.get(
    "/flujo_descarga",
    summary="Histórico - Flujo descarga AP",
    description="""
Obtiene registros históricos del sensor de flujo de descarga de alta presión de la Bomba B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Variaciones en el flujo pueden indicar cavitación o problemas en válvulas.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de flujo medido (m³/h)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de flujo de descarga"
)
async def get_sensores_flujo_descarga(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoDescarga, "flujo_descarga", DEFAULT_SENSORES_FLUJO_DESCARGA, inicio, termino, limite)

@router_b.get(
    "/flujo_agua_domo_ap",
    summary="Histórico - Flujo agua domo AP",
    description="""
Obtiene registros históricos del sensor de flujo de agua alimentación al domo de alta presión.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Flujo compensado crítico para el balance de vapor en el sistema HRSG.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de flujo compensado (m³/h)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de flujo domo AP"
)
async def get_sensores_flujo_agua_domo_ap(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoAP, "flujo_agua_domo_ap", DEFAULT_SENSORES_FLUJO_AGUA_DOMO_AP, inicio, termino, limite)

@router_b.get(
    "/flujo_domo_ap_compensated",
    summary="Histórico - Flujo domo AP compensado",
    description="Obtiene registros históricos del flujo de agua alimentación domo AP compensado. Usa la misma tabla flujo_agua_domo_ap_b.",
    response_description="Lista de registros históricos"
)
async def get_sensores_flujo_domo_ap_compensated(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoAP, "flujo_agua_domo_ap", DEFAULT_SENSORES_FLUJO_AGUA_DOMO_AP, inicio, termino, limite)

@router_b.get(
    "/flujo_agua_domo_mp",
    summary="Histórico - Flujo agua domo MP",
    description="""
Obtiene registros históricos del sensor de flujo de agua alimentación al domo de media presión.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Flujo compensado para el circuito de media presión del HRSG.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de flujo compensado (m³/h)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de flujo domo MP"
)
async def get_sensores_flujo_agua_domo_mp(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoMP, "flujo_agua_domo_mp", DEFAULT_SENSORES_FLUJO_AGUA_DOMO_MP, inicio, termino, limite)

@router_b.get(
    "/flujo_agua_recalentador",
    summary="Histórico - Flujo agua recalentador",
    description="""
Obtiene registros históricos del sensor de flujo de agua de atemperación del recalentador.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Controla la temperatura del vapor recalentado para proteger la turbina.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de flujo de atemperación (m³/h)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de flujo recalentador"
)
async def get_sensores_flujo_agua_recalentador(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaRecalentadorA, "flujo_agua_recalentador", DEFAULT_SENSORES_FLUJO_AGUA_RECALENTADOR, inicio, termino, limite)

@router_b.get(
    "/flujo_agua_vapor_alta",
    summary="Histórico - Flujo agua vapor alta",
    description="""
Obtiene registros históricos del sensor de flujo de agua de atemperación de vapor de alta presión.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Regula la temperatura del vapor sobrecalentado AP SH.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de flujo de atemperación (m³/h)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de flujo vapor alta"
)
async def get_sensores_flujo_agua_vapor_alta(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaVaporAltaA, "flujo_agua_vapor_alta", DEFAULT_SENSORES_FLUJO_AGUA_VAPOR_ALTA, inicio, termino, limite)

@router_b.get(
    "/presion_agua",
    summary="Histórico - Presión agua AP",
    description="""
Obtiene registros históricos del sensor de presión de agua alimentación al economizador AP.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Presión crítica para el funcionamiento correcto del economizador de alta presión.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de presión medido (bar/PSI)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de presión"
)
async def get_sensores_presion_agua(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAgua, "presion_agua", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router_b.get(
    "/temperatura_ambiental",
    summary="Histórico - Temperatura ambiental",
    description="""
Obtiene registros históricos del sensor de temperatura ambiente.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
La temperatura ambiente afecta la eficiencia del sistema de enfriamiento.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de temperatura medido (°C)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de temperatura ambiental"
)
async def get_sensores_temperatura_ambiental(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaAmbientalA, "temperatura_ambiental", DEFAULT_SENSORES_TEMPERATURA_AMBIENTAL, inicio, termino, limite)

@router_b.get(
    "/temperatura_agua_alim",
    summary="Histórico - Temperatura agua alimentación",
    description="""
Obtiene registros históricos del sensor de temperatura del agua de alimentación AP.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Temperatura crítica para la eficiencia del ciclo térmico y protección del economizador.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de temperatura medido (°C)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de temperatura agua alimentación"
)
async def get_sensores_temperatura_agua_alim(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaAguaAlim, "temperatura_agua_alim", DEFAULT_SENSORES_TEMPERATURA_AGUA_ALIM, inicio, termino, limite)

@router_b.get(
    "/temperatura_estator",
    summary="Histórico - Temperatura estator motor",
    description="""
Obtiene registros históricos del sensor de temperatura del estator del motor de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Temperaturas elevadas indican problemas de aislamiento o sobrecarga del motor.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de temperatura medido (°C)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de temperatura estator"
)
async def get_sensores_temperatura_estator(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaEstator, "temperatura_estator", DEFAULT_SENSORES_TEMPERATURA_ESTATOR, inicio, termino, limite)

@router_b.get(
    "/vibracion_axial_empuje",
    summary="Histórico - Vibración axial empuje",
    description="""
Obtiene registros históricos del sensor de vibración axial del descanso de empuje de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Vibraciones axiales excesivas indican desgaste en cojinetes o desalineación.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de vibración medido (mm/s o g)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de vibración axial"
)
async def get_sensores_vibracion_axial_empuje(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionAxialEmpuje, "vibracion_axial_empuje", DEFAULT_SENSORES_VIBRACION_AXIAL_EMPUJE, inicio, termino, limite)

@router_b.get(
    "/vibracion_x_descanso",
    summary="Histórico - Vibración X descanso",
    description="""
Obtiene registros históricos del sensor de vibración en eje X del descanso interno de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Mide vibraciones radiales que pueden indicar desbalanceo o problemas mecánicos.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de vibración medido (mm/s o g)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de vibración X"
)
async def get_sensores_vibracion_x_descanso(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionXDescanso, "vibracion_x_descanso", DEFAULT_SENSORES_VIBRACION_X_DESCANSO, inicio, termino, limite)

@router_b.get(
    "/vibracion_y_descanso",
    summary="Histórico - Vibración Y descanso",
    description="""
Obtiene registros históricos del sensor de vibración en eje Y del descanso interno de la Bomba 1B.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Complementa la medición del eje X para análisis orbital de vibraciones.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de vibración medido (mm/s o g)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de vibración Y"
)
async def get_sensores_vibracion_y_descanso(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionYDescanso, "vibracion_y_descanso", DEFAULT_SENSORES_VIBRACION_Y_DESCANSO, inicio, termino, limite)

@router_b.get(
    "/voltaje_barra",
    summary="Histórico - Voltaje barra 6.6KV",
    description="""
Obtiene registros históricos del sensor de voltaje de las barras de distribución de 6.6KV.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Indicadores:**
Fluctuaciones de voltaje pueden afectar el rendimiento del motor y otros equipos eléctricos.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de voltaje medido (KV)
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de voltaje"
)
async def get_sensores_voltaje_barra(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVoltajeBarraA, "voltaje_barra", DEFAULT_SENSORES_VOLTAJE_BARRA, inicio, termino, limite)





# ============================================
# ENDPOINTS NUEVOS AGREGADOS - 2025-02-17
# ============================================

# Importar nuevos modelos
from modelos_b.modelos_b import SensorTemperaturaDescansoInternoBombaB, SensorTemperaturaDescansoInternaEmpujeBombaB, SensorTemperaturaDescansoInternaMotorBombaB

@router_b.get(
    "/temp_descanso_bomba",
    summary="Historico - Temp. descanso interno bomba B",
    description="""
Obtiene registros historicos del sensor de temperatura del descanso interno de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de temperatura descanso bomba B"
)
async def get_sensores_temp_descanso_bomba_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaDescansoInternoBombaB, "temp_descanso_bomba", DEFAULT_SENSORES_TEMPERATURA_ESTATOR, inicio, termino, limite)


@router_b.post(
    "/prediccion_temp_descanso_bomba",
    summary="Detectar anomalia - Temp. descanso interno bomba B",
    description="""
Analiza la temperatura del descanso interno de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de temperatura (C)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_temp_descanso_bomba_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_bomba", umbral_key="prediccion_temp_descanso_bomba", model_class=SensorTemperaturaDescansoInternoBombaB)


@router_b.get(
    "/temp_descanso_empuje",
    summary="Historico - Temp. descanso empuje bomba B",
    description="""
Obtiene registros historicos del sensor de temperatura del descanso de empuje de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de temperatura descanso empuje bomba B"
)
async def get_sensores_temp_descanso_empuje_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaDescansoInternaEmpujeBombaB, "temp_descanso_empuje", DEFAULT_SENSORES_TEMPERATURA_ESTATOR, inicio, termino, limite)


@router_b.post(
    "/prediccion_temp_descanso_empuje",
    summary="Detectar anomalia - Temp. descanso empuje bomba B",
    description="""
Analiza la temperatura del descanso de empuje de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de temperatura (C)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_temp_descanso_empuje_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_empuje", umbral_key="prediccion_temp_descanso_empuje", model_class=SensorTemperaturaDescansoInternaEmpujeBombaB)


@router_b.get(
    "/temp_descanso_motor",
    summary="Historico - Temp. descanso motor bomba B",
    description="""
Obtiene registros historicos del sensor de temperatura del descanso del motor de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de temperatura descanso motor bomba B"
)
async def get_sensores_temp_descanso_motor_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaDescansoInternaMotorBombaB, "temp_descanso_motor", DEFAULT_SENSORES_TEMPERATURA_ESTATOR, inicio, termino, limite)


@router_b.post(
    "/prediccion_temp_descanso_motor",
    summary="Detectar anomalia - Temp. descanso motor bomba B",
    description="""
Analiza la temperatura del descanso del motor de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de temperatura (C)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_temp_descanso_motor_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_motor", umbral_key="prediccion_temp_descanso_motor", model_class=SensorTemperaturaDescansoInternaMotorBombaB)


# ============================================
# ENDPOINTS SEÑALES FALTANTES BOMBA B - 2025-02-23
# ============================================

# --- Vibración X Descanso Externo ---
@router_b.get(
    "/vibracion_x_descanso_externo",
    summary="Historico - Vibracion X descanso externo bomba B",
    description="""
Obtiene registros historicos del sensor de vibracion eje X del descanso externo de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de vibracion X externo bomba B"
)
async def get_sensores_vibracion_x_descanso_externo_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionXDescansoExternoB, "vibracion_x_descanso_externo", DEFAULT_SENSORES_VIBRACION_X_DESCANSO, inicio, termino, limite)


@router_b.post(
    "/prediccion_vibracion_x_descanso_externo",
    summary="Detectar anomalia - Vibracion X descanso externo bomba B",
    description="""
Analiza la vibracion en eje X del descanso externo de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de vibracion (um)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_vibracion_x_descanso_externo_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_x_descanso_externo", umbral_key="prediccion_vibracion_x_descanso_externo", model_class=SensorVibracionXDescansoExternoB)


# --- Vibración Y Descanso Externo ---
@router_b.get(
    "/vibracion_y_descanso_externo",
    summary="Historico - Vibracion Y descanso externo bomba B",
    description="""
Obtiene registros historicos del sensor de vibracion eje Y del descanso externo de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de vibracion Y externo bomba B"
)
async def get_sensores_vibracion_y_descanso_externo_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracionYDescansoExternoB, "vibracion_y_descanso_externo", DEFAULT_SENSORES_VIBRACION_Y_DESCANSO, inicio, termino, limite)


@router_b.post(
    "/prediccion_vibracion_y_descanso_externo",
    summary="Detectar anomalia - Vibracion Y descanso externo bomba B",
    description="""
Analiza la vibracion en eje Y del descanso externo de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de vibracion (um)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_vibracion_y_descanso_externo_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_y_descanso_externo", umbral_key="prediccion_vibracion_y_descanso_externo", model_class=SensorVibracionYDescansoExternoB)


# --- Presión Succión BAA ---
@router_b.get(
    "/presion_succion_baa",
    summary="Historico - Presion succion BAA bomba B",
    description="""
Obtiene registros historicos del sensor de presion de succion BAA de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de presion succion BAA bomba B"
)
async def get_sensores_presion_succion_baa_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionSuccionBAAB, "presion_succion_baa", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)


@router_b.post(
    "/prediccion_presion_succion_baa",
    summary="Detectar anomalia - Presion succion BAA bomba B",
    description="""
Analiza la presion de succion BAA de la Bomba B.

**Modelo:** SIN MODELO (pendiente)

**Entrada:**
- `valor_sensor`: Valor numerico de presion (barg)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_presion_succion_baa_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_succion_baa", umbral_key="prediccion_presion_succion_baa", model_class=SensorPresionSuccionBAAB)


# --- Posición Válvula Recirculación ---
@router_b.get(
    "/posicion_valvula_recirc",
    summary="Historico - Posicion valvula recirculacion bomba B",
    description="""
Obtiene registros historicos del sensor de posicion de la valvula de recirculacion de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de posicion valvula recirc bomba B"
)
async def get_sensores_posicion_valvula_recirc_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPosicionValvulaRecircB, "posicion_valvula_recirc", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)


@router_b.post(
    "/prediccion_posicion_valvula_recirc",
    summary="Detectar anomalia - Posicion valvula recirculacion bomba B",
    description="""
Analiza la posicion de la valvula de recirculacion de la Bomba B.

**Modelo:** SIN MODELO (pendiente)

**Entrada:**
- `valor_sensor`: Valor numerico de posicion (%)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_posicion_valvula_recirc_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="posicion_valvula_recirc", umbral_key="prediccion_posicion_valvula_recirc", model_class=SensorPosicionValvulaRecircB)


# --- MW Brutos / Potencia Bruta Planta ---
@router_b.get(
    "/mw_brutos_generacion_gas",
    summary="Historico - MW brutos generacion gas bomba B",
    description="""
Obtiene registros historicos del sensor de MW brutos de generacion de gas (potencia bruta planta).

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de MW brutos bomba B"
)
async def get_sensores_mw_brutos_generacion_gas_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorMwBrutosGeneracionGas, "mw_brutos_generacion_gas", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)


@router_b.post(
    "/prediccion_mw_brutos_generacion_gas",
    summary="Detectar anomalia - MW brutos generacion gas bomba B",
    description="""
Analiza los MW brutos de generacion de gas (potencia bruta planta).

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de potencia (MW)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_mw_brutos_generacion_gas_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="mw_brutos_generacion_gas", umbral_key="prediccion_mw_brutos_generacion_gas", model_class=SensorMwBrutosGeneracionGas)


# --- Presión Agua Econ AP ---
@router_b.get(
    "/presion_agua_econ_ap",
    summary="Historico - Presion agua alimentacion econ AP bomba B",
    description="""
Obtiene registros historicos del sensor de presion de agua alimentacion economizador alta presion de la Bomba B.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de presion agua econ AP bomba B"
)
async def get_sensores_presion_agua_econ_ap_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAguaAlimentacionEconAP, "presion_agua_econ_ap", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)


@router_b.post(
    "/prediccion_presion_agua_econ_ap",
    summary="Detectar anomalia - Presion agua alimentacion econ AP bomba B",
    description="""
Analiza la presion de agua alimentacion economizador alta presion de la Bomba B.

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de presion (barg)
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_presion_agua_econ_ap_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua_econ_ap", umbral_key="prediccion_presion_agua_econ_ap", model_class=SensorPresionAguaAlimentacionEconAP)


# ============================================
# NUEVA RUTA - Flujo agua atemperacion vapor alta AP
# Tabla compartida de Bomba A (gm_influx inserta en flujo_de_agua_atemp_vapor_alta_ap)
# ============================================

@router_b.get(
    "/flujo_atemp_vapor_alta_ap",
    summary="Historico - Flujo agua atemp vapor alta AP bomba B",
    description="""
Obtiene registros historicos del flujo de agua de atemperacion vapor alta presion AP.
Esta tabla es compartida con Bomba A y recibe datos de gm_influx.

**Parametros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad maxima de registros (10-500, default: 40)
    """,
    response_description="Lista de registros historicos de flujo atemp vapor alta AP"
)
async def get_sensores_flujo_atemp_vapor_alta_ap_b(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoDeAguaAtempVaporAltaAP, "flujo_atemp_vapor_alta_ap", DEFAULT_SENSORES_FLUJO_AGUA_VAPOR_ALTA, inicio, termino, limite)


@router_b.post(
    "/prediccion_flujo_atemp_vapor_alta_ap",
    summary="Detectar anomalia - Flujo agua atemp vapor alta AP bomba B",
    description="""
Analiza el flujo de agua de atemperacion de vapor de alta presion AP.
Tabla compartida con Bomba A (flujo_de_agua_atemp_vapor_alta_ap).

**Modelo:** Isolation Forest (deteccion de outliers)

**Entrada:**
- `valor_sensor`: Valor numerico de flujo (kg/h)

**Sistema de alertas:**
Se evaluan las anomalias en una ventana de 8 horas:
- **AVISO**: 3+ anomalias
- **ALERTA**: 8+ anomalias
- **CRITICA**: 15+ anomalias
    """,
    response_description="Resultado de la prediccion con clasificacion y estado de alertas"
)
async def predecir_flujo_atemp_vapor_alta_ap_b(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_atemp_vapor_alta_ap", umbral_key="prediccion_flujo_atemp_vapor_alta_ap", model_class=SensorFlujoDeAguaAtempVaporAltaAP)

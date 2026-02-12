from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta, timezone
import numpy as np
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from esquemas.esquema import SensorInput, PrediccionBombaInput, PrediccionBombaOutput, PrediccionBombaResponse
from modelos.database import get_db
from modelos.modelos import (SensorCorriente, SensorSalidaAgua, SensorPresionAgua, SensorMw_brutos_generacion_gas,
                          SensorTemperatura_Ambiental, SensorTemperatura_descanso_interna_empuje_bomba_1aa,
                          SensorTemperatura_descanso_interna_motor_bomba_1a, SensorTemperatura_descanso_interno_bomba_1a,
                          SensorVibracion_axial_descanso, SensorVoltaje_barra, PrediccionBombaA, Alerta, Bitacora,
                          SensorExcentricidadBomba, SensorFlujoAguaDomoAP, SensorFlujoAguaDomoMP,
                          SensorFlujoAguaRecalentador, SensorFlujoAguaVaporAlta, SensorPosicionValvulaRecirc,
                          SensorPresionAguaMP, SensorPresionSuccionBAA, SensorTemperaturaEstator, SensorFlujoSalida12FPMFC)

router = APIRouter(prefix="/sensores", tags=["Sensores Bomba A"])


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
MODELS_DIR = os.path.join(BASE_DIR, "..", "modelos_prediccion")  # Ruta absoluta a la carpeta de modelos

# Mapa de claves de modelo a rutas de archivo
MODEL_PATHS = {
    # Modelos originales actualizados
    "corriente_motor": "Corriente_MTR_BBA_Agua_Alim_1A.pkl",
    "mw_brutos_gas": "model_MW_brutos.pkl",
    "presion_agua": "Presi_n_Agua_Alimentacion_Econ._AP.pkl",
    "salida_bomba": "Temperatura_descarga_Bba_Agua_Alim_1A.pkl",
    "temperatura_ambiental": "Temp_Ambiental.pkl",
    "temp_descanso_bomba_1a": "Vibracion_X_Descanso_Interno_Bomba_1A_A.pkl",
    "temp_descanso_empuje_bomba_1a": "Vibracion_Y_Descanso_Interno_Bomba_1A_B.pkl",
    "temp_descanso_motor_bomba_1a": "Temperatura_Descanso_Interno_MTR_Bomba_1A.pkl",
    "vibracion_axial_empuje": "Vibracion_Axial_Descanso_Empuje_Bomba_1A.pkl",
    "voltaje_barra": "Voltaje_Barra_6_6KV.pkl",
    
    # Modelos adicionales
    "excentricidad_bomba": "Excentricidad_Bomba_1A.pkl",
    "flujo_agua_domo_ap": "Flujo_de_Agua_Alimentacion_Domo_AP_Compensated_18B.pkl",
    "flujo_agua_domo_mp": "Flujo_de_Agua_Alimentacion_Domo_MP_Compensated_16B.pkl",
    "flujo_agua_recalentador": "Flujo_de_Agua_Atemp_Recale_Calient_RH.pkl",
    "flujo_agua_vapor_alta": "Flujo_de_Agua_Atemp_Vapor_Alta_AP_SH.pkl",
    "posicion_valvula_recirc": "Posicion_v_lvula_recirc_BAA_AE01A.pkl",
    "presion_agua_mp": "Presion_Agua_Alimentacion_Econ._MP.pkl",
    "presion_succion_baa": "Presion_succion_BAA_AE01A.pkl",
    "temperatura_estator": "Temperatura_Estator_MTR_BBA_AA_1A_A.pkl",
    "flujo_salida_12fpmfc": "12FPMFC.1B.OUT.pkl",
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
# NOTA: Umbrales ajustados para pruebas con datos limitados (100 registros por sensor)
# En produccion, restaurar valores originales segun analisis historico
UMBRAL_SENSORES = {
    'prediccion_corriente': {
        "umbral_minimo": 3,   # AVISO
        "umbral_alerta": 8,   # ALERTA
        "umbral_critica": 15, # CRITICA
    },
    'prediccion_salida-agua': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_presion-agua': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_mw-brutos-gas': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_temperatura-ambiental': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_temp-descanso-bomba-1a': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_temp-empuje-bomba-1a': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_temp-motor-bomba-1a': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_vibracion-axial': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_voltaje-barra': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_flujo-salida-12fpmfc': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_flujo-agua-domo-ap': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_flujo-agua-domo-mp': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_excentricidad-bomba': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_flujo-agua-recalentador': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_flujo-agua-vapor-alta': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_posicion-valvula-recirc': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_presion-agua-mp': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_presion-succion-baa': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
    },
    'prediccion_temperatura-estator': {
        "umbral_minimo": 3,
        "umbral_alerta": 8,
        "umbral_critica": 15,
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
    Cuenta las anomalías (clasificacion == -1) en una ventana de tiempo específica y retorna información temporal detallada.
    CORREGIDO: Busca todas las anomalías sin filtrar por sensor_id específico, ya que cada registro es único.
    
    Args:
        db: Sesión de base de datos
        model_class: Clase del modelo de sensor
        tiempo_base: Tiempo de referencia para la ventana
    
    Returns:
        dict: Información detallada de anomalías incluyendo conteo, timestamps y patrones temporales
    """
    try:
        # Calcular el rango de tiempo (ventana de VENTANA_HORAS horas hacia atrás)
        tiempo_inicio = tiempo_base - timedelta(hours=VENTANA_HORAS)
        
        # CORRECCIÓN CRÍTICA: Buscar TODAS las anomalías en la ventana de tiempo
        # No filtrar por sensor_id ya que cada registro es único con su propio ID auto-incremental
        anomalias_query = db.query(model_class).filter(
            model_class.clasificacion == -1,
            model_class.tiempo_ejecucion.isnot(None),
            model_class.tiempo_ejecucion >= tiempo_inicio,
            model_class.tiempo_ejecucion <= tiempo_base
        ).all()
        
        logger.info(f"[CONTAR_ANOMALIAS] Buscando anomalías entre {tiempo_inicio} y {tiempo_base}")
        logger.info(f"[CONTAR_ANOMALIAS] Encontradas {len(anomalias_query)} anomalías en ventana de tiempo")
        
        # También buscar registros con tiempo_ejecucion NULL para compatibilidad con datos existentes
        anomalias_null_time = db.query(model_class).filter(
            model_class.clasificacion == -1,
            model_class.tiempo_ejecucion.is_(None)
        ).all()
        
        # Filtrar registros con tiempo NULL por ventana de tiempo usando tiempo_sensor
        anomalias_en_ventana = list(anomalias_query)  # Copiar las anomalías con tiempo válido
        fecha_actual = tiempo_base.date()
        
        for anomalia in anomalias_null_time:
            tiempo_registro = None
            
            if hasattr(anomalia, 'tiempo_sensor') and anomalia.tiempo_sensor:
                # Para registros con tiempo_ejecucion NULL, construir timestamp usando fecha actual + tiempo_sensor
                try:
                    # Parsear tiempo_sensor (formato "HH:MM:SS")
                    hora_str = str(anomalia.tiempo_sensor)
                    if ':' in hora_str:
                        hora_parts = hora_str.split(':')
                        if len(hora_parts) >= 2:
                            hora = int(hora_parts[0])
                            minuto = int(hora_parts[1])
                            segundo = int(hora_parts[2]) if len(hora_parts) > 2 else 0
                            tiempo_registro = datetime.combine(fecha_actual, datetime.min.time().replace(hour=hora, minute=minuto, second=segundo))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parseando tiempo_sensor {anomalia.tiempo_sensor}: {e}")
                    continue
            
            # Verificar si el registro está dentro de la ventana de tiempo
            if tiempo_registro and tiempo_inicio <= tiempo_registro <= tiempo_base:
                anomalias_en_ventana.append(anomalia)
        
        conteo_total = len(anomalias_en_ventana)
        logger.info(f"[CONTAR_ANOMALIAS] Total de anomalías en ventana (incluyendo NULL): {conteo_total}")
        
        if conteo_total == 0:
            return {
                'conteo': 0,
                'primera_anomalia': None,
                'ultima_anomalia': None,
                'duracion_total': None,
                'anomalias_consecutivas': 0,
                'frecuencia_por_hora': 0.0,
                'distribucion_temporal': [],
                'patron_consecutivo': False
            }
        
        # Extraer timestamps válidos para análisis temporal
        timestamps_validos = []
        for anomalia in anomalias_en_ventana:
            if anomalia.tiempo_ejecucion is not None:
                timestamps_validos.append(anomalia.tiempo_ejecucion)
            elif hasattr(anomalia, 'tiempo_sensor') and anomalia.tiempo_sensor:
                try:
                    hora_str = str(anomalia.tiempo_sensor)
                    if ':' in hora_str:
                        hora_parts = hora_str.split(':')
                        if len(hora_parts) >= 2:
                            hora = int(hora_parts[0])
                            minuto = int(hora_parts[1])
                            segundo = int(hora_parts[2]) if len(hora_parts) > 2 else 0
                            tiempo_construido = datetime.combine(fecha_actual, datetime.min.time().replace(hour=hora, minute=minuto, second=segundo))
                            timestamps_validos.append(tiempo_construido)
                except (ValueError, AttributeError):
                    continue
        
        # Usar timestamps_validos en lugar de la línea anterior que causaba error
        timestamps = sorted(timestamps_validos)
        
        # Verificar que tengamos timestamps válidos
        if not timestamps:
            return {
                'conteo': 0,
                'primera_anomalia': None,
                'ultima_anomalia': None,
                'duracion_total': None,
                'anomalias_consecutivas': 0,
                'frecuencia_por_hora': 0.0,
                'distribucion_temporal': [],
                'patron_consecutivo': False
            }
        
        primera_anomalia = timestamps[0]
        ultima_anomalia = timestamps[-1]
        
        # Calcular duración total
        duracion_total = (ultima_anomalia - primera_anomalia).total_seconds() / 3600  # en horas
        
        # Calcular frecuencia por hora
        frecuencia_por_hora = conteo_total / VENTANA_HORAS if VENTANA_HORAS > 0 else 0
        
        # Detectar anomalías consecutivas y patrones
        anomalias_consecutivas = calcular_anomalias_consecutivas(timestamps)
        patron_consecutivo = anomalias_consecutivas >= 3  # 3 o más anomalías consecutivas
        
        # Crear distribución temporal por horas
        distribucion_temporal = crear_distribucion_temporal(timestamps, tiempo_inicio, tiempo_base)
        
        return {
            'conteo': conteo_total,
            'primera_anomalia': primera_anomalia,
            'ultima_anomalia': ultima_anomalia,
            'duracion_total': duracion_total,
            'anomalias_consecutivas': anomalias_consecutivas,
            'frecuencia_por_hora': round(frecuencia_por_hora, 2),
            'distribucion_temporal': distribucion_temporal,
            'patron_consecutivo': patron_consecutivo
        }
    except Exception as e:
        logger.error(f"Error al contar anomalías: {str(e)}")
        return {
            'conteo': 0,
            'primera_anomalia': None,
            'ultima_anomalia': None,
            'duracion_total': None,
            'anomalias_consecutivas': 0,
            'frecuencia_por_hora': 0.0,
            'distribucion_temporal': [],
            'patron_consecutivo': False
        }



# Información detallada de cada sensor para mensajes más descriptivos
def calcular_anomalias_consecutivas(timestamps: list) -> int:
    """
    Calcula el número máximo de anomalías consecutivas en una secuencia temporal.
    
    Args:
        timestamps: Lista de timestamps de anomalías ordenados cronológicamente
    
    Returns:
        int: Número máximo de anomalías consecutivas
    """
    if len(timestamps) <= 1:
        return len(timestamps)
    
    max_consecutivas = 1
    consecutivas_actuales = 1
    
    # Definir umbral de tiempo para considerar anomalías como consecutivas (30 minutos)
    umbral_consecutivo = timedelta(minutes=30)
    
    for i in range(1, len(timestamps)):
        tiempo_diferencia = timestamps[i] - timestamps[i-1]
        
        if tiempo_diferencia <= umbral_consecutivo:
            consecutivas_actuales += 1
            max_consecutivas = max(max_consecutivas, consecutivas_actuales)
        else:
            consecutivas_actuales = 1
    
    return max_consecutivas


def crear_distribucion_temporal(timestamps: list, tiempo_inicio: datetime, tiempo_fin: datetime) -> list:
    """
    Crea una distribución temporal de anomalías por horas dentro de la ventana de tiempo.
    
    Args:
        timestamps: Lista de timestamps de anomalías
        tiempo_inicio: Inicio de la ventana de tiempo
        tiempo_fin: Fin de la ventana de tiempo
    
    Returns:
        list: Lista de diccionarios con hora y conteo de anomalías
    """
    # Crear buckets por hora
    distribucion = []
    hora_actual = tiempo_inicio.replace(minute=0, second=0, microsecond=0)
    
    while hora_actual < tiempo_fin:
        hora_siguiente = hora_actual + timedelta(hours=1)
        
        # Contar anomalías en esta hora
        anomalias_en_hora = sum(1 for ts in timestamps 
                               if hora_actual <= ts < hora_siguiente)
        
        distribucion.append({
            'hora': hora_actual.strftime('%H:%M'),
            'conteo': anomalias_en_hora
        })
        
        hora_actual = hora_siguiente
    
    return distribucion


def formatear_duracion(duracion_horas: float) -> str:
    """
    Formatea la duración en horas a un formato legible.
    
    Args:
        duracion_horas: Duración en horas
    
    Returns:
        str: Duración formateada
    """
    if duracion_horas is None:
        return "N/A"
    
    if duracion_horas < 1:
        minutos = int(duracion_horas * 60)
        return f"{minutos} minutos"
    elif duracion_horas < 24:
        horas = int(duracion_horas)
        minutos = int((duracion_horas - horas) * 60)
        return f"{horas}h {minutos}m"
    else:
        dias = int(duracion_horas / 24)
        horas_restantes = int(duracion_horas % 24)
        return f"{dias}d {horas_restantes}h"


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
    'prediccion_presion-agua': {
        'nombre': 'Presión de agua',
        'descripcion': 'Nivel de presión en el sistema hidráulico',
        'acciones': {
            'AVISO': 'Verificar sistema de regulación de presión',
            'ALERTA': 'Revisar posibles fugas o fallos en el sistema de presión',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrepresión en el sistema hidráulico'
        }
    },
    'prediccion_mw-brutos-gas': {
        'nombre': 'MW brutos de gas',
        'descripcion': 'Generación de potencia bruta por consumo de gas',
        'acciones': {
            'AVISO': 'Verificar eficiencia en la conversión de gas a potencia',
            'ALERTA': 'Revisar sistema de combustión y suministro de gas',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en sistema de generación'
        }
    },
    'prediccion_temperatura-ambiental': {
        'nombre': 'Temperatura ambiental',
        'descripcion': 'Temperatura ambiente en la zona de operación',
        'acciones': {
            'AVISO': 'Verificar sistemas de ventilación y refrigeración',
            'ALERTA': 'Activar sistemas adicionales de enfriamiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrecalentamiento de equipos'
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
    },
    # Nuevos sensores
    'prediccion_excentricidad-bomba': {
        'nombre': 'Excentricidad Bomba 1A',
        'descripcion': 'Medición de excentricidad en la bomba 1A',
        'acciones': {
            'AVISO': 'Verificar alineación y balanceo del rotor',
            'ALERTA': 'Revisar desgaste en cojinetes y programar mantenimiento',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla catastrófica por desalineación'
        }
    },
    'prediccion_flujo-agua-domo-ap': {
        'nombre': 'Flujo de Agua Domo AP',
        'descripcion': 'Flujo de agua de alimentación al domo de alta presión',
        'acciones': {
            'AVISO': 'Verificar sistema de control de flujo y válvulas',
            'ALERTA': 'Revisar posibles obstrucciones o fallos en bombas de alimentación',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrecalentamiento en domo AP'
        }
    },
    'prediccion_flujo-agua-domo-mp': {
        'nombre': 'Flujo de Agua Domo MP',
        'descripcion': 'Flujo de agua de alimentación al domo de media presión',
        'acciones': {
            'AVISO': 'Verificar sistema de control de flujo y niveles',
            'ALERTA': 'Revisar funcionamiento de válvulas y sistema de bombeo',
            'CRÍTICA': 'Intervención inmediata: Riesgo de operación inadecuada del domo MP'
        }
    },
    'prediccion_flujo-agua-recalentador': {
        'nombre': 'Flujo de Agua Recalentador',
        'descripcion': 'Flujo de agua para atemperación del recalentador',
        'acciones': {
            'AVISO': 'Verificar sistema de control de temperatura',
            'ALERTA': 'Revisar posibles fugas o bloqueos en sistema de atemperación',
            'CRÍTICA': 'Intervención inmediata: Riesgo de sobrecalentamiento en recalentador'
        }
    },
    'prediccion_flujo-agua-vapor-alta': {
        'nombre': 'Flujo de Agua Vapor Alta',
        'descripcion': 'Flujo de agua para atemperación de vapor de alta presión',
        'acciones': {
            'AVISO': 'Verificar sistema de control de temperatura del vapor',
            'ALERTA': 'Revisar válvulas de atemperación y sensores de temperatura',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en turbina por temperatura excesiva'
        }
    },
    'prediccion_posicion-valvula-recirc': {
        'nombre': 'Posición Válvula Recirculación',
        'descripcion': 'Posición de la válvula de recirculación de la bomba de agua de alimentación',
        'acciones': {
            'AVISO': 'Verificar sistema de control de la válvula',
            'ALERTA': 'Revisar actuador y posibles fugas en la válvula',
            'CRÍTICA': 'Intervención inmediata: Riesgo de cavitación en bomba por flujo inadecuado'
        }
    },
    'prediccion_presion-agua-mp': {
        'nombre': 'Presión Agua MP',
        'descripcion': 'Presión del agua de alimentación en el economizador de media presión',
        'acciones': {
            'AVISO': 'Verificar sistema de control de presión',
            'ALERTA': 'Revisar posibles fugas o restricciones en tuberías',
            'CRÍTICA': 'Intervención inmediata: Riesgo de daño en economizador por presión anormal'
        }
    },
    'prediccion_presion-succion-baa': {
        'nombre': 'Presión Succión BAA',
        'descripcion': 'Presión en la succión de la bomba de agua de alimentación',
        'acciones': {
            'AVISO': 'Verificar nivel en tanque de agua de alimentación',
            'ALERTA': 'Revisar posibles restricciones en línea de succión',
            'CRÍTICA': 'Intervención inmediata: Riesgo de cavitación y daño en bomba'
        }
    },
    'prediccion_temperatura-estator': {
        'nombre': 'Temperatura Estator',
        'descripcion': 'Temperatura del estator del motor de la bomba de agua de alimentación',
        'acciones': {
            'AVISO': 'Verificar sistema de refrigeración del motor',
            'ALERTA': 'Revisar carga del motor y sistema de ventilación',
            'CRÍTICA': 'Intervención inmediata: Riesgo de falla en aislamiento del motor'
        }
    },
    'prediccion_flujo-salida-12fpmfc': {
        'nombre': 'Flujo Salida 12FPMFC',
        'descripcion': 'Flujo de salida en el medidor de flujo 12FPMFC',
        'acciones': {
            'AVISO': 'Verificar calibración del medidor de flujo',
            'ALERTA': 'Revisar posibles obstrucciones o fallos en el sistema',
            'CRÍTICA': 'Intervención inmediata: Riesgo de operación inadecuada por medición incorrecta'
        }
    }
}

def determinar_alerta(info_anomalias: dict, umbral_sensor_key: str, bomba_id: str = "A") -> dict:
    """
    Devuelve un diccionario con información completa de la alerta incluyendo datos temporales.
    
    Args:
        info_anomalias: Diccionario con información detallada de anomalías (de contar_anomalias)
        umbral_sensor_key: Clave del sensor en UMBRAL_SENSORES
        bomba_id: Identificador de la bomba (A o B)
        
    Returns:
        dict: Información completa de la alerta con datos temporales o None si no hay alerta
    """
    # Extraer el conteo de anomalías del diccionario
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
            "info_temporal": {
                "primera_anomalia": info_anomalias.get('primera_anomalia'),
                "ultima_anomalia": info_anomalias.get('ultima_anomalia'),
                "duracion_total": info_anomalias.get('duracion_total'),
                "anomalias_consecutivas": info_anomalias.get('anomalias_consecutivas'),
                "frecuencia_por_hora": info_anomalias.get('frecuencia_por_hora'),
                "distribucion_temporal": info_anomalias.get('distribucion_temporal'),
                "patron_consecutivo": info_anomalias.get('patron_consecutivo')
            },
            "timestamp_alerta": datetime.now(timezone.utc).isoformat()
        }
    
    return None


def _crear_mensaje_temporal(info_anomalias: dict, nivel: str) -> str:
    """
    Crea un mensaje descriptivo con la información temporal de las anomalías.
    
    Args:
        info_anomalias: Diccionario con información temporal de anomalías
        nivel: Nivel de la alerta (AVISO, ALERTA, CRÍTICA)
        
    Returns:
        str: Mensaje temporal descriptivo
    """
    conteo = info_anomalias.get('conteo', 0)
    duracion = info_anomalias.get('duracion_total')
    consecutivas = info_anomalias.get('anomalias_consecutivas', 0)
    frecuencia = info_anomalias.get('frecuencia_por_hora', 0)
    primera = info_anomalias.get('primera_anomalia')
    ultima = info_anomalias.get('ultima_anomalia')
    
    mensaje_partes = []
    
    # Información básica de conteo y duración
    if duracion:
        duracion_formateada = formatear_duracion(duracion)
        mensaje_partes.append(f"Se detectaron {conteo} anomalías en las últimas {duracion_formateada}")
    else:
        mensaje_partes.append(f"Se detectaron {conteo} anomalías")
    
    # Información sobre anomalías consecutivas
    if consecutivas > 1:
        if nivel == "CRÍTICA":
            mensaje_partes.append(f"CRÍTICO: {consecutivas} anomalías consecutivas detectadas")
        elif nivel == "ALERTA":
            mensaje_partes.append(f"ATENCIÓN: {consecutivas} anomalías consecutivas")
        else:
            mensaje_partes.append(f"{consecutivas} anomalías consecutivas")
    
    # Información sobre frecuencia
    if frecuencia > 0:
        if frecuencia >= 5:
            mensaje_partes.append(f"Frecuencia alta: {frecuencia:.1f} anomalías/hora")
        elif frecuencia >= 2:
            mensaje_partes.append(f"Frecuencia moderada: {frecuencia:.1f} anomalías/hora")
        else:
            mensaje_partes.append(f"Frecuencia: {frecuencia:.1f} anomalías/hora")
    
    # Información temporal específica
    if primera and ultima:
        if primera == ultima:
            mensaje_partes.append(f"Última detección: {ultima.strftime('%H:%M:%S')}")
        else:
            mensaje_partes.append(f"Período: {primera.strftime('%H:%M')} - {ultima.strftime('%H:%M')}")
    
    return ". ".join(mensaje_partes) + "."


def nivel_numerico(nivel: str) -> int:
    """Convierte el nivel textual a un valor numérico para comparaciones"""
    if nivel and ':' in nivel:
        nivel = nivel.split(':')[0].strip()
    return {"AVISO": 1, "ALERTA": 2, "CRÍTICA": 3}.get(nivel, 0)


def procesar(sensor: SensorInput, db: Session, modelo_key: str, umbral_key: str, model_class):
    """
    Lógica común de clasificación, conteo incremental/decremental y generación de alertas.
    Implementa arquitectura de series temporales para anomalías.

    Si recibe id_sensor, actualiza el registro específico.
    Si no, busca el último registro o crea uno nuevo.
    """
    try:
        # Predecir si es anomalía o no
        clase = predecir_sensores_np(modelos[modelo_key], sensor.valor)
        descripcion = "Normal" if clase == 1 else "Anomalía"
        tiempo_actual = datetime.now()

        # Parsear tiempo_sensor si viene
        sensor_dt = None
        try:
            if hasattr(sensor, 'tiempo_sensor') and sensor.tiempo_sensor is not None:
                if isinstance(sensor.tiempo_sensor, datetime):
                    sensor_dt = sensor.tiempo_sensor
                elif isinstance(sensor.tiempo_sensor, str):
                    # Intentar formatos comunes (ISO y variantes)
                    try:
                        sensor_dt = datetime.fromisoformat(sensor.tiempo_sensor.replace('Z', '+00:00'))
                    except Exception:
                        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                            try:
                                sensor_dt = datetime.strptime(sensor.tiempo_sensor, fmt)
                                break
                            except Exception:
                                pass
                        # Si viene sólo la hora, combinamos con la fecha del servidor
                        if not sensor_dt:
                            for fmt in ("%H:%M:%S", "%H:%M"):
                                try:
                                    hora_tmp = datetime.strptime(sensor.tiempo_sensor, fmt).time()
                                    sensor_dt = datetime.combine(tiempo_actual.date(), hora_tmp)
                                    break
                                except Exception:
                                    pass
            if not sensor_dt:
                sensor_dt = tiempo_actual
        except Exception:
            sensor_dt = tiempo_actual

        # NUEVA LÓGICA: Si viene id_sensor, actualizar ese registro específico
        clasificacion_anterior = None
        contador_anterior = 0

        if sensor.id_sensor:
            # OPTIMIZACIÓN: UPDATE directo sin SELECT previo
            # Primero obtenemos el contador anterior para el cálculo posterior
            lectura_anterior = db.query(model_class.clasificacion, model_class.contador_anomalias).filter(
                model_class.id == sensor.id_sensor
            ).first()

            if not lectura_anterior:
                logger.error(f"Registro con id {sensor.id_sensor} no encontrado")
                raise HTTPException(404, f"Registro con id {sensor.id_sensor} no encontrado")

            clasificacion_anterior = lectura_anterior.clasificacion
            contador_anterior = lectura_anterior.contador_anomalias if lectura_anterior.contador_anomalias else 0

            # UPDATE directo (no traemos todo el registro)
            rows_updated = db.query(model_class).filter(
                model_class.id == sensor.id_sensor
            ).update({
                'clasificacion': clase
            }, synchronize_session=False)

            if rows_updated == 0:
                raise HTTPException(404, f"No se pudo actualizar registro {sensor.id_sensor}")

            logger.info(f"✅ UPDATE directo ID {sensor.id_sensor}: clasificacion={clase}")

            # Necesitamos el objeto para usar después
            lectura = db.query(model_class).filter(
                model_class.id == sensor.id_sensor
            ).first()

        else:
            # Comportamiento original: buscar último registro o crear nuevo
            lectura = db.query(model_class).filter(
                model_class.tiempo_ejecucion.isnot(None)
            ).order_by(model_class.id.desc()).first()

            if not lectura:
                # No existe registro previo, crear nuevo
                logger.info(f"No se encontró registro previo. Creando nuevo registro para sensor.")
                lectura = model_class(
                    tiempo_ejecucion=sensor_dt,
                    tiempo_sensor=(sensor.tiempo_sensor if isinstance(sensor.tiempo_sensor, str) else sensor_dt.strftime("%Y-%m-%d %H:%M:%S")),
                    valor_sensor=sensor.valor,
                    clasificacion=clase,
                    contador_anomalias=0
                )
                db.add(lectura)
                clasificacion_anterior = None
                contador_anterior = 0
            else:
                # Actualizar registro existente
                clasificacion_anterior = lectura.clasificacion
                contador_anterior = lectura.contador_anomalias if hasattr(lectura, 'contador_anomalias') else 0

                # Actualizar valores del registro existente
                lectura.clasificacion = clase
                lectura.valor_sensor = sensor.valor
                lectura.tiempo_ejecucion = sensor_dt
                lectura.tiempo_sensor = (sensor.tiempo_sensor if isinstance(sensor.tiempo_sensor, str) else sensor_dt.strftime("%Y-%m-%d %H:%M:%S"))

                tipo_valor = "anomalía" if clase == -1 else "normal"
                logger.info(f"Actualizando registro existente ID: {lectura.id} con valor {tipo_valor}")

        # Commit después de actualizar/crear
        try:
            db.commit()
            if hasattr(lectura, 'id') and lectura.id:
                db.refresh(lectura)
        except Exception as commit_error:
            logger.error(f"Error al procesar registro: {str(commit_error)}")
            db.rollback()
            raise
            
    except Exception as e:
        logger.error(f"Error general en procesar(): {str(e)}")
        raise HTTPException(500, f"Error al procesar datos del sensor: {str(e)}")
    
    # Obtenemos la información detallada de anomalías en la ventana de tiempo
    # Validar que tiempo_ejecucion no sea None antes de llamar a contar_anomalias
    tiempo_base = lectura.tiempo_ejecucion if lectura.tiempo_ejecucion is not None else datetime.now()
    if tiempo_base is None:
        # Si tiempo_ejecucion es None, usar la fecha/hora actual
        tiempo_base = datetime.now()
        logger.warning("tiempo_ejecucion es None, usando datetime.now()")

    # OPTIMIZACIÓN: Usar versión con cache
    info_anomalias = contar_anomalias_cached(db, model_class, tiempo_base)
    conteo_anomalias = info_anomalias['conteo']

    
    # Ajustar contador según la clasificación
    if clase == 1:  # Si es normal
        # El contador se mantiene igual, no se modifica
        lectura.contador_anomalias = contador_anterior
        print(f"[{umbral_key}] Valor normal. Contador se mantiene en {contador_anterior}")
    else:  # Si es anomalía
        # CORRECCIÓN: Para anomalías usamos el conteo real de la ventana de tiempo
        # NO sumamos +1 porque el registro actual ya está incluido en el conteo
        print(f"[DEBUG] conteo_anomalias devuelto por función: {conteo_anomalias}")
        print(f"[DEBUG] Asignando contador_anomalias = {conteo_anomalias}")
        lectura.contador_anomalias = conteo_anomalias
        print(f"[{umbral_key}] Anomalía detectada. Anomalías en ventana de tiempo: {conteo_anomalias}")
    
    # Hacer commit para guardar el contador actualizado
    db.commit()
    
    # Si es anomalía, evaluamos niveles de alerta basados en el conteo de anomalías
    if clase == -1 and lectura.contador_anomalias > 0:
        # Usamos la información completa de anomalías para determinar la alerta
        alerta_info = determinar_alerta(info_anomalias, umbral_key, "A")
        if alerta_info:
            # Buscar alerta previa para comparar nivel
            prev = db.query(Alerta) \
                     .filter(Alerta.tipo_sensor == umbral_key) \
                     .order_by(Alerta.id.desc()) \
                     .first()
            
            # Obtener nivel numérico de alerta previa y actual
            prev_n = nivel_numerico(prev.descripcion) if prev else 0
            curr_n = nivel_numerico(alerta_info["nivel"])
            
            # Solo generar nueva alerta si el nivel ha aumentado
            if curr_n > prev_n:
                # Construir mensaje descriptivo (simplificado según requerimiento del cliente)
                # Formato: tipo de alerta, sensor, bomba, descripción, intervalo, acción recomendada

                # Formatear intervalo de tiempo
                inicio_anomalia = info_anomalias.get('primera_anomalia')
                fin_anomalia = info_anomalias.get('ultima_anomalia')
                if inicio_anomalia and fin_anomalia:
                    intervalo = f"{inicio_anomalia.strftime('%Y-%m-%d %H:%M')} - {fin_anomalia.strftime('%Y-%m-%d %H:%M')}"
                else:
                    intervalo = "No disponible"

                mensaje = f"{alerta_info['nivel']}: {alerta_info['nombre_sensor']}\n"
                mensaje += f"Bomba: A\n"
                mensaje += f"Descripción: {alerta_info['descripcion_sensor']}\n"
                mensaje += f"Intervalo: {intervalo}\n"
                mensaje += f"Acción recomendada: {alerta_info['accion_recomendada']}"
                
                alerta = Alerta(
                    sensor_id=lectura.id,
                    tipo_sensor=umbral_key,
                    descripcion=mensaje,
                    timestamp=datetime.now(),
                    contador_anomalias=lectura.contador_anomalias,
                    timestamp_inicio_anomalia=info_anomalias.get('primera_anomalia'),
                    timestamp_fin_anomalia=info_anomalias.get('ultima_anomalia')
                )
                db.add(alerta)
                db.commit()

                # Si alcanzamos nivel CRÍTICA, reiniciar contador a 0
                if alerta_info["nivel"] == "CRÍTICA":
                    lectura.contador_anomalias = 0
                    db.commit()
                    print(f"[{umbral_key}] Nivel CRÍTICO alcanzado. Contador reiniciado a 0")

    return {
        "id_registro": lectura.id,
        "valor": sensor.valor,
        "prediccion": clase,
        "descripcion": descripcion,
        "contador_anomalias": conteo_anomalias
    }


# ————— Rutas Post —————

@router.post(
    "/predecir-bomba",
    response_model=PrediccionBombaOutput,
    summary="Prediccion global de falla - Bomba A",
    description="""
Realiza una prediccion de probabilidad de falla utilizando el modelo **Random Forest** entrenado para la Bomba A.

## Parametros de entrada
El modelo requiere **20 variables** de sensores:
- Presion de agua, voltaje de barra, corriente del motor
- Vibraciones, temperaturas (motor, bomba, empuje, ambiental)
- Flujos de agua (domo AP/MP, recalentador, vapor alta)
- Excentricidad, posicion de valvula, MW brutos de gas

## Respuesta
- `prediccion`: Porcentaje de probabilidad de falla (0-100%)
- `status`: Estado de la operacion ("success")

## Almacenamiento
Cada prediccion se guarda en la base de datos con fecha y hora de ejecucion.
    """,
    response_description="Porcentaje de probabilidad de falla y estado de la operacion"
)
async def predecir_bomba(
    datos: PrediccionBombaInput,
    db: Session = Depends(get_db)
):
    try:
        # Obtener el modelo usando ModelRegistry en lugar de cargarlo directamente
        logger.info("Obteniendo modelo para predicción de bomba")
        model_path = os.path.join(MODELS_DIR, "bm_randomforest_bomba_a.pkl")
        model = joblib.load(model_path)
        
        # Preparar los datos en el orden correcto para el modelo
        input_data = pd.DataFrame([{
            # Campos originales
            'Presión Agua Alimentación AP (barg)': datos.presion_agua,
            'Voltaje Barra 6,6KV (V)': datos.voltaje_barra,
            'Corriente Motor Bomba Agua Alimentacion BFWP A (A)': datos.corriente_motor,
            'Vibración Axial Descanso Emp Bomba 1A (ms)': datos.vibracion_axial,
            'Salida de Bomba de Alta Presión': datos.salida_bomba,
            'Flujo de Agua Atemperación Vapor Alta AP SH (kg/h)': datos.flujo_agua,
            'MW Brutos de Generación Total Gas (MW)': datos.mw_brutos_gas,
            'Temperatura Descanso Interno Motor Bomba 1A (°C)': datos.temp_motor,
            'Temperatura Descanso Interno Bomba 1A (°C)': datos.temp_bomba,
            'Temperatura Descanso Interno Empuje Bomba 1A (°C)': datos.temp_empuje,
            'Temperatura Ambiental (°C)': datos.temp_ambiental,
            
            # Campos adicionales para los otros modelos
            'Excentricidad Bomba 1A': datos.excentricidad_bomba,
            'Flujo de Agua Alimentación Domo AP': datos.flujo_agua_domo_ap,
            'Flujo de Agua Alimentación Domo MP': datos.flujo_agua_domo_mp,
            'Flujo de Agua Atemperación Recalentador': datos.flujo_agua_recalentador,
            'Posición válvula recirculación BAA': datos.posicion_valvula_recirc,
            'Presión Agua Alimentación Economizador MP': datos.presion_agua_mp,
            'Presión succión BAA': datos.presion_succion_baa,
            'Temperatura Estator Motor Bomba AA': datos.temperatura_estator,
            'Flujo de Salida 12FPMFC': datos.flujo_salida_12fpmfc
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
        nueva_prediccion = PrediccionBombaA(
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
        logger.error(f"Error al realizar la predicción: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar la predicción: {str(e)}"
        )


@router.get(
    "/predicciones-bomba-a",
    response_model=List[PrediccionBombaResponse],
    summary="Historico de predicciones - Bomba A",
    description="""
Obtiene el historico de las ultimas predicciones de falla realizadas para la Bomba A.

## Parametros
- `limite`: Cantidad de registros a devolver (1-100, default: 40)

## Respuesta
Lista ordenada cronologicamente (mas antiguos primero) con:
- `id`: Identificador unico de la prediccion
- `valor_prediccion`: Porcentaje de probabilidad de falla
- `hora_ejecucion`: Hora en que se realizo la prediccion
- `dia_ejecucion`: Fecha de la prediccion

## Uso
Ideal para graficar la evolucion de la probabilidad de falla en el tiempo.
    """,
    response_description="Lista de predicciones historicas de la Bomba A"
)
async def obtener_predicciones_bomba(
    db: Session = Depends(get_db),
    limite: int = Query(40, description="Numero de registros a devolver (max 100)", le=100, ge=1)
):
    try:
        # Consulta directa con ordenamiento y límite
        predicciones = db.query(PrediccionBombaA)\
                        .order_by(PrediccionBombaA.id.desc())\
                        .limit(limite)\
                        .all()
        predicciones = list(reversed(predicciones))  # Ahora los más antiguos primero
        logger.info(f"Registros encontrados: {len(predicciones)}")
        return predicciones
        
    except Exception as e:
        logger.error(f"Error al obtener predicciones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/prediccion_corriente",
    summary="Detectar anomalía - Corriente del motor",
    description="""
Analiza el valor de corriente eléctrica del motor de la Bomba A para detectar anomalías.

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

@router.post(
    "/prediccion_salida-agua",
    summary="Detectar anomalía - Salida de agua",
    description="""
Analiza el flujo/temperatura de salida de agua de la Bomba A para detectar anomalías en el caudal de descarga.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico del sensor de salida de agua

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
async def predecir_salida(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="salida_bomba", umbral_key="prediccion_salida-agua", model_class=SensorSalidaAgua)

@router.post(
    "/prediccion_presion-agua",
    summary="Detectar anomalía - Presión de agua AP",
    description="""
Analiza la presión de agua de alimentación en el economizador de alta presión de la Bomba A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de presión (PSI o Bar)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Valores anormales pueden indicar problemas en el sistema hidráulico, obstrucciones o fugas.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_presion(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua", umbral_key="prediccion_presion-agua", model_class=SensorPresionAgua)

@router.post(
    "/prediccion_mw-brutos-gas",
    summary="Detectar anomalía - MW brutos generación gas",
    description="""
Analiza la generación de potencia bruta por consumo de gas para detectar ineficiencias energéticas.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de MW brutos generados

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Anomalías pueden indicar problemas en la conversión energética o ineficiencias en la combustión.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_mw_gas(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="mw_brutos_gas", umbral_key="prediccion_mw-brutos-gas", model_class=SensorMw_brutos_generacion_gas)

@router.post(
    "/prediccion_temperatura-ambiental",
    summary="Detectar anomalía - Temperatura ambiental",
    description="""
Analiza la temperatura ambiente en la zona de operación de la Bomba A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Valores extremos pueden afectar el rendimiento de los equipos y la refrigeración.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_ambiental", umbral_key="prediccion_temperatura-ambiental", model_class=SensorTemperatura_Ambiental)

@router.post(
    "/prediccion_temp-descanso-bomba-1a",
    summary="Detectar anomalía - Temp. descanso bomba",
    description="""
Analiza la temperatura en los rodamientos/descansos internos de la Bomba 1A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Temperaturas elevadas indican posible desgaste en rodamientos o falta de lubricación.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temp_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_bomba_1a", umbral_key="prediccion_temp-descanso-bomba-1a", model_class=SensorTemperatura_descanso_interno_bomba_1a)

@router.post(
    "/prediccion_temp-empuje-bomba-1a",
    summary="Detectar anomalía - Temp. empuje bomba",
    description="""
Analiza la temperatura en el cojinete de empuje de la Bomba 1A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Temperaturas anormales pueden indicar problemas de carga axial o fallas en el sistema de refrigeración.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temp_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_empuje_bomba_1a", umbral_key="prediccion_temp-empuje-bomba-1a", model_class=SensorTemperatura_descanso_interna_empuje_bomba_1aa)

@router.post(
    "/prediccion_temp-motor-bomba-1a",
    summary="Detectar anomalía - Temp. motor bomba",
    description="""
Analiza la temperatura de operación del motor de la Bomba 1A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Sobrecalentamiento puede indicar sobrecarga del motor o falla en el sistema de ventilación.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temp_motor(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_motor_bomba_1a", umbral_key="prediccion_temp-motor-bomba-1a", model_class=SensorTemperatura_descanso_interna_motor_bomba_1a)

@router.post(
    "/prediccion_vibracion-axial",
    summary="Detectar anomalía - Vibración axial",
    description="""
Analiza el nivel de vibración axial en el descanso de empuje de la Bomba A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de vibración (mm/s o g)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Vibraciones excesivas indican posible desbalanceo, desalineación o desgaste en componentes rotativos.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_vibracion(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_axial_empuje", umbral_key="prediccion_vibracion-axial", model_class=SensorVibracion_axial_descanso)

@router.post(
    "/prediccion_voltaje-barra",
    summary="Detectar anomalía - Voltaje barra 6.6KV",
    description="""
Analiza el nivel de voltaje en las barras de distribución de 6.6KV.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de voltaje (KV)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Fluctuaciones de voltaje pueden dañar equipos eléctricos sensibles y afectar la operación de motores.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_voltaje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="voltaje_barra", umbral_key="prediccion_voltaje-barra", model_class=SensorVoltaje_barra)

# Rutas POST para los nuevos sensores
@router.post(
    "/prediccion_excentricidad-bomba",
    summary="Detectar anomalía - Excentricidad bomba",
    description="""
Analiza la excentricidad del rotor de la Bomba 1A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de excentricidad (mm o mils)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Valores elevados de excentricidad indican posible desalineación, desgaste en cojinetes o problemas en el eje.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_excentricidad_bomba(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="excentricidad_bomba", umbral_key="prediccion_excentricidad-bomba", model_class=SensorExcentricidadBomba)

@router.post(
    "/prediccion_flujo-agua-domo-ap",
    summary="Detectar anomalía - Flujo agua domo AP",
    description="""
Analiza el flujo de agua de alimentación al domo de alta presión del HRSG.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Variaciones en el flujo pueden afectar la generación de vapor y el balance térmico del sistema.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_domo_ap(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_ap", umbral_key="prediccion_flujo-agua-domo-ap", model_class=SensorFlujoAguaDomoAP)

@router.post(
    "/prediccion_flujo-agua-domo-mp",
    summary="Detectar anomalía - Flujo agua domo MP",
    description="""
Analiza el flujo de agua de alimentación al domo de media presión del HRSG.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Este flujo es esencial para el balance térmico del HRSG. Anomalías pueden afectar la eficiencia del ciclo combinado.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_domo_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_mp", umbral_key="prediccion_flujo-agua-domo-mp", model_class=SensorFlujoAguaDomoMP)

@router.post(
    "/prediccion_flujo-agua-recalentador",
    summary="Detectar anomalía - Flujo agua recalentador",
    description="""
Analiza el flujo de agua para atemperación del recalentador.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Este flujo controla la temperatura del vapor recalentado. Anomalías pueden causar daños térmicos a la turbina.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_recalentador(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_recalentador", umbral_key="prediccion_flujo-agua-recalentador", model_class=SensorFlujoAguaRecalentador)

@router.post(
    "/prediccion_flujo-agua-vapor-alta",
    summary="Detectar anomalía - Flujo agua vapor alta",
    description="""
Analiza el flujo de agua para atemperación de vapor de alta presión.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo (m³/h o GPM)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Este flujo protege la turbina de temperaturas excesivas. Anomalías pueden causar daños severos al equipo.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_agua_vapor_alta(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_vapor_alta", umbral_key="prediccion_flujo-agua-vapor-alta", model_class=SensorFlujoAguaVaporAlta)

@router.post(
    "/prediccion_posicion-valvula-recirc",
    summary="Detectar anomalía - Posición válvula recirculación",
    description="""
Analiza la posición de la válvula de recirculación de la Bomba A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de posición (% apertura)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Posiciones anómalas de la válvula pueden causar cavitación en la bomba y daño a los impulsores.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_posicion_valvula_recirc(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="posicion_valvula_recirc", umbral_key="prediccion_posicion-valvula-recirc", model_class=SensorPosicionValvulaRecirc)

@router.post(
    "/prediccion_presion-agua-mp",
    summary="Detectar anomalía - Presión agua MP",
    description="""
Analiza la presión de agua de alimentación en el economizador de media presión.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de presión (PSI o Bar)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Anomalías pueden indicar restricciones en el sistema, fugas o problemas con la bomba.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_presion_agua_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua_mp", umbral_key="prediccion_presion-agua-mp", model_class=SensorPresionAguaMP)

@router.post(
    "/prediccion_presion-succion-baa",
    summary="Detectar anomalía - Presión succión BAA",
    description="""
Analiza la presión en la succión de la bomba de agua de alimentación.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de presión (PSI o Bar)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Baja presión de succión puede causar cavitación severa, daño a los impulsores y falla de la bomba.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_presion_succion_baa(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_succion_baa", umbral_key="prediccion_presion-succion-baa", model_class=SensorPresionSuccionBAA)

@router.post(
    "/prediccion_temperatura-estator",
    summary="Detectar anomalía - Temperatura estator",
    description="""
Analiza la temperatura del estator del motor de la Bomba A.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de temperatura (°C)

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Sobrecalentamiento del estator indica posibles problemas de aislamiento, sobrecarga o falla en el sistema de refrigeración.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_temperatura_estator(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_estator", umbral_key="prediccion_temperatura-estator", model_class=SensorTemperaturaEstator)

@router.post(
    "/prediccion_flujo-salida-12fpmfc",
    summary="Detectar anomalía - Flujo salida 12FPMFC",
    description="""
Analiza el flujo de salida medido por el sensor 12FPMFC.

**Modelo:** Isolation Forest (detección de outliers)

**Entrada:**
- `valor_sensor`: Valor numérico de flujo

**Sistema de alertas:**
Se evalúan las anomalías en una ventana de 8 horas:
- **AVISO**: 3+ anomalías
- **ALERTA**: 8+ anomalías
- **CRÍTICA**: 15+ anomalías

**Indicadores de falla:**
Variaciones significativas indican cambios en la operación del sistema que pueden requerir atención.

**Respuesta:**
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `alerta`: Información de alerta si se supera algún umbral
    """,
    response_description="Resultado de la predicción con clasificación y estado de alertas"
)
async def predecir_flujo_salida_12fpmfc(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_salida_12fpmfc", umbral_key="prediccion_flujo-salida-12fpmfc", model_class=SensorFlujoSalida12FPMFC)




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

# Rutas GET para consulta de datos historicos
@router.get(
    "/corriente",
    summary="Histórico - Corriente del motor",
    description="""
Obtiene registros históricos del sensor de corriente eléctrica del motor de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio del rango (ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `termino`: Fecha/hora de fin del rango (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando el modelo Isolation Forest.

**Respuesta:**
Lista de registros con:
- `valor_sensor`: Valor de corriente medido
- `clasificacion`: 1 (normal) o -1 (anomalía)
- `tiempo_ejecucion`: Timestamp del registro
    """,
    response_description="Lista de registros históricos del sensor de corriente"
)
async def get_sensores_corriente(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601): YYYY-MM-DDTHH:MM:SS"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601): YYYY-MM-DDTHH:MM:SS"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorCorriente, "corriente_motor", DEFAULT_SENSORES_CORRIENTE, inicio, termino, limite)

@router.get(
    "/salida-agua",
    summary="Histórico - Salida de agua",
    description="""
Obtiene registros históricos del sensor de salida de agua de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos del sensor de salida de agua"
)
async def get_sensores_salida_agua(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorSalidaAgua, "salida_bomba", DEFAULT_SENSORES_SALIDA_AGUA, inicio, termino, limite)

@router.get(
    "/presion-agua",
    summary="Histórico - Presión de agua AP",
    description="""
Obtiene registros históricos del sensor de presión de agua de alta presión de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
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

@router.get(
    "/generacion-gas",
    summary="Histórico - MW brutos gas",
    description="""
Obtiene registros históricos del sensor de generación de potencia bruta por consumo de gas.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de generación de MW"
)
async def get_sensores_generacion_gas(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorMw_brutos_generacion_gas, "mw_brutos_gas", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/temperatura-ambiental",
    summary="Histórico - Temperatura ambiental",
    description="""
Obtiene registros históricos del sensor de temperatura ambiente en la zona de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de temperatura ambiental"
)
async def get_sensores_temperatura_ambiental(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_Ambiental, "temperatura_ambiental", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/temperatura-interna-empuje",
    summary="Histórico - Temp. empuje bomba",
    description="""
Obtiene registros históricos del sensor de temperatura del cojinete de empuje de la Bomba 1A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de temperatura del empuje"
)
async def get_sensores_temp_interna_empuje(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_empuje_bomba_1aa, "temp_descanso_empuje_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/temperatura-descanso-motor",
    summary="Histórico - Temp. motor bomba",
    description="""
Obtiene registros históricos del sensor de temperatura del motor de la Bomba 1A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de temperatura del motor"
)
async def get_sensores_temp_descanso_motor(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_motor_bomba_1a, "temp_descanso_motor_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/temperatura-descanso-bomba",
    summary="Histórico - Temp. descanso bomba",
    description="""
Obtiene registros históricos del sensor de temperatura de los rodamientos/descansos de la Bomba 1A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de temperatura del descanso"
)
async def get_sensores_temp_descanso_bomba(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interno_bomba_1a, "temp_descanso_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/vibracion-axial",
    summary="Histórico - Vibración axial",
    description="""
Obtiene registros históricos del sensor de vibración axial del descanso de empuje de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de vibración axial"
)
async def get_sensores_vibracion_axial(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracion_axial_descanso, "vibracion_axial_empuje", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/voltaje-barra",
    summary="Histórico - Voltaje barra 6.6KV",
    description="""
Obtiene registros históricos del sensor de voltaje de las barras de distribución 6.6KV.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de voltaje"
)
async def get_sensores_voltaje_barra(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVoltaje_barra, "voltaje_barra", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

# Rutas GET para los nuevos sensores
@router.get(
    "/excentricidad-bomba",
    summary="Histórico - Excentricidad bomba",
    description="""
Obtiene registros históricos del sensor de excentricidad del rotor de la Bomba 1A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de excentricidad"
)
async def get_sensores_excentricidad_bomba(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorExcentricidadBomba, "excentricidad_bomba", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/flujo-agua-domo-ap",
    summary="Histórico - Flujo agua domo AP",
    description="""
Obtiene registros históricos del flujo de agua al domo de alta presión del HRSG.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de flujo domo AP"
)
async def get_sensores_flujo_agua_domo_ap(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoAP, "flujo_agua_domo_ap", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/flujo-agua-domo-mp",
    summary="Histórico - Flujo agua domo MP",
    description="""
Obtiene registros históricos del flujo de agua al domo de media presión del HRSG.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de flujo domo MP"
)
async def get_sensores_flujo_agua_domo_mp(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoMP, "flujo_agua_domo_mp", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/flujo-agua-recalentador",
    summary="Histórico - Flujo agua recalentador",
    description="""
Obtiene registros históricos del flujo de agua de atemperación del recalentador.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de flujo recalentador"
)
async def get_sensores_flujo_agua_recalentador(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaRecalentador, "flujo_agua_recalentador", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/flujo-agua-vapor-alta",
    summary="Histórico - Flujo agua vapor alta",
    description="""
Obtiene registros históricos del flujo de agua de atemperación de vapor de alta presión.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de flujo vapor alta"
)
async def get_sensores_flujo_agua_vapor_alta(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaVaporAlta, "flujo_agua_vapor_alta", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/posicion-valvula-recirc",
    summary="Histórico - Posición válvula recirculación",
    description="""
Obtiene registros históricos de la posición de la válvula de recirculación de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de posición de válvula"
)
async def get_sensores_posicion_valvula_recirc(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPosicionValvulaRecirc, "posicion_valvula_recirc", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/presion-agua-mp",
    summary="Histórico - Presión agua MP",
    description="""
Obtiene registros históricos del sensor de presión de agua de media presión.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de presión MP"
)
async def get_sensores_presion_agua_mp(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAguaMP, "presion_agua_mp", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/presion-succion-baa",
    summary="Histórico - Presión succión BAA",
    description="""
Obtiene registros históricos del sensor de presión en la succión de la bomba de agua de alimentación.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de presión succión"
)
async def get_sensores_presion_succion_baa(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionSuccionBAA, "presion_succion_baa", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/temperatura-estator",
    summary="Histórico - Temperatura estator",
    description="""
Obtiene registros históricos del sensor de temperatura del estator del motor de la Bomba A.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de temperatura estator"
)
async def get_sensores_temperatura_estator(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaEstator, "temperatura_estator", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)

@router.get(
    "/flujo-salida-12fpmfc",
    summary="Histórico - Flujo salida 12FPMFC",
    description="""
Obtiene registros históricos del medidor de flujo 12FPMFC.

**Parámetros de filtrado:**
- `inicio`: Fecha/hora de inicio (ISO 8601)
- `termino`: Fecha/hora de fin (ISO 8601)
- `limite`: Cantidad máxima de registros (10-500, default: 40)

**Clasificación automática:**
Los registros sin clasificación se clasifican automáticamente usando ML.

**Respuesta:**
Lista de registros con valor, clasificación (1=normal, -1=anomalía) y timestamps.
    """,
    response_description="Lista de registros históricos de flujo 12FPMFC"
)
async def get_sensores_flujo_salida_12fpmfc(
    inicio: Optional[str] = Query(None, description="Fecha inicio (ISO 8601)"),
    termino: Optional[str] = Query(None, description="Fecha fin (ISO 8601)"),
    limite: int = Query(40, description="Cantidad de registros (10-500)", ge=10, le=500),
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoSalida12FPMFC, "flujo_salida_12fpmfc", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino, limite)


# Obtener los rangos de tiempo de cada tabla 

from datetime import datetime

def _get_range(db: Session, model):
    """
    Devuelve la fecha mínima y máxima de tiempo_ejecucion
    para la tabla del modelo pasado, en el formato 'YYYY-MM-DD HH:MM:SS.sss'.
    """
    minimo, maximo = db.query(
        func.min(model.tiempo_ejecucion),
        func.max(model.tiempo_ejecucion)
    ).one()

    # Si no hay datos, devolvemos None
    def format_date(date):
        return date.strftime('%Y-%m-%d %H:%M:%S.000') if date else None

    return {
        "inicio": format_date(minimo),
        "termino": format_date(maximo)
    }


@router.get(
    "/corriente/rango",
    summary="Rango de fechas - Corriente",
    description="""
Obtiene la fecha mínima y máxima de los datos disponibles del sensor de corriente.

**Uso:**
Útil para configurar filtros de fecha en consultas históricas y conocer el rango temporal de datos disponibles.

**Respuesta:**
- `inicio`: Timestamp del primer registro disponible
- `termino`: Timestamp del último registro disponible
    """,
    response_description="Rango de fechas disponibles"
)
async def rango_corriente(db: Session = Depends(get_db)):
    return _get_range(db, SensorCorriente)

@router.get(
    "/salida-agua/rango",
    summary="Rango de fechas - Salida agua",
    description="""
Obtiene la fecha mínima y máxima de los datos disponibles del sensor de salida de agua.

**Uso:**
Útil para configurar filtros de fecha en consultas históricas.

**Respuesta:**
- `inicio`: Timestamp del primer registro disponible
- `termino`: Timestamp del último registro disponible
    """,
    response_description="Rango de fechas disponibles"
)
async def rango_salida_agua(db: Session = Depends(get_db)):
    return _get_range(db, SensorSalidaAgua)


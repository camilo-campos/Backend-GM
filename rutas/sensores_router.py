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
import time
import logging
from functools import lru_cache

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    'prediccion_corriente': {
        "umbral_minimo": 101,  # 50% de 202
        "umbral_alerta": 162,   # 80% de 202
        "umbral_critica": 202,
    },
    'prediccion_salida-agua': {
        "umbral_minimo": 49,   # 50% de 98
        "umbral_alerta": 78,  # 80% de 98
        "umbral_critica": 98,
    },
    'prediccion_presion-agua': {
        "umbral_minimo": 118,  # 50% de 235
        "umbral_alerta": 188,  # 80% de 235
        "umbral_critica": 235,
    },
    'prediccion_mw-brutos-gas': {
        "umbral_minimo": 56,  # 50% de 112
        "umbral_alerta": 90,  # 80% de 112
        "umbral_critica": 112,
    },
    'prediccion_temperatura-ambiental': {
        "umbral_minimo": 14,   # 50% de 28
        "umbral_alerta": 22,  # 80% de 28
        "umbral_critica": 28,
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
        "umbral_minimo": 18,   # 50% de 36
        "umbral_alerta": 29,  # 80% de 36
        "umbral_critica": 36,
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
        # Predecir si es anomalía o no
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
            
            # Guardar la clasificación anterior para detectar cambios
            clasificacion_anterior = lectura.clasificacion
            # Guardar el contador anterior para poder decrementarlo si es necesario
            contador_anterior = lectura.contador_anomalias if hasattr(lectura, 'contador_anomalias') else 0

            # Actualizar la clasificación actual y tiempo de ejecución
            lectura.clasificacion = clase
            lectura.tiempo_ejecucion = datetime.now(timezone.utc)
            
            # Hacer el primer commit para guardar la clasificación y tiempo
            try:
                db.commit()
            except Exception as commit_error:
                logger.error(f"Error al hacer commit de la clasificación: {str(commit_error)}")
                db.rollback()
                
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
            clasificacion_anterior = None
            contador_anterior = 0
            
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
    
    # Hacer commit para guardar el contador actualizado
    db.commit()
    
    # Si es anomalía, evaluamos niveles de alerta basados en el conteo de anomalías
    if clase == -1 and lectura.contador_anomalias > 0:
        # Usamos el contador actual para determinar la alerta
        alerta_info = determinar_alerta(lectura.contador_anomalias, umbral_key)
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
                mensaje = f"{alerta_info['nivel']}: {alerta_info['nombre_sensor']} - {alerta_info['conteo_anomalias']} anomalías en {VENTANA_HORAS} horas ({alerta_info['porcentaje_umbral']}% del umbral crítico)\n"
                mensaje += f"Descripción: {alerta_info['descripcion_sensor']}\n"
                mensaje += f"Acción recomendada: {alerta_info['accion_recomendada']}"
                
                alerta = Alerta(
                    sensor_id=sensor.id_sensor,
                    tipo_sensor=umbral_key,
                    descripcion=mensaje,
                    contador_anomalias=lectura.contador_anomalias  # Guardar el contador actualizado
                )
                db.add(alerta)
                db.commit()

    return {
        "id_sensor": sensor.id_sensor,
        "valor": sensor.valor,
        "prediccion": clase,
        "descripcion": descripcion,
        "contador_anomalias": anomalias_ventana
    }


# ————— Rutas Post —————

@router.post("/predecir-bomba", response_model=PrediccionBombaOutput)
async def predecir_bomba(
    datos: PrediccionBombaInput,
    db: Session = Depends(get_db)
):
    """
    Realiza una predicción utilizando el modelo Random Forest para la bomba.
    
    Parámetros:
    - datos: Objeto con los valores de entrada para el modelo
    
    Retorna:
    - prediccion: Valor predicho por el modelo
    - status: Estado de la operación
    """
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
        prediccion = model.predict(input_data)
        # Obtener probabilidades para cada clase
        probabilidades = model.predict_proba(input_data)
        
        # Seleccionar la probabilidad correspondiente a la clase predicha
        # Si es clasificación binaria (0,1), tomamos el índice correspondiente a la clase predicha
        clase_predicha = int(prediccion[0])
        # Asumiendo que predict_proba devuelve probabilidades para todas las clases en orden
        # Para clasificación binaria, [0] es prob de clase 0, [1] es prob de clase 1
        prob_clase_predicha = float(probabilidades[0][clase_predicha])
        
        # Convertir la probabilidad a porcentaje con dos decimales
        porcentaje_prediccion = round(prob_clase_predicha * 100, 2)
        
        logger.info(f"Predicción realizada: {prediccion[0]} con probabilidad: {porcentaje_prediccion:.2f}%")
        
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


@router.get("/predicciones-bomba-a", response_model=List[PrediccionBombaResponse])
async def obtener_predicciones_bomba(
    db: Session = Depends(get_db),
    limite: int = Query(40, description="Número de registros a devolver (máx 100)", le=100, ge=1)
):
    """
    Obtiene las últimas predicciones de la bomba.
    """
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


@router.post("/prediccion_corriente")
async def predecir_corriente(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="corriente_motor", umbral_key="prediccion_corriente", model_class=SensorCorriente)

@router.post("/prediccion_salida-agua")
async def predecir_salida(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="salida_bomba",    umbral_key="prediccion_salida-agua",    model_class=SensorSalidaAgua)

@router.post("/prediccion_presion-agua")
async def predecir_presion(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua",    umbral_key="prediccion_presion-agua", model_class=SensorPresionAgua)

@router.post("/prediccion_mw-brutos-gas")
async def predecir_mw_gas(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="mw_brutos_gas", umbral_key="prediccion_mw-brutos-gas", model_class=SensorMw_brutos_generacion_gas)

@router.post("/prediccion_temperatura-ambiental")
async def predecir_temperatura_ambiental(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_ambiental", umbral_key="prediccion_temperatura-ambiental", model_class=SensorTemperatura_Ambiental)

@router.post("/prediccion_temp-descanso-bomba-1a")
async def predecir_temp_descanso(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_bomba_1a", umbral_key="prediccion_temp-descanso-bomba-1a", model_class=SensorTemperatura_descanso_interno_bomba_1a)

@router.post("/prediccion_temp-empuje-bomba-1a")
async def predecir_temp_empuje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_empuje_bomba_1a", umbral_key="prediccion_temp-empuje-bomba-1a", model_class=SensorTemperatura_descanso_interna_empuje_bomba_1aa)

@router.post("/prediccion_temp-motor-bomba-1a")
async def predecir_temp_motor(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temp_descanso_motor_bomba_1a", umbral_key="prediccion_temp-motor-bomba-1a", model_class=SensorTemperatura_descanso_interna_motor_bomba_1a)

@router.post("/prediccion_vibracion-axial")
async def predecir_vibracion(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="vibracion_axial_empuje", umbral_key="prediccion_vibracion-axial", model_class=SensorVibracion_axial_descanso)

@router.post("/prediccion_voltaje-barra")
async def predecir_voltaje(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="voltaje_barra", umbral_key="prediccion_voltaje-barra", model_class=SensorVoltaje_barra)

# Rutas POST para los nuevos sensores
@router.post("/prediccion_excentricidad-bomba")
async def predecir_excentricidad_bomba(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="excentricidad_bomba", umbral_key="prediccion_excentricidad-bomba", model_class=SensorExcentricidadBomba)

@router.post("/prediccion_flujo-agua-domo-ap")
async def predecir_flujo_agua_domo_ap(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_ap", umbral_key="prediccion_flujo-agua-domo-ap", model_class=SensorFlujoAguaDomoAP)

@router.post("/prediccion_flujo-agua-domo-mp")
async def predecir_flujo_agua_domo_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_domo_mp", umbral_key="prediccion_flujo-agua-domo-mp", model_class=SensorFlujoAguaDomoMP)

@router.post("/prediccion_flujo-agua-recalentador")
async def predecir_flujo_agua_recalentador(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_recalentador", umbral_key="prediccion_flujo-agua-recalentador", model_class=SensorFlujoAguaRecalentador)

@router.post("/prediccion_flujo-agua-vapor-alta")
async def predecir_flujo_agua_vapor_alta(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="flujo_agua_vapor_alta", umbral_key="prediccion_flujo-agua-vapor-alta", model_class=SensorFlujoAguaVaporAlta)

@router.post("/prediccion_posicion-valvula-recirc")
async def predecir_posicion_valvula_recirc(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="posicion_valvula_recirc", umbral_key="prediccion_posicion-valvula-recirc", model_class=SensorPosicionValvulaRecirc)

@router.post("/prediccion_presion-agua-mp")
async def predecir_presion_agua_mp(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_agua_mp", umbral_key="prediccion_presion-agua-mp", model_class=SensorPresionAguaMP)

@router.post("/prediccion_presion-succion-baa")
async def predecir_presion_succion_baa(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="presion_succion_baa", umbral_key="prediccion_presion-succion-baa", model_class=SensorPresionSuccionBAA)

@router.post("/prediccion_temperatura-estator")
async def predecir_temperatura_estator(sensor: SensorInput, db: Session = Depends(get_db)):
    return procesar(sensor, db, modelo_key="temperatura_estator", umbral_key="prediccion_temperatura-estator", model_class=SensorTemperaturaEstator)

@router.post("/prediccion_flujo-salida-12fpmfc")
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

# Rutas
@router.get("/corriente")
async def get_sensores_corriente(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorCorriente, "corriente_motor", DEFAULT_SENSORES_CORRIENTE, inicio, termino)

@router.get("/salida-agua")
async def get_sensores_salida_agua(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorSalidaAgua, "salida_bomba", DEFAULT_SENSORES_SALIDA_AGUA, inicio, termino)

@router.get("/presion-agua")
async def get_sensores_presion_agua(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAgua, "presion_agua", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/generacion-gas")
async def get_sensores_generacion_gas(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorMw_brutos_generacion_gas, "mw_brutos_gas", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/temperatura-ambiental")
async def get_sensores_temperatura_ambiental(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_Ambiental, "temperatura_ambiental", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/temperatura-interna-empuje")
async def get_sensores_temp_interna_empuje(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_empuje_bomba_1aa, "temp_descanso_empuje_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/temperatura-descanso-motor")
async def get_sensores_temp_descanso_motor(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interna_motor_bomba_1a, "temp_descanso_motor_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/temperatura-descanso-bomba")
async def get_sensores_temp_descanso_bomba(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperatura_descanso_interno_bomba_1a, "temp_descanso_bomba_1a", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/vibracion-axial")
async def get_sensores_vibracion_axial(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVibracion_axial_descanso, "vibracion_axial_empuje", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/voltaje-barra")
async def get_sensores_voltaje_barra(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorVoltaje_barra, "voltaje_barra", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

# Rutas GET para los nuevos sensores
@router.get("/excentricidad-bomba")
async def get_sensores_excentricidad_bomba(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorExcentricidadBomba, "excentricidad_bomba", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/flujo-agua-domo-ap")
async def get_sensores_flujo_agua_domo_ap(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoAP, "flujo_agua_domo_ap", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/flujo-agua-domo-mp")
async def get_sensores_flujo_agua_domo_mp(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaDomoMP, "flujo_agua_domo_mp", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/flujo-agua-recalentador")
async def get_sensores_flujo_agua_recalentador(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaRecalentador, "flujo_agua_recalentador", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/flujo-agua-vapor-alta")
async def get_sensores_flujo_agua_vapor_alta(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoAguaVaporAlta, "flujo_agua_vapor_alta", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/posicion-valvula-recirc")
async def get_sensores_posicion_valvula_recirc(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPosicionValvulaRecirc, "posicion_valvula_recirc", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/presion-agua-mp")
async def get_sensores_presion_agua_mp(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionAguaMP, "presion_agua_mp", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/presion-succion-baa")
async def get_sensores_presion_succion_baa(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorPresionSuccionBAA, "presion_succion_baa", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/temperatura-estator")
async def get_sensores_temperatura_estator(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorTemperaturaEstator, "temperatura_estator", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)

@router.get("/flujo-salida-12fpmfc")
async def get_sensores_flujo_salida_12fpmfc(
    inicio: Optional[str] = Query(None), 
    termino: Optional[str] = Query(None), 
    db: Session = Depends(get_db)
):
    return await _get_and_classify(db, SensorFlujoSalida12FPMFC, "flujo_salida_12fpmfc", DEFAULT_SENSORES_PRESION_AGUA, inicio, termino)


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


@router.get("/corriente/rango")
async def rango_corriente(db: Session = Depends(get_db)):
    return _get_range(db, SensorCorriente)

@router.get("/salida-agua/rango")
async def rango_salida_agua(db: Session = Depends(get_db)):
    return _get_range(db, SensorSalidaAgua)


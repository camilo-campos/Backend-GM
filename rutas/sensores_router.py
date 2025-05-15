from fastapi import APIRouter, Depends , HTTPException
from datetime import datetime, timedelta
from datetime import datetime, timezone
import numpy as np
from typing import Optional
from fastapi import Query
from datetime import datetime
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
    "corriente_motor": "model_Corriente Motor Bomba Agua Alimentacion BFWP A (A).pkl",
    "mw_brutos_gas": "model_MW Brutos de Generación Total Gas (MW).pkl",
    "presion_agua": "model_Presión Agua Alimentación AP (barg).pkl",
    "salida_bomba": "model_Salida de Bomba de Alta Presión.pkl",
    "temperatura_ambiental": "model_Temperatura Ambiental (°C).pkl",
    "temp_descanso_bomba_1a": "model_Temperatura Descanso Interno Bomba 1A (°C).pkl",
    "temp_descanso_empuje_bomba_1a": "model_Temperatura Descanso Interno Empuje Bomba 1A (°C).pkl",
    "temp_descanso_motor_bomba_1a": "model_Temperatura Descanso Interno Motor Bomba 1A (°C).pkl",
    "vibracion_axial_empuje": "model_Vibración Axial Descanso Emp Bomba 1A (ms).pkl",
    "voltaje_barra": "model_Voltaje Barra 6,6KV (V).pkl",
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
    """
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(hours=VENTANA_HORAS)
    return db.query(func.count(model_class.id)) \
        .filter(model_class.clasificacion == -1) \
        .filter(model_class.id == sensor_id) \
        .filter(model_class.tiempo_ejecucion.between(inicio, ahora)) \
        .scalar()


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
    clase = predecir_sensores_np(modelos[modelo_key], sensor.valor)
    descripcion = "Normal" if clase == 1 else "Anomalía"

    # Actualiza lectura
    lectura = db.query(model_class).get(sensor.id_sensor)
    if not lectura:
        raise HTTPException(404, "Lectura no encontrada")

    # Ajuste de contador local en la tabla
    # Asegúrate de que el modelo SQL tenga un campo 'contador_anomalias' (Integer, default=0)
    if clase == -1:
        lectura.contador_anomalias = lectura.contador_anomalias + 1
        print(f"[{umbral_key}] Anomalía detectada. Contador actualizado: {lectura.contador_anomalias}")
    else:
        lectura.contador_anomalias = max(lectura.contador_anomalias - 1, 0)
        print(f"[{umbral_key}] Valor normal. Contador actualizado: {lectura.contador_anomalias}")


    lectura.clasificacion = clase
    lectura.tiempo_ejecucion = datetime.now(timezone.utc)
    db.commit()

        # Si es anomalía, evaluamos niveles de alerta en base al contador almacenado
    if clase == -1:
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
                    descripcion=mensaje
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

@router.get("/presion-agua/rango")
async def rango_presion_agua(db: Session = Depends(get_db)):
    return _get_range(db, SensorPresionAgua)

@router.get("/generacion-gas/rango")
async def rango_generacion_gas(db: Session = Depends(get_db)):
    return _get_range(db, SensorMw_brutos_generacion_gas)

@router.get("/temperatura-ambiental/rango")
async def rango_temperatura_ambiental(db: Session = Depends(get_db)):
    return _get_range(db, SensorTemperatura_Ambiental)

@router.get("/temperatura-interna-empuje/rango")
async def rango_temp_interna_empuje(db: Session = Depends(get_db)):
    return _get_range(db, SensorTemperatura_descanso_interna_empuje_bomba_1aa)

@router.get("/temperatura-descanso-motor/rango")
async def rango_temp_descanso_motor(db: Session = Depends(get_db)):
    return _get_range(db, SensorTemperatura_descanso_interna_motor_bomba_1a)

@router.get("/temperatura-descanso-bomba/rango")
async def rango_temp_descanso_bomba(db: Session = Depends(get_db)):
    return _get_range(db, SensorTemperatura_descanso_interno_bomba_1a)

@router.get("/vibracion-axial/rango")
async def rango_vibracion_axial(db: Session = Depends(get_db)):
    return _get_range(db, SensorVibracion_axial_descanso)

@router.get("/voltaje-barra/rango")
async def rango_voltaje_barra(db: Session = Depends(get_db)):
    return _get_range(db, SensorVoltaje_barra)

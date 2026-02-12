from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from modelos.database import get_db
from modelos.modelos import (
    Alerta as AlertaA,
    SensorCorriente, SensorSalidaAgua, SensorPresionAgua,
    SensorMw_brutos_generacion_gas, SensorTemperatura_Ambiental,
    SensorTemperatura_descanso_interna_empuje_bomba_1aa,
    SensorTemperatura_descanso_interna_motor_bomba_1a,
    SensorTemperatura_descanso_interno_bomba_1a,
    SensorVibracion_axial_descanso, SensorVoltaje_barra,
    SensorExcentricidadBomba, SensorFlujoAguaDomoAP, SensorFlujoAguaDomoMP,
    SensorFlujoAguaRecalentador, SensorFlujoAguaVaporAlta,
    SensorPosicionValvulaRecirc, SensorPresionAguaMP, SensorPresionSuccionBAA,
    SensorTemperaturaEstator, SensorFlujoSalida12FPMFC
)
from modelos_b.modelos_b import (
    Alerta as AlertaB,
    SensorCorriente as SensorCorrienteB,
    SensorExcentricidadBomba as SensorExcentricidadBombaB,
    SensorFlujoDescarga as SensorFlujoDescargaB,
    SensorFlujoAguaDomoAP as SensorFlujoAguaDomoAPB,
    SensorFlujoAguaDomoMP as SensorFlujoAguaDomoMPB,
    SensorFlujoAguaRecalentador as SensorFlujoAguaRecalentadorB,
    SensorFlujoAguaVaporAlta as SensorFlujoAguaVaporAltaB,
    SensorPresionAgua as SensorPresionAguaB,
    SensorTemperaturaAmbiental as SensorTemperaturaAmbientalB,
    SensorTemperaturaAguaAlim as SensorTemperaturaAguaAlimB,
    SensorTemperaturaEstator as SensorTemperaturaEstatorB,
    SensorVibracionAxialEmpuje as SensorVibracionAxialEmpujeB,
    SensorVibracionXDescanso as SensorVibracionXDescansoB,
    SensorVibracionYDescanso as SensorVibracionYDescansoB,
    SensorVoltajeBarra as SensorVoltajeBarraB
)


# Mapeo de tipo_sensor a modelo de sensor (Bomba A)
# Los nombres deben coincidir con los umbral_key usados en sensores_router.py
MAPEO_SENSORES_A = {
    "prediccion_corriente": SensorCorriente,
    "prediccion_salida-agua": SensorSalidaAgua,
    "prediccion_presion-agua": SensorPresionAgua,
    "prediccion_mw-brutos": SensorMw_brutos_generacion_gas,
    "prediccion_mw-brutos-gas": SensorMw_brutos_generacion_gas,
    "prediccion_temperatura-ambiental": SensorTemperatura_Ambiental,
    "prediccion_temp-descanso-empuje": SensorTemperatura_descanso_interna_empuje_bomba_1aa,
    "prediccion_temp-descanso-motor": SensorTemperatura_descanso_interna_motor_bomba_1a,
    "prediccion_temp-descanso-interno": SensorTemperatura_descanso_interno_bomba_1a,
    "prediccion_temp-descanso-bomba-1a": SensorTemperatura_descanso_interno_bomba_1a,  # Nombre usado en endpoint
    "prediccion_temp-empuje-bomba-1a": SensorTemperatura_descanso_interna_empuje_bomba_1aa,  # Nombre usado en endpoint
    "prediccion_temp-motor-bomba-1a": SensorTemperatura_descanso_interna_motor_bomba_1a,  # Nombre usado en endpoint
    "prediccion_vibracion-axial": SensorVibracion_axial_descanso,
    "prediccion_voltaje-barra": SensorVoltaje_barra,
    "prediccion_excentricidad": SensorExcentricidadBomba,
    "prediccion_excentricidad-bomba": SensorExcentricidadBomba,
    "prediccion_flujo-domo-ap": SensorFlujoAguaDomoAP,
    "prediccion_flujo-agua-domo-ap": SensorFlujoAguaDomoAP,  # Nombre real del endpoint
    "prediccion_flujo-domo-mp": SensorFlujoAguaDomoMP,
    "prediccion_flujo-agua-domo-mp": SensorFlujoAguaDomoMP,  # Nombre real del endpoint
    "prediccion_flujo-recalentador": SensorFlujoAguaRecalentador,
    "prediccion_flujo-agua-recalentador": SensorFlujoAguaRecalentador,  # Nombre real del endpoint
    "prediccion_flujo-vapor-alta": SensorFlujoAguaVaporAlta,
    "prediccion_flujo-agua-vapor-alta": SensorFlujoAguaVaporAlta,  # Nombre real del endpoint
    "prediccion_posicion-valvula": SensorPosicionValvulaRecirc,
    "prediccion_posicion-valvula-recirc": SensorPosicionValvulaRecirc,  # Nombre real del endpoint
    "prediccion_presion-mp": SensorPresionAguaMP,
    "prediccion_presion-agua-mp": SensorPresionAguaMP,  # Nombre real del endpoint
    "prediccion_presion-succion": SensorPresionSuccionBAA,
    "prediccion_presion-succion-baa": SensorPresionSuccionBAA,  # Nombre real del endpoint
    "prediccion_temp-estator": SensorTemperaturaEstator,
    "prediccion_temperatura-estator": SensorTemperaturaEstator,  # Nombre real del endpoint
    "prediccion_flujo-12fpmfc": SensorFlujoSalida12FPMFC,
    "prediccion_flujo-salida-12fpmfc": SensorFlujoSalida12FPMFC,  # Nombre real del endpoint
}

# Mapeo de tipo_sensor a modelo de sensor (Bomba B)
# Los nombres deben coincidir con los umbral_key usados en sensores_router_B.py
MAPEO_SENSORES_B = {
    "prediccion_corriente": SensorCorrienteB,
    "prediccion_excentricidad_bomba": SensorExcentricidadBombaB,
    "prediccion_flujo_descarga": SensorFlujoDescargaB,
    "prediccion_flujo_agua_domo_ap": SensorFlujoAguaDomoAPB,
    "prediccion_flujo_agua_domo_mp": SensorFlujoAguaDomoMPB,
    "prediccion_flujo_agua_recalentador": SensorFlujoAguaRecalentadorB,
    "prediccion_flujo_agua_vapor_alta": SensorFlujoAguaVaporAltaB,
    "prediccion_presion_agua": SensorPresionAguaB,
    "prediccion_temperatura_ambiental": SensorTemperaturaAmbientalB,
    "prediccion_temperatura_agua_alim": SensorTemperaturaAguaAlimB,
    "prediccion_temperatura_estator": SensorTemperaturaEstatorB,
    "prediccion_vibracion_axial_empuje": SensorVibracionAxialEmpujeB,
    "prediccion_vibracion_x_descanso": SensorVibracionXDescansoB,
    "prediccion_vibracion_y_descanso": SensorVibracionYDescansoB,
    "prediccion_voltaje_barra": SensorVoltajeBarraB,
}


router = APIRouter(prefix="/alertas_umbral", tags=["Alertas"])

async def _get_and_classify_bitacoras(db: Session, dias: int = 2):
    """
    Obtiene las alertas de los últimos N días de ambas bombas (A y B) y las combina en una sola lista
    ordenada por timestamp de manera descendente (las más recientes primero).

    Args:
        db: Sesión de base de datos
        dias: Número de días hacia atrás para filtrar alertas (por defecto 2)
    """
    # Calcular fecha límite según los días especificados
    fecha_limite = datetime.now() - timedelta(days=dias)

    # Obtener alertas de la bomba A de los últimos 2 días
    alertas_a = (
        db.query(AlertaA)
          .filter(AlertaA.timestamp >= fecha_limite)
          .order_by(AlertaA.id.desc())
          .all()
    )

    # Obtener alertas de la bomba B de los últimos 2 días
    alertas_b = (
        db.query(AlertaB)
          .filter(AlertaB.timestamp >= fecha_limite)
          .order_by(AlertaB.id.desc())
          .all()
    )
    
    # Combinar ambas listas
    todas_alertas = alertas_a + alertas_b
    
    # Si no hay alertas, retornar lista vacía
    if not todas_alertas:
        return []
    
    # Ordenar la lista combinada por timestamp (las más recientes primero)
    # Convertimos cada alerta a un diccionario y añadimos un campo 'origen' para identificar de qué bomba proviene
    alertas_formateadas = []
    
    for alerta in alertas_a:
        alerta_dict = {
            "id": alerta.id,
            "sensor_id": alerta.sensor_id,
            "tipo_sensor": alerta.tipo_sensor,
            "timestamp": alerta.timestamp,
            "descripcion": alerta.descripcion,
            "origen": "Bomba A",
            "timestamp_inicio_anomalia": alerta.timestamp_inicio_anomalia,
            "timestamp_fin_anomalia": alerta.timestamp_fin_anomalia,
            "tiene_datos_anomalia": alerta.timestamp_inicio_anomalia is not None
        }
        alertas_formateadas.append(alerta_dict)

    for alerta in alertas_b:
        alerta_dict = {
            "id": alerta.id,
            "sensor_id": alerta.sensor_id,
            "tipo_sensor": alerta.tipo_sensor,
            "timestamp": alerta.timestamp,
            "descripcion": alerta.descripcion,
            "origen": "Bomba B",
            "timestamp_inicio_anomalia": alerta.timestamp_inicio_anomalia,
            "timestamp_fin_anomalia": alerta.timestamp_fin_anomalia,
            "tiene_datos_anomalia": alerta.timestamp_inicio_anomalia is not None
        }
        alertas_formateadas.append(alerta_dict)
    
    # Ordenar por timestamp descendente (las más recientes primero)
    alertas_formateadas.sort(key=lambda x: x["timestamp"], reverse=True)

    # Retornar todas las alertas de los últimos 2 días (sin límite)
    return alertas_formateadas


# Ruta GET para obtener alertas con filtro de días configurable
@router.get(
    "/todas_alertas",
    summary="Obtener todas las alertas de ambas bombas",
    description="""
Consulta las alertas generadas por el sistema de detección de anomalías para ambas bombas (A y B).

**Sistema de Alertas:**
Las alertas se generan automáticamente cuando se detectan múltiples anomalías en un sensor dentro de una ventana de 8 horas:
- **AVISO**: 3+ anomalías en 8 horas
- **ALERTA**: 8+ anomalías en 8 horas
- **CRÍTICA**: 15+ anomalías en 8 horas

**Parámetros:**
- `dias`: Número de días hacia atrás para filtrar (1-90, default: 2)

**Respuesta:**
Lista de alertas ordenadas por timestamp (más recientes primero), incluyendo:
- ID de la alerta
- Tipo de sensor afectado
- Descripción y nivel de severidad
- Timestamps del período anómalo
- Origen (Bomba A o B)
    """,
    response_description="Lista de alertas de ambas bombas"
)
async def get_todas_alertas(
    dias: int = Query(default=2, ge=1, le=90, description="Número de días hacia atrás para filtrar alertas (1-90)"),
    db: Session = Depends(get_db)
):
    try:
        alertas = await _get_and_classify_bitacoras(db, dias=dias)

        return {
            "message": "Consulta exitosa",
            "filtro_dias": dias,
            "total_alertas": len(alertas),
            "data": alertas
        }
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


def _buscar_alerta(db: Session, alerta_id: int, bomba: str = None):
    """
    Busca una alerta por ID. Si se especifica bomba, busca directamente en esa tabla.
    Si no se especifica, busca en ambas (primero B, luego A para evitar colisiones).
    """
    # Si se especifica la bomba, buscar directamente en esa tabla
    if bomba:
        bomba_upper = bomba.upper()
        if bomba_upper == "A":
            alerta = db.query(AlertaA).filter(AlertaA.id == alerta_id).first()
            if alerta:
                return alerta, "A", MAPEO_SENSORES_A
        elif bomba_upper == "B":
            alerta = db.query(AlertaB).filter(AlertaB.id == alerta_id).first()
            if alerta:
                return alerta, "B", MAPEO_SENSORES_B
        return None, None, None

    # Si no se especifica bomba, buscar en ambas (primero B para evitar colisiones comunes)
    # Buscar en Bomba B primero
    alerta = db.query(AlertaB).filter(AlertaB.id == alerta_id).first()
    if alerta:
        return alerta, "B", MAPEO_SENSORES_B

    # Buscar en Bomba A
    alerta = db.query(AlertaA).filter(AlertaA.id == alerta_id).first()
    if alerta:
        return alerta, "A", MAPEO_SENSORES_A

    return None, None, None


def _obtener_datos_sensor(db: Session, modelo_sensor, timestamp_inicio, timestamp_fin):
    """Obtiene los datos del sensor en el rango temporal especificado"""
    registros = db.query(modelo_sensor).filter(
        modelo_sensor.tiempo_ejecucion >= timestamp_inicio,
        modelo_sensor.tiempo_ejecucion <= timestamp_fin
    ).order_by(modelo_sensor.tiempo_ejecucion.asc()).all()

    return registros


@router.get(
    "/{alerta_id}/datos_anomalia",
    summary="Obtener datos del sensor durante la anomalía",
    description="""
Recupera los registros del sensor correspondiente durante el período exacto de la anomalía que generó la alerta.

**Uso principal:**
Permite recrear el gráfico del comportamiento del sensor durante el evento anómalo, mostrando exactamente qué valores causaron la alerta.

**Parámetros:**
- `alerta_id`: ID de la alerta a consultar
- `bomba`: 'A' o 'B' para especificar la bomba (recomendado si hay IDs duplicados)

**Respuesta incluye:**
- Período anómalo (inicio, fin, duración en minutos)
- Estadísticas (total registros, % anomalías)
- Lista de datos con valor, clasificación y timestamp de cada registro

**Nota:** Solo funciona para alertas que tienen timestamps de anomalía registrados.
    """,
    response_description="Datos del sensor durante el período anómalo"
)
async def get_datos_anomalia(
    alerta_id: int,
    bomba: Optional[str] = Query(None, description="Bomba específica: 'A' o 'B'. Si no se especifica, busca en ambas."),
    db: Session = Depends(get_db)
):
    try:
        # Buscar la alerta (con bomba específica si se proporciona)
        alerta, bomba_encontrada, mapeo_sensores = _buscar_alerta(db, alerta_id, bomba)

        if not alerta:
            raise HTTPException(status_code=404, detail=f"Alerta con ID {alerta_id} no encontrada")

        # Verificar que la alerta tiene timestamps de anomalia
        if not alerta.timestamp_inicio_anomalia or not alerta.timestamp_fin_anomalia:
            raise HTTPException(
                status_code=400,
                detail="Esta alerta no tiene datos del periodo anomalo registrados"
            )

        # Obtener el modelo del sensor
        modelo_sensor = mapeo_sensores.get(alerta.tipo_sensor)
        if not modelo_sensor:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de sensor '{alerta.tipo_sensor}' no reconocido"
            )

        # Obtener los datos del sensor en el periodo anomalo
        registros = _obtener_datos_sensor(
            db,
            modelo_sensor,
            alerta.timestamp_inicio_anomalia,
            alerta.timestamp_fin_anomalia
        )

        # Calcular estadisticas
        total_registros = len(registros)
        registros_anomalos = sum(1 for r in registros if r.clasificacion == -1)
        registros_normales = total_registros - registros_anomalos

        # Calcular duracion en minutos
        duracion = alerta.timestamp_fin_anomalia - alerta.timestamp_inicio_anomalia
        duracion_minutos = int(duracion.total_seconds() / 60)

        # Formatear los datos
        datos = []
        for registro in registros:
            datos.append({
                "tiempo_ejecucion": registro.tiempo_ejecucion.isoformat() if registro.tiempo_ejecucion else None,
                "valor_sensor": registro.valor_sensor,
                "clasificacion": registro.clasificacion,
                "es_anomalia": registro.clasificacion == -1
            })

        return {
            "alerta_id": alerta_id,
            "tipo_sensor": alerta.tipo_sensor,
            "bomba": bomba_encontrada,
            "periodo_anomalo": {
                "timestamp_inicio": alerta.timestamp_inicio_anomalia.isoformat(),
                "timestamp_fin": alerta.timestamp_fin_anomalia.isoformat(),
                "duracion_minutos": duracion_minutos
            },
            "estadisticas": {
                "total_registros": total_registros,
                "registros_anomalos": registros_anomalos,
                "registros_normales": registros_normales,
                "porcentaje_anomalias": round((registros_anomalos / total_registros * 100), 1) if total_registros > 0 else 0
            },
            "datos": datos
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de anomalia: {str(e)}")


@router.get(
    "/{alerta_id}/datos_anomalia_contexto",
    summary="Obtener datos de anomalía con contexto temporal",
    description="""
Recupera los registros del sensor durante la anomalía **más** un contexto temporal extendido antes y después del evento.

**Ventaja sobre `/datos_anomalia`:**
Permite visualizar el comportamiento del sensor ANTES de la anomalía (para identificar patrones previos) y DESPUÉS (para ver la recuperación).

**Parámetros:**
- `alerta_id`: ID de la alerta a consultar
- `minutos_antes`: Minutos de contexto previo (0-120, default: 30)
- `minutos_despues`: Minutos de contexto posterior (0-120, default: 30)
- `bomba`: 'A' o 'B' para especificar la bomba

**Respuesta incluye:**
- Período anómalo original
- Período de consulta extendido
- Datos del sensor con indicador `en_periodo_anomalo` para distinguir registros dentro/fuera del evento
- Estadísticas completas

**Ejemplo de uso:**
Con `minutos_antes=60` y `minutos_despues=30`, se obtienen datos desde 1 hora antes hasta 30 minutos después del período anómalo.
    """,
    response_description="Datos del sensor con contexto temporal extendido"
)
async def get_datos_anomalia_contexto(
    alerta_id: int,
    minutos_antes: int = Query(default=30, ge=0, le=120, description="Minutos de contexto antes del periodo anomalo"),
    minutos_despues: int = Query(default=30, ge=0, le=120, description="Minutos de contexto despues del periodo anomalo"),
    bomba: Optional[str] = Query(None, description="Bomba específica: 'A' o 'B'. Si no se especifica, busca en ambas."),
    db: Session = Depends(get_db)
):
    try:
        # Buscar la alerta (con bomba específica si se proporciona)
        alerta, bomba_encontrada, mapeo_sensores = _buscar_alerta(db, alerta_id, bomba)

        if not alerta:
            raise HTTPException(status_code=404, detail=f"Alerta con ID {alerta_id} no encontrada")

        # Verificar que la alerta tiene timestamps de anomalia
        if not alerta.timestamp_inicio_anomalia or not alerta.timestamp_fin_anomalia:
            raise HTTPException(
                status_code=400,
                detail="Esta alerta no tiene datos del periodo anomalo registrados"
            )

        # Obtener el modelo del sensor
        modelo_sensor = mapeo_sensores.get(alerta.tipo_sensor)
        if not modelo_sensor:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de sensor '{alerta.tipo_sensor}' no reconocido"
            )

        # Calcular rango extendido con contexto
        timestamp_inicio_contexto = alerta.timestamp_inicio_anomalia - timedelta(minutes=minutos_antes)
        timestamp_fin_contexto = alerta.timestamp_fin_anomalia + timedelta(minutes=minutos_despues)

        # Obtener los datos del sensor en el periodo extendido
        registros = _obtener_datos_sensor(
            db,
            modelo_sensor,
            timestamp_inicio_contexto,
            timestamp_fin_contexto
        )

        # Calcular estadisticas
        total_registros = len(registros)
        registros_anomalos = sum(1 for r in registros if r.clasificacion == -1)
        registros_normales = total_registros - registros_anomalos

        # Calcular duracion del periodo anomalo en minutos
        duracion = alerta.timestamp_fin_anomalia - alerta.timestamp_inicio_anomalia
        duracion_minutos = int(duracion.total_seconds() / 60)

        # Formatear los datos con indicador de si estan en el periodo anomalo
        datos = []
        for registro in registros:
            en_periodo_anomalo = (
                registro.tiempo_ejecucion >= alerta.timestamp_inicio_anomalia and
                registro.tiempo_ejecucion <= alerta.timestamp_fin_anomalia
            ) if registro.tiempo_ejecucion else False

            datos.append({
                "tiempo_ejecucion": registro.tiempo_ejecucion.isoformat() if registro.tiempo_ejecucion else None,
                "valor_sensor": registro.valor_sensor,
                "clasificacion": registro.clasificacion,
                "es_anomalia": registro.clasificacion == -1,
                "en_periodo_anomalo": en_periodo_anomalo
            })

        return {
            "alerta_id": alerta_id,
            "tipo_sensor": alerta.tipo_sensor,
            "bomba": bomba_encontrada,
            "periodo_anomalo": {
                "timestamp_inicio": alerta.timestamp_inicio_anomalia.isoformat(),
                "timestamp_fin": alerta.timestamp_fin_anomalia.isoformat(),
                "duracion_minutos": duracion_minutos
            },
            "periodo_consulta": {
                "timestamp_inicio_contexto": timestamp_inicio_contexto.isoformat(),
                "timestamp_fin_contexto": timestamp_fin_contexto.isoformat(),
                "minutos_contexto_previo": minutos_antes,
                "minutos_contexto_posterior": minutos_despues
            },
            "estadisticas": {
                "total_registros": total_registros,
                "registros_anomalos": registros_anomalos,
                "registros_normales": registros_normales,
                "porcentaje_anomalias": round((registros_anomalos / total_registros * 100), 1) if total_registros > 0 else 0
            },
            "datos": datos
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"Error al obtener datos con contexto: {str(e)}")


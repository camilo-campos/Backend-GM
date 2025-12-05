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


router = APIRouter(prefix="/alertas_umbral", tags=["alertas_umbral"])

async def _get_and_classify_bitacoras(db: Session):
    """
    Obtiene las últimas alertas de ambas bombas (A y B) y las combina en una sola lista
    ordenada por timestamp de manera descendente (las más recientes primero).
    """
    # Obtener alertas de la bomba A
    alertas_a = (
        db.query(AlertaA)
          .order_by(AlertaA.id.desc())
          .limit(40)
          .all()
    )
    
    # Obtener alertas de la bomba B
    alertas_b = (
        db.query(AlertaB)
          .order_by(AlertaB.id.desc())
          .limit(40)
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
    
    # Limitar a las 40 alertas más recientes
    return alertas_formateadas[:40]


# Ruta GET filtrando solo fallas
@router.get("/todas_alertas")
async def get_todas_bitacoras_fallas(db: Session = Depends(get_db)):
    try:
        alertas = await _get_and_classify_bitacoras(db)

        return {"message": "Consulta exitosa", "data": alertas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


def _buscar_alerta(db: Session, alerta_id: int):
    """Busca una alerta por ID en ambas tablas (A y B)"""
    # Buscar en Bomba A
    alerta = db.query(AlertaA).filter(AlertaA.id == alerta_id).first()
    if alerta:
        return alerta, "A", MAPEO_SENSORES_A

    # Buscar en Bomba B
    alerta = db.query(AlertaB).filter(AlertaB.id == alerta_id).first()
    if alerta:
        return alerta, "B", MAPEO_SENSORES_B

    return None, None, None


def _obtener_datos_sensor(db: Session, modelo_sensor, timestamp_inicio, timestamp_fin):
    """Obtiene los datos del sensor en el rango temporal especificado"""
    registros = db.query(modelo_sensor).filter(
        modelo_sensor.tiempo_ejecucion >= timestamp_inicio,
        modelo_sensor.tiempo_ejecucion <= timestamp_fin
    ).order_by(modelo_sensor.tiempo_ejecucion.asc()).all()

    return registros


@router.get("/{alerta_id}/datos_anomalia")
async def get_datos_anomalia(
    alerta_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos del sensor durante el periodo de anomalia de una alerta especifica.
    Permite recrear el grafico del momento exacto de la anomalia.
    """
    try:
        # Buscar la alerta
        alerta, bomba, mapeo_sensores = _buscar_alerta(db, alerta_id)

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
            "bomba": bomba,
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


@router.get("/{alerta_id}/datos_anomalia_contexto")
async def get_datos_anomalia_contexto(
    alerta_id: int,
    minutos_antes: int = Query(default=30, ge=0, le=120, description="Minutos de contexto antes del periodo anomalo"),
    minutos_despues: int = Query(default=30, ge=0, le=120, description="Minutos de contexto despues del periodo anomalo"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los datos del sensor con contexto temporal extendido.
    Incluye datos ANTES y DESPUES del periodo anomalo para visualizar
    el comportamiento previo y la recuperacion del sensor.
    """
    try:
        # Buscar la alerta
        alerta, bomba, mapeo_sensores = _buscar_alerta(db, alerta_id)

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
            "bomba": bomba,
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


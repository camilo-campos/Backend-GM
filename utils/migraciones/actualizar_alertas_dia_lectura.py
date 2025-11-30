"""
Script de migración para:
 1) Actualizar las descripciones de las alertas (tabla 'alertas') para incluir
    "Día de lectura" tomado EXCLUSIVAMENTE desde tiempo_ejecucion del registro
    del sensor (bomba A).
 2) Corregir el año de tiempo_ejecucion en los registros de sensores cuando se
    guardó por error (por ejemplo, 2025 -> 2024). NO modifica tiempo_sensor.

Uso básico (solo actualizar alertas, sin guardar cambios):
    python -m utils.migraciones.actualizar_alertas_dia_lectura --dry-run

Aplicar cambios reales (actualizar alertas):
    python -m utils.migraciones.actualizar_alertas_dia_lectura

Corregir el año de tiempo_ejecucion en sensores (por ejemplo, fijar 2024 para 'prediccion_corriente'):
    python -m utils.migraciones.actualizar_alertas_dia_lectura \
        --fix-ejecucion-year \
        --target-year 2024 \
        --tipo-sensor prediccion_corriente

Notas:
 - Este script trabaja con las tablas de la bomba A (modelos.modelos).
 - Para bomba B se necesitaría un script análogo importando modelos_b.modelos_b.
"""

import re
import argparse
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from modelos.database import SessionLocal
from modelos.modelos import (
    Alerta,
    SensorCorriente,
    SensorSalidaAgua,
    SensorPresionAgua,
    SensorMw_brutos_generacion_gas,
    SensorTemperatura_Ambiental,
    SensorTemperatura_descanso_interna_empuje_bomba_1aa,
    SensorTemperatura_descanso_interna_motor_bomba_1a,
    SensorTemperatura_descanso_interno_bomba_1a,
    SensorVibracion_axial_descanso,
    SensorVoltaje_barra,
    SensorExcentricidadBomba,
    SensorFlujoAguaDomoAP,
    SensorFlujoAguaDomoMP,
    SensorFlujoAguaRecalentador,
    SensorFlujoAguaVaporAlta,
    SensorPosicionValvulaRecirc,
    SensorPresionAguaMP,
    SensorPresionSuccionBAA,
    SensorTemperaturaEstator,
    SensorFlujoSalida12FPMFC,
)


# Mapeo entre el valor de Alerta.tipo_sensor y la clase de tabla de sensor (bomba A)
TIPO_SENSOR_TO_MODEL = {
    'prediccion_corriente': SensorCorriente,
    'prediccion_salida-agua': SensorSalidaAgua,
    'prediccion_presion-agua': SensorPresionAgua,
    'prediccion_mw-brutos-gas': SensorMw_brutos_generacion_gas,
    'prediccion_temperatura-ambiental': SensorTemperatura_Ambiental,
    'prediccion_temp-descanso-bomba-1a': SensorTemperatura_descanso_interno_bomba_1a,
    'prediccion_temp-empuje-bomba-1a': SensorTemperatura_descanso_interna_empuje_bomba_1aa,
    'prediccion_temp-motor-bomba-1a': SensorTemperatura_descanso_interna_motor_bomba_1a,
    'prediccion_vibracion-axial': SensorVibracion_axial_descanso,
    'prediccion_voltaje-barra': SensorVoltaje_barra,
    'prediccion_excentricidad-bomba': SensorExcentricidadBomba,
    'prediccion_flujo-agua-domo-ap': SensorFlujoAguaDomoAP,
    'prediccion_flujo-agua-domo-mp': SensorFlujoAguaDomoMP,
    'prediccion_flujo-agua-recalentador': SensorFlujoAguaRecalentador,
    'prediccion_flujo-agua-vapor-alta': SensorFlujoAguaVaporAlta,
    'prediccion_posicion-valvula-recirc': SensorPosicionValvulaRecirc,
    'prediccion_presion-agua-mp': SensorPresionAguaMP,
    'prediccion_presion-succion-baa': SensorPresionSuccionBAA,
    'prediccion_temperatura-estator': SensorTemperaturaEstator,
    'prediccion_flujo-salida-12fpmfc': SensorFlujoSalida12FPMFC,
}


def construir_datetime_desde_ejecucion(sensor_obj) -> datetime:
    """Obtiene el datetime de lectura desde tiempo_ejecucion del registro del sensor.
    No utiliza tiempo_sensor; si tiempo_ejecucion no es datetime, intenta parsear ISO.
    """
    te = getattr(sensor_obj, 'tiempo_ejecucion', None)
    if isinstance(te, datetime):
        return te
    try:
        return datetime.fromisoformat(str(te))
    except Exception:
        return datetime.now()


def actualizar_alerta_descripcion(alerta: Alerta, dia_dt: datetime) -> Tuple[str, bool]:
    """
    Actualiza la descripción de la alerta para incluir 'Día de lectura: YYYY-MM-DD'.
    - Si existe el segmento 'Período: HH:MM - HH:MM', inserta la fecha inmediatamente después
      de ese segmento, manteniendo la lógica del texto.
    - Si no existe 'Período:', agrega la línea de 'Día de lectura' al final como antes.

    Retorna (descripcion_actualizada, se_modifico)
    """
    desc_original = alerta.descripcion or ""
    dia_str = dia_dt.strftime("%Y-%m-%d")

    # 1) Quitar cualquier 'Día de lectura: YYYY-MM-DD' existente para evitar duplicados
    desc_sin_fecha = re.sub(r"\s*Día de lectura:\s*\d{4}-\d{2}-\d{2}\.?", "", desc_original).strip()

    # 2) Intentar ubicar justo después de 'Período: HH:MM - HH:MM'
    patron_periodo = r"(Período:\s*\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})(\.)?"

    if re.search(patron_periodo, desc_sin_fecha):
        def _repl(m):
            base = m.group(1)
            punto = m.group(2) or "."
            # Insertamos la fecha inmediatamente después del período, con puntuación coherente
            return f"{base}{punto} Día de lectura: {dia_str}"

        nuevo_desc = re.sub(patron_periodo, _repl, desc_sin_fecha, count=1)
        mod = (nuevo_desc != desc_original)
        return nuevo_desc, mod
    else:
        # 3) Fallback: agregar al final como nueva línea
        sufijo = "\n" if not desc_sin_fecha.endswith("\n") else ""
        nuevo_desc = f"{desc_sin_fecha}{sufijo}Día de lectura: {dia_str}"
        mod = (nuevo_desc != desc_original)
        return nuevo_desc, mod


def procesar_alertas(db: Session, dry_run: bool = True, tipo_sensor_filtro: Optional[str] = None):
    """Actualiza las descripciones de las alertas para incluir el día de lectura
    tomando SIEMPRE el día desde tiempo_ejecucion del sensor.
    """
    tipos = [tipo_sensor_filtro] if tipo_sensor_filtro else list(TIPO_SENSOR_TO_MODEL.keys())
    q = db.query(Alerta).filter(Alerta.tipo_sensor.in_(tipos)).order_by(Alerta.id.asc())
    total = 0
    actualizadas = 0
    sin_sensor = 0
    for alerta in q.all():
        total += 1
        model_cls = TIPO_SENSOR_TO_MODEL.get(alerta.tipo_sensor)
        sensor_obj = db.query(model_cls).get(alerta.sensor_id) if model_cls else None
        if not sensor_obj:
            sin_sensor += 1
            continue
        dia_dt = construir_datetime_desde_ejecucion(sensor_obj)
        nuevo_desc, mod = actualizar_alerta_descripcion(alerta, dia_dt)
        if mod:
            actualizadas += 1
            alerta.descripcion = nuevo_desc
            # Ajustar timestamp de la alerta para reflejar el momento del dato
            alerta.timestamp = dia_dt
            if not dry_run:
                db.add(alerta)
    if not dry_run:
        db.commit()
    print(f"Alertas procesadas: {total}, actualizadas: {actualizadas}, sin sensor: {sin_sensor}, dry_run={dry_run}")


def corregir_tiempo_ejecucion_year(db: Session, target_year: int, tipo_sensor: str):
    """Corrige SOLO el año de tiempo_ejecucion en la tabla de sensores indicada.
    No modifica tiempo_sensor. Útil para casos donde tiempo_ejecucion quedó con 2025.
    """
    model_cls = TIPO_SENSOR_TO_MODEL.get(tipo_sensor)
    if not model_cls:
        raise ValueError(f"tipo_sensor no reconocido: {tipo_sensor}")

    q = db.query(model_cls).order_by(model_cls.id.asc())
    actualizados = 0
    total = 0
    for s in q.all():
        total += 1
        te = getattr(s, 'tiempo_ejecucion', None)
        if isinstance(te, datetime):
            if te.year != target_year:
                nuevo_te = datetime(target_year, te.month, te.day, te.hour, te.minute, te.second, te.microsecond, te.tzinfo)
                s.tiempo_ejecucion = nuevo_te
                actualizados += 1
                db.add(s)
        else:
            # Intentar parseo ISO, ajustar año si procede
            try:
                te_parsed = datetime.fromisoformat(str(te))
                if te_parsed.year != target_year:
                    nuevo_te = datetime(target_year, te_parsed.month, te_parsed.day, te_parsed.hour, te_parsed.minute, te_parsed.second, te_parsed.microsecond, te_parsed.tzinfo)
                    s.tiempo_ejecucion = nuevo_te
                    actualizados += 1
                    db.add(s)
            except Exception:
                # No se puede parsear; se omite
                pass
    db.commit()
    print(f"Sensores '{tipo_sensor}' procesados: {total}, tiempo_ejecucion corregidos: {actualizados} (target_year={target_year})")


def main():
    parser = argparse.ArgumentParser(description="Actualizar alertas con Día de lectura (desde tiempo_ejecucion) y corregir año de tiempo_ejecucion en sensores (Bomba A)")
    parser.add_argument('--dry-run', action='store_true', help='No guarda cambios, solo muestra conteos (por defecto: False)')
    parser.add_argument('--tipo-sensor', type=str, default=None, help='Filtrar por un tipo de sensor específico (clave de alerta)')
    parser.add_argument('--fix-ejecucion-year', action='store_true', help='Corrige SOLO el año de tiempo_ejecucion en la tabla de sensores indicada por --tipo-sensor')
    parser.add_argument('--target-year', type=int, default=2024, help='Año objetivo para tiempo_ejecucion (por defecto: 2024)')

    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        procesar_alertas(db, dry_run=args.dry_run, tipo_sensor_filtro=args.tipo_sensor)
        if args.fix_ejecucion_year:
            if not args.tipo_sensor:
                raise ValueError("--fix-ejecucion-year requiere --tipo-sensor para identificar la tabla de sensores a corregir")
            corregir_tiempo_ejecucion_year(db, target_year=args.target_year, tipo_sensor=args.tipo_sensor)
    finally:
        db.close()


if __name__ == '__main__':
    main()
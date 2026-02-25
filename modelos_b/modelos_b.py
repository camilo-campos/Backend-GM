from sqlalchemy import Column, Integer, Float, String, DateTime, Text, func, ForeignKey, Time, Date
from sqlalchemy.sql import func
from modelos.database import Base



class Alerta(Base):
    __tablename__ = 'alertas_b'

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)  # ID del sensor afectado
    tipo_sensor = Column(String, nullable=False)  # Tipo de sensor (corriente, voltaje, etc.)
    timestamp = Column(DateTime, default=func.now())  # Fecha y hora de la alerta
    descripcion = Column(Text)  # Texto descriptivo de la alerta
    contador_anomalias = Column(Integer, default=0)
    timestamp_inicio_anomalia = Column(DateTime, nullable=True)  # Inicio del periodo anomalo
    timestamp_fin_anomalia = Column(DateTime, nullable=True)  # Fin del periodo anomalo



class SensorCorriente(Base):
    __tablename__ = 'sensores_corriente_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor, puede ser int o float
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)






class SensorExcentricidadBomba(Base):
    __tablename__ = 'excentricidad_bomba_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoDescarga(Base):
    __tablename__ = 'flujo_descarga_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaDomoAP(Base):
    __tablename__ = 'flujo_agua_domo_ap_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaDomoMP(Base):
    __tablename__ = 'flujo_agua_domo_mp_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaRecalentador(Base):
    __tablename__ = 'flujo_agua_recalentador_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaVaporAlta(Base):
    __tablename__ = 'flujo_agua_vapor_alta_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorPresionAgua(Base):
    __tablename__ = 'presion_agua_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaAmbiental(Base):
    __tablename__ = 'temperatura_ambiental_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaAguaAlim(Base):
    __tablename__ = 'temperatura_agua_alim_ap_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaEstator(Base):
    __tablename__ = 'temperatura_estator_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorVibracionAxialEmpuje(Base):
    __tablename__ = 'vibracion_axial_empuje_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorVibracionXDescanso(Base):
    __tablename__ = 'vibracion_x_descanso_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorVibracionYDescanso(Base):
    __tablename__ = 'vibracion_y_descanso_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorVoltajeBarra(Base):
    __tablename__ = 'voltaje_barra_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class PrediccionBombaB(Base):
    __tablename__ = 'predicciones_bomba_b'  # Nombre exacto de la tabla
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_prediccion = Column(Float, nullable=False)
    hora_ejecucion = Column(Time, server_default=func.current_time())  # Tipo TIME con valor por defecto
    dia_ejecucion = Column(Date, server_default=func.current_date())  # Tipo DATE con valor por defecto



# ============================================
# MODELOS NUEVOS AGREGADOS - 2025-02-17
# ============================================

class SensorTemperaturaDescansoInternoBombaB(Base):
    __tablename__ = 'temperatura_descanso_interno_bomba_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaDescansoInternaEmpujeBombaB(Base):
    __tablename__ = 'temperatura_descanso_interna_empuje_bomba_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaDescansoInternaMotorBombaB(Base):
    __tablename__ = 'temperatura_descanso_interna_motor_bomba_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


# ============================================
# MODELOS NUEVOS AGREGADOS - 2025-02-23
# Señales faltantes Bomba B
# ============================================

class SensorVibracionXDescansoExternoB(Base):
    __tablename__ = 'vibracion_x_descanso_externo_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorVibracionYDescansoExternoB(Base):
    __tablename__ = 'vibracion_y_descanso_externo_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorPresionSuccionBAAB(Base):
    __tablename__ = 'presion_succion_baa_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorPosicionValvulaRecircB(Base):
    __tablename__ = 'posicion_valvula_recirc_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoDomoAPCompensatedB(Base):
    __tablename__ = 'flujo_domo_ap_compensated_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorMwBrutosGeneracionGasB(Base):
    __tablename__ = 'mw_brutos_generacion_gas_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)


class SensorPresionAguaEconAPB(Base):
    __tablename__ = 'presion_agua_econ_ap_b'

    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())
    tiempo_sensor = Column(String)
    valor_sensor = Column(Float)
    clasificacion = Column(Integer, nullable=True)
    contador_anomalias = Column(Integer, default=0)

from sqlalchemy import Column, Integer, Float, String, DateTime , Text , func , ForeignKey , Time , Date
from sqlalchemy.sql import func
from .database import Base



class Alerta(Base):
    __tablename__ = 'alertas'

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)  # ID del sensor afectado
    tipo_sensor = Column(String, nullable=False)  # Tipo de sensor (corriente, voltaje, etc.)
    timestamp = Column(DateTime, default=func.now())  # Fecha y hora de la alerta
    descripcion = Column(Text)  # Texto descriptivo de la alerta
    contador_anomalias = Column(Integer, default=0)
    timestamp_inicio_anomalia = Column(DateTime, nullable=True)  # Inicio del periodo anomalo
    timestamp_fin_anomalia = Column(DateTime, nullable=True)  # Fin del periodo anomalo



class SensorCorriente(Base):
    __tablename__ = 'sensores_corriente'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor, puede ser int o float
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorSalidaAgua(Base):
    __tablename__ = 'sensores_salida_agua'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorPresionAgua(Base):
    __tablename__ = 'sensores_presion_agua'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorMw_brutos_generacion_gas(Base):
    __tablename__ = 'mw_brutos_generacion_gas'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorTemperatura_Ambiental(Base):
    __tablename__ = 'temperatura_ambiental'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorTemperatura_descanso_interna_empuje_bomba_1aa(Base):
    __tablename__ = 'temperatura_descanso_interna_empuje_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorTemperatura_descanso_interna_motor_bomba_1a(Base):
    __tablename__ = 'temperatura_descanso_interna_motor_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorTemperatura_descanso_interno_bomba_1a(Base):
    __tablename__ = 'temperatura_descanso_interno_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorVibracion_axial_descanso(Base):
    __tablename__ = 'vibracion_axial_descanso'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)

class SensorVoltaje_barra(Base):
    __tablename__ = 'voltaje_barra'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class Bitacora(Base):
    __tablename__ = 'bitacoras'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now(), nullable=False)
    bitacora = Column(Text, nullable=False)
    clasificacion = Column(Text, nullable=True)
    alerta_aviso = Column(Text, nullable=True)


class BitacoraB(Base):
    __tablename__ = 'bitacoras_b'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now(), nullable=False)
    bitacora = Column(Text, nullable=False)
    clasificacion = Column(Text, nullable=True)
    alerta_aviso = Column(Text, nullable=True)


class PrediccionBombaA(Base):
    __tablename__ = 'predicciones_bomba_a'  # Nombre exacto de la tabla
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_prediccion = Column(Float, nullable=False)
    hora_ejecucion = Column(Time, server_default=func.current_time())  # Tipo TIME con valor por defecto
    dia_ejecucion = Column(Date, server_default=func.current_date())  # Tipo DATE con valor por defecto


# Clases para los modelos adicionales
class SensorExcentricidadBomba(Base):
    __tablename__ = 'excentricidad_bomba'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaDomoAP(Base):
    __tablename__ = 'flujo_agua_domo_ap'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaDomoMP(Base):
    __tablename__ = 'flujo_agua_domo_mp'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaRecalentador(Base):
    __tablename__ = 'flujo_agua_recalentador'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoAguaVaporAlta(Base):
    __tablename__ = 'flujo_agua_vapor_alta'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorPosicionValvulaRecirc(Base):
    __tablename__ = 'posicion_valvula_recirc'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorPresionAguaMP(Base):
    __tablename__ = 'presion_agua_mp'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorPresionSuccionBAA(Base):
    __tablename__ = 'presion_succion_baa'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorTemperaturaEstator(Base):
    __tablename__ = 'temperatura_estator'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)


class SensorFlujoSalida12FPMFC(Base):
    __tablename__ = 'flujo_salida_12fpmfc'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos
    contador_anomalias = Column(Integer, default=0)
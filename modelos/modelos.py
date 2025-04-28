from sqlalchemy import Column, Integer, Float, String, DateTime , Text , func , ForeignKey
from sqlalchemy.sql import func
from .database import Base



class Alerta(Base):
    __tablename__ = 'alertas'

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)  # ID del sensor afectado
    tipo_sensor = Column(String, nullable=False)  # Tipo de sensor (corriente, voltaje, etc.)
    timestamp = Column(DateTime, default=func.now())  # Fecha y hora de la alerta
    descripcion = Column(Text)  # Texto descriptivo de la alerta



class SensorCorriente(Base):
    __tablename__ = 'sensores_corriente'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor, puede ser int o float
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorSalidaAgua(Base):
    __tablename__ = 'sensores_salida_agua'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorPresionAgua(Base):
    __tablename__ = 'sensores_presion_agua'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos


class SensorMw_brutos_generacion_gas(Base):
    __tablename__ = 'mw_brutos_generacion_gas'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos


class SensorTemperatura_Ambiental(Base):
    __tablename__ = 'temperatura_ambiental'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorTemperatura_descanso_interna_empuje_bomba_1aa(Base):
    __tablename__ = 'temperatura_descanso_interna_empuje_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorTemperatura_descanso_interna_motor_bomba_1a(Base):
    __tablename__ = 'temperatura_descanso_interna_motor_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorTemperatura_descanso_interno_bomba_1a(Base):
    __tablename__ = 'temperatura_descanso_interno_bomba_1a'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorVibracion_axial_descanso(Base):
    __tablename__ = 'vibracion_axial_descanso'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos

class SensorVoltaje_barra(Base):
    __tablename__ = 'voltaje_barra'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now())  # Fecha y hora de ejecución
    tiempo_sensor = Column(String)  # Hora / minuto del sensor
    valor_sensor = Column(Float)  # Valor del sensor
    clasificacion = Column(Integer, nullable=True)  # Permitir valores nulos


class Bitacora(Base):
    __tablename__ = 'bitacoras'
    
    id = Column(Integer, primary_key=True, index=True)
    tiempo_ejecucion = Column(DateTime, default=func.now(), nullable=False)
    bitacora = Column(Text, nullable=False)
    clasificacion = Column(Text, nullable=True)
    alerta_aviso = Column(Text, nullable=True)
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from .database import Base

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



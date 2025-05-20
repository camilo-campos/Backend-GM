from pydantic import BaseModel , Field
from typing import List

class DatosSensores(BaseModel):
    datos: List[List[float]]
    fecha:str# Lista de listas de valores flotantes
    

class SensorInput(BaseModel):
    id_sensor: str
    valor: float
    
    
class BitacoraInput(BaseModel):
    id_bitacora: str
    bitacora: str

class PrediccionBombaInput(BaseModel):
    """
    Esquema para los datos de entrada para la predicción de la bomba.
    Todas las columnas son requeridas y deben ser valores numéricos.
    """
    presion_agua: float = Field(..., description="Presión Agua Alimentación AP (barg)")
    voltaje_barra: float = Field(..., description="Voltaje Barra 6,6KV (V)")
    corriente_motor: float = Field(..., description="Corriente Motor Bomba Agua Alimentacion BFWP A (A)")
    vibracion_axial: float = Field(..., description="Vibración Axial Descanso Emp Bomba 1A (ms)")
    salida_bomba: float = Field(..., description="Salida de Bomba de Alta Presión")
    flujo_agua: float = Field(..., description="Flujo de Agua Atemperación Vapor Alta AP SH (kg/h)")
    mw_brutos_gas: float = Field(..., description="MW Brutos de Generación Total Gas (MW)")
    temp_motor: float = Field(..., description="Temperatura Descanso Interno Motor Bomba 1A (°C)")
    temp_bomba: float = Field(..., description="Temperatura Descanso Interno Bomba 1A (°C)")
    temp_empuje: float = Field(..., description="Temperatura Descanso Interno Empuje Bomba 1A (°C)")
    temp_ambiental: float = Field(..., description="Temperatura Ambiental (°C)")


class PrediccionBombaOutput(BaseModel):
    """Esquema para la respuesta de la predicción de la bomba"""
    prediccion: float
    status: str = "success"

from datetime import time, date

class PrediccionBombaResponse(BaseModel):
    id: int
    valor_prediccion: float
    hora_ejecucion: time
    dia_ejecucion: date

    class Config:
        from_attributes = True  # Reemplaza orm_mode en Pydantic v2
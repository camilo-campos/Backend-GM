from pydantic import BaseModel , Field
from typing import List

class DatosSensores(BaseModel):
    datos: List[List[float]]
    fecha:str# Lista de listas de valores flotantes
    

class SensorInput(BaseModel):
    valor: float
    
    
class BitacoraInput(BaseModel):
    id_bitacora: str
    bitacora: str

class PrediccionBombaInput(BaseModel):
    """
    Esquema para los datos de entrada para la predicción de la bomba.
    Todas las columnas son requeridas y deben ser valores numéricos.
    Contiene un campo para cada modelo en la carpeta modelos_prediccion.
    """
    # Campos originales
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
    
    # Campos adicionales para los otros modelos
    excentricidad_bomba: float = Field(..., description="Excentricidad Bomba 1A")
    flujo_agua_domo_ap: float = Field(..., description="Flujo de Agua Alimentación Domo AP")
    flujo_agua_domo_mp: float = Field(..., description="Flujo de Agua Alimentación Domo MP")
    flujo_agua_recalentador: float = Field(..., description="Flujo de Agua Atemperación Recalentador")
    posicion_valvula_recirc: float = Field(..., description="Posición válvula recirculación BAA")
    presion_agua_mp: float = Field(..., description="Presión Agua Alimentación Economizador MP")
    presion_succion_baa: float = Field(..., description="Presión succión BAA")
    temperatura_estator: float = Field(..., description="Temperatura Estator Motor Bomba AA")
    flujo_salida_12fpmfc: float = Field(..., description="Flujo de Salida 12FPMFC")


class PrediccionBombaBInput(BaseModel):
    """
    Esquema para los datos de entrada para la predicción de la bomba B.
    Todas las columnas son requeridas y deben ser valores numéricos.
    Contiene un campo para cada modelo en la carpeta modelos_prediccion_b (excepto bm_randomforest_bomba_b.pkl).
    """
    # Campos basados en los modelos en modelos_prediccion_b
    corriente_motor: float = Field(..., description="Corriente Motor Bomba Agua Alimentacion 1B")
    excentricidad_bomba: float = Field(..., description="Excentricidad Bomba 1B")
    flujo_descarga_ap: float = Field(..., description="Flujo Descarga AP BAA AE01B")
    flujo_agua_domo_ap: float = Field(..., description="Flujo de Agua Alimentación Domo AP Compensated")
    flujo_agua_domo_mp: float = Field(..., description="Flujo de Agua Alimentación Domo MP Compensated")
    flujo_agua_recalentador: float = Field(..., description="Flujo de Agua Atemperación Recalentador")
    flujo_agua_vapor_alta: float = Field(..., description="Flujo de Agua Atemperación Vapor Alta AP SH")
    presion_agua_ap: float = Field(..., description="Presión Agua Alimentación Economizador AP")
    temperatura_ambiental: float = Field(..., description="Temperatura Ambiental")
    temperatura_agua_alim_ap: float = Field(..., description="Temperatura Agua Alimentación AP")
    temperatura_estator: float = Field(..., description="Temperatura Estator Motor Bomba AA 1B")
    vibracion_axial: float = Field(..., description="Vibración Axial Descanso Empuje Bomba 1B")
    vibracion_x_descanso: float = Field(..., description="Vibración X Descanso Interno Bomba 1B")
    vibracion_y_descanso: float = Field(..., description="Vibración Y Descanso Interno Bomba 1B")
    voltaje_barra: float = Field(..., description="Voltaje Barra 6.6KV")


class PrediccionBombaOutput(BaseModel):
    """Esquema para la respuesta de la predicción de la bomba"""
    prediccion: float
    status: str = "success"


class PrediccionBombaBOutput(BaseModel):
    """Esquema para la respuesta de la predicción de la bomba B"""
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
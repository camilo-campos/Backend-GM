from pydantic import BaseModel
from typing import List

class DatosSensores(BaseModel):
    datos: List[List[float]]  # Lista de listas de valores flotantes

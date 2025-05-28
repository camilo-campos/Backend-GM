from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import Alerta as AlertaA
from modelos_b.modelos_b import Alerta as AlertaB


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
            "contador_anomalias": alerta.contador_anomalias,
            "origen": "Bomba A"
        }
        alertas_formateadas.append(alerta_dict)
    
    for alerta in alertas_b:
        alerta_dict = {
            "id": alerta.id,
            "sensor_id": alerta.sensor_id,
            "tipo_sensor": alerta.tipo_sensor,
            "timestamp": alerta.timestamp,
            "descripcion": alerta.descripcion,
            "contador_anomalias": alerta.contador_anomalias,
            "origen": "Bomba B"
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




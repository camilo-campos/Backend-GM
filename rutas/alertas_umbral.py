from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import Alerta
from esquemas.esquema import BitacoraInput
from langchain_llm.analisis import llm_chain, llm_chain_2

router = APIRouter(prefix="/alertas_umbral", tags=["alertas_umbral"])

async def _get_and_classify_bitacoras(db: Session):
    """
    Obtiene las últimas 40 bitácoras, predice y actualiza su clasificación
    si está nula, y retorna la lista completa.
    """
    Alertas = (
        db.query(Alerta)
          .order_by(Alerta.id.desc())
          .limit(40)
          .all()
    )

    if not Alertas:
        return []


    return Alertas


# Ruta GET filtrando solo fallas
@router.get("/todas_alertas")
async def get_todas_bitacoras_fallas(db: Session = Depends(get_db)):
    try:
        alertas = await _get_and_classify_bitacoras(db)
       
        return {"message": "Consulta exitosa", "data": alertas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")




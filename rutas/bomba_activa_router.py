from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from modelos.database import get_db
from modelos.modelos import BombaActiva

router = APIRouter(prefix="/bomba_activa", tags=["Bomba Activa"])


@router.get(
    "/actual",
    summary="Obtener la bomba activa actual",
    description="""
Consulta el último registro de la tabla bomba_activa para determinar cuál bomba está operando.

**Valores posibles:**
- `A`: Solo Bomba A activa
- `B`: Solo Bomba B activa
- `A/B`: Ambas bombas activas

El frontend usa este dato para filtrar las alertas de sensores generales
y mostrarlas solo en la bomba correspondiente.
    """,
)
async def get_bomba_activa(db: Session = Depends(get_db)):
    try:
        ultimo = (
            db.query(BombaActiva)
            .order_by(BombaActiva.id.desc())
            .first()
        )

        if not ultimo:
            return {
                "bomba_activa": None,
                "mensaje": "No hay registros de bomba activa"
            }

        valor = ultimo.bomba_activa
        if valor == "O":
            estado = "Sin bomba activa"
        elif valor == "A/B":
            estado = "Ambas bombas activas"
        else:
            estado = f"Bomba {valor} activa"

        return {
            "bomba_activa": valor,
            "estado": estado,
            "tiempo_ejecucion": ultimo.tiempo_ejecucion.isoformat() if ultimo.tiempo_ejecucion else None,
            "tiempo_sensor": ultimo.tiempo_sensor,
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al consultar bomba activa")


@router.get(
    "/historial",
    summary="Obtener historial de cambios de bomba activa",
    description="Devuelve los últimos N registros donde hubo un cambio de bomba activa.",
)
async def get_historial_bomba_activa(
    limite: int = 50,
    db: Session = Depends(get_db)
):
    try:
        registros = (
            db.query(BombaActiva)
            .order_by(BombaActiva.id.desc())
            .limit(limite)
            .all()
        )

        # Filtrar solo los cambios (cuando bomba_activa cambia respecto al registro anterior)
        cambios = []
        ultimo_valor = None
        for reg in reversed(registros):
            if reg.bomba_activa != ultimo_valor:
                cambios.append({
                    "bomba_activa": reg.bomba_activa,
                    "tiempo_ejecucion": reg.tiempo_ejecucion.isoformat() if reg.tiempo_ejecucion else None,
                    "tiempo_sensor": reg.tiempo_sensor,
                })
                ultimo_valor = reg.bomba_activa

        return {
            "total_cambios": len(cambios),
            "historial": list(reversed(cambios))
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al consultar historial")

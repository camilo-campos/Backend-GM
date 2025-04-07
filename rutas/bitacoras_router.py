from fastapi import APIRouter, Depends , HTTPException
from esquemas.esquema import BitacoraInput
from sqlalchemy.orm import Session
from modelos.database import get_db 
from modelos.modelos import Bitacora
from langchain_llm.analisis import llm_chain , llm_chain_2 


router = APIRouter(prefix="/bitacoras", tags=["bitacoras"])
#llm_chain.invoke({"bitacora": ""})
#llm_chain_2.invoke({"bitacora": ""})

@router.post("/analisis")
async def predecir_corriente(bitacora: BitacoraInput, db: Session = Depends(get_db)):
    try:
        # Realizar el primer análisis
        primer_analisis = llm_chain.invoke({"bitacora": bitacora.bitacora}).strip()  # Eliminar espacios en blanco innecesarios
        
        # Buscar la bitacora por el ID que envía el usuario
        bitacora_db = db.query(Bitacora).filter(Bitacora.id == bitacora.id_bitacora).first()
        
        if not bitacora_db:
            raise HTTPException(status_code=404, detail="Bitacora no encontrada.")
        
        # Si el primer análisis contiene "HRSG Pump Failures", realizar el segundo análisis
        if "HRSG Pump Failures" in primer_analisis:
            segundo_analisis = llm_chain_2.invoke({"bitacora": bitacora.bitacora}).strip()  # Eliminar espacios en blanco innecesarios
            
            # Actualizar la bitacora con los resultados de ambos análisis
            bitacora_db.clasificacion = primer_analisis  # Guardamos el primer análisis en clasificacion
            bitacora_db.alerta_aviso = segundo_analisis  # Guardamos el segundo análisis en alerta_aviso
            
            # Guardar los cambios en la base de datos
            db.commit()

            return {
                "primer resultado": primer_analisis,
                "segundo resultado": segundo_analisis
            }
        else:
            # Si no contiene "HRSG Pump Failures", solo actualizamos clasificacion
            bitacora_db.clasificacion = primer_analisis
            
            # Guardar los cambios en la base de datos
            db.commit()

            return {
                "primer resultado": primer_analisis
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# Ruta para obtener datos de sensores de corriente
@router.get("/todas")
async def get_todas_bitacoras(db: Session = Depends(get_db)):
    try:
        bitacoras = (
            db.query(Bitacora)
            .order_by(Bitacora.id.desc())  # Últimos registros primero
            .limit(40)  # Limita a los últimos 40
            .all()
        )
        
        if not bitacoras:
            return {
                "message": "No hay bitácoras registradas en la base de datos.",
                "data": []
            }

        return {
            "message": "Consulta exitosa",
            "data": bitacoras
        }
    except Exception as e:
        print("Error:", e)
        return {
            "message": "Error al conectar con la base de datos.",
            "error": str(e),
            "data": []
        }
        
        
@router.get("/todas_fallas")
async def get_todas_bitacoras_fallas(db: Session = Depends(get_db)):
    try:
        bitacoras = (
            db.query(Bitacora)
            .filter(Bitacora.clasificacion.like('%HRSG Pump Failures%'))  # Filtrando por la columna clasificacion
            .order_by(Bitacora.id.desc())  # Últimos registros primero
            .limit(40)  # Limita a los últimos 40
            .all()
        )
        
        if not bitacoras:
            return {
                "message": "No hay bitácoras relacionadas con 'HRSG Pump Failures'.",
                "data": []
            }

        return {
            "message": "Consulta exitosa",
            "data": bitacoras
        }
    except Exception as e:
        print("Error:", e)
        return {
            "message": "Error al conectar con la base de datos.",
            "error": str(e),
            "data": []
        }






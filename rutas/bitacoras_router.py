from fastapi import APIRouter, Depends , HTTPException
from esquemas.esquema import BitacoraInput
from sqlalchemy.orm import Session
from modelos.database import get_db
from langchain_llm.analisis import llm_chain , llm_chain_2 


router = APIRouter(prefix="/bitacoras", tags=["bitacoras"])
#llm_chain.invoke({"bitacora": ""})
#llm_chain_2.invoke({"bitacora": ""})

@router.post("/analisis")
async def predecir_corriente(bitacora: BitacoraInput, db: Session = Depends(get_db)):
    try:
        primer_analisis = llm_chain.invoke({"bitacora": bitacora.bitacora})
        
        if "HRSG Pump Failures" in primer_analisis:
            
            segundo_analisis = llm_chain_2.invoke({"bitacora": bitacora.bitacora})
            return {
                "primer resultado" : primer_analisis,
                "segundo resultado" : segundo_analisis
            }
        else:
            
            return {
            "primer resultado" : primer_analisis
            
        }

            
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Ruta para obtener datos de sensores de corriente
@router.get("/corriente")
async def get_sensores_corriente():
    try:
        

            
        return 
    except Exception as e:
        print("Error:", e)
        return {
            
        }





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import BitacoraB
from esquemas.esquema import BitacoraInput
from langchain_llm.analisis import llm_chain, llm_chain_2
from utils.traduccion_bitacoras import verificar_y_traducir_bitacora
import asyncio

router = APIRouter(prefix="/bitacoras_b", tags=["bitacoras_b"])

async def _get_and_classify_bitacoras(db: Session):
    """
    Obtiene las últimas 40 bitácoras, predice y actualiza su clasificación
    si está nula, y retorna la lista completa.
    """
    bitacoras = (
        db.query(BitacoraB)
          .order_by(BitacoraB.id.desc())
          .limit(40)
          .all()
    )

    if not bitacoras:
        return []

    # Filtrar sin clasificación
    no_clasificadas = [b for b in bitacoras if b.clasificacion is None]
    if no_clasificadas:
        for b in no_clasificadas:
            primer_analisis = llm_chain.invoke({"bitacora": b.bitacora}).strip()
            # Si detecta fallo específico
            if "HRSG Pump Failures" in primer_analisis:
                segundo_analisis = llm_chain_2.invoke({"bitacora": b.bitacora}).strip()
                b.clasificacion = primer_analisis
                b.alerta_aviso = segundo_analisis
            else:
                b.clasificacion = primer_analisis

            db.add(b)
        
        db.commit()
        
        # Verificar y traducir bitácoras después de la clasificación (asíncrono)
        for b in no_clasificadas:
            db.refresh(b)
            # Aplicar verificación y traducción automática
            try:
                resultado_traduccion = await verificar_y_traducir_bitacora(b.id, db)
                if resultado_traduccion['traduccion_realizada']:
                    print(f"✅ BitácoraB {b.id} traducida automáticamente")
                elif resultado_traduccion['errores']:
                    print(f"❌ Errores en traducción de BitácoraB {b.id}: {resultado_traduccion['errores']}")
            except Exception as e:
                print(f"❌ Error en traducción de BitácoraB {b.id}: {e}")

    return bitacoras

# Ruta para análisis puntual (POST original)
@router.post("/analisis")
async def predecir_corriente(bitacora: BitacoraInput, db: Session = Depends(get_db)):
    try:
        primer_analisis = llm_chain.invoke({"bitacora": bitacora.bitacora}).strip()
        bitacora_db = db.query(BitacoraB).filter(BitacoraB.id == bitacora.id_bitacora).first()
        if not bitacora_db:
            raise HTTPException(status_code=404, detail="Bitacora no encontrada.")

        if "HRSG Pump Failures" in primer_analisis:
            segundo_analisis = llm_chain_2.invoke({"bitacora": bitacora.bitacora}).strip()
            bitacora_db.clasificacion = primer_analisis
            bitacora_db.alerta_aviso = segundo_analisis
            db.commit()
            
            # Verificar y traducir después de la clasificación (asíncrono)
            try:
                resultado_traduccion = await verificar_y_traducir_bitacora(bitacora_db.id, db)
                if resultado_traduccion['traduccion_realizada']:
                    print(f"✅ BitácoraB {bitacora_db.id} traducida exitosamente")
                else:
                    print(f"ℹ️ BitácoraB {bitacora_db.id} no requirió traducción")
            except Exception as e:
                print(f"❌ Error en traducción de BitácoraB {bitacora_db.id}: {e}")
            
            return {"primer resultado": primer_analisis, "segundo resultado": segundo_analisis}
        else:
            bitacora_db.clasificacion = primer_analisis
            db.commit()
            
            # Verificar y traducir después de la clasificación (asíncrono)
            try:
                resultado_traduccion = await verificar_y_traducir_bitacora(bitacora_db.id, db)
                if resultado_traduccion['traduccion_realizada']:
                    print(f"✅ BitácoraB {bitacora_db.id} traducida exitosamente")
                else:
                    print(f"ℹ️ BitácoraB {bitacora_db.id} no requirió traducción")
            except Exception as e:
                print(f"❌ Error en traducción de BitácoraB {bitacora_db.id}: {e}")
            
            return {"primer resultado": primer_analisis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ruta GET todas con clasificación automática
@router.get("/todas")
async def get_todas_bitacoras(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_bitacoras(db)
        return {"message": "Consulta exitosa", "data": bitacoras}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")

# Ruta GET filtrando solo fallas
@router.get("/todas_fallas")
async def get_todas_bitacoras_fallas(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_bitacoras(db)
        # Filtrar fallas HRSG en ambos idiomas (inglés y español)
        fallas = [b for b in bitacoras if b.clasificacion and (
            "HRSG Pump Failures" in b.clasificacion or
            "Fallas de Bomba HRSG" in b.clasificacion or
            "Fallas de Bombas HRSG" in b.clasificacion
        )]
        return {"message": "Consulta exitosa", "data": fallas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")







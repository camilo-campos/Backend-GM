from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import Bitacora
from esquemas.esquema import BitacoraInput
from langchain_llm.analisis import llm_chain, llm_chain_2
from utils.traduccion_bitacoras import verificar_y_traducir_bitacora, traducir_clasificacion
import asyncio

router = APIRouter(prefix="/bitacoras", tags=["bitacoras"])

async def _get_and_classify_bitacoras(db: Session):
    """
    Obtiene las últimas 40 bitácoras, predice y actualiza su clasificación
    si está nula, y retorna la lista completa.
    """
    bitacoras = (
        db.query(Bitacora)
          .order_by(Bitacora.id.desc())
          .limit(40)
          .all()
    )

    if not bitacoras:
        return []

    # Si WatsonX no está disponible, solo retornar las bitácoras sin clasificar
    if llm_chain is None:
        return bitacoras

    # Filtrar sin clasificación
    no_clasificadas = [b for b in bitacoras if b.clasificacion is None]
    if no_clasificadas:
        for b in no_clasificadas:
            primer_analisis = llm_chain.invoke({"bitacora": b.bitacora}).strip()
            # Si detecta fallo específico (comparación en inglés)
            if "HRSG Pump Failures" in primer_analisis:
                segundo_analisis = llm_chain_2.invoke({"bitacora": b.bitacora}).strip()
                b.clasificacion = primer_analisis  # Guardar en inglés primero
                b.alerta_aviso = segundo_analisis
            else:
                b.clasificacion = primer_analisis  # Guardar en inglés primero

            db.add(b)

        db.commit()

        # Proceso final: traducir texto y clasificaciones
        for b in no_clasificadas:
            db.refresh(b)

            # Paso 1: Verificar y traducir texto de bitácora (si está en inglés)
            try:
                resultado_traduccion = await verificar_y_traducir_bitacora(b.id, db)
                if resultado_traduccion['traduccion_realizada']:
                    print(f"✅ Bitácora {b.id} traducida automáticamente")
                elif resultado_traduccion['errores']:
                    print(f"❌ Errores en traducción de bitácora {b.id}: {resultado_traduccion['errores']}")
            except Exception as e:
                print(f"❌ Error en traducción de bitácora {b.id}: {e}")

            # Paso 2: Traducir clasificación de inglés a español (último paso)
            if b.clasificacion:
                clasificacion_original = b.clasificacion
                b.clasificacion = traducir_clasificacion(clasificacion_original)
                if b.clasificacion != clasificacion_original:
                    db.add(b)
                    print(f"✅ Clasificación traducida: {clasificacion_original[:50]}... -> {b.clasificacion[:50]}...")

        db.commit()

    return bitacoras

# Ruta para análisis puntual (POST original)
@router.post("/analisis")
async def predecir_corriente(bitacora: BitacoraInput, db: Session = Depends(get_db)):
    try:
        primer_analisis = llm_chain.invoke({"bitacora": bitacora.bitacora}).strip()
        bitacora_db = db.query(Bitacora).filter(Bitacora.id == bitacora.id_bitacora).first()
        if not bitacora_db:
            raise HTTPException(status_code=404, detail="Bitacora no encontrada.")

        # Guardar clasificación en inglés primero (para que el proceso funcione correctamente)
        if "HRSG Pump Failures" in primer_analisis:
            segundo_analisis = llm_chain_2.invoke({"bitacora": bitacora.bitacora}).strip()
            bitacora_db.clasificacion = primer_analisis
            bitacora_db.alerta_aviso = segundo_analisis
        else:
            segundo_analisis = None
            bitacora_db.clasificacion = primer_analisis

        db.commit()

        # Paso 1: Verificar y traducir texto de bitácora (si está en inglés)
        try:
            resultado_traduccion = await verificar_y_traducir_bitacora(bitacora_db.id, db)
            if resultado_traduccion['traduccion_realizada']:
                print(f"✅ Bitácora {bitacora_db.id} traducida exitosamente")
        except Exception as e:
            print(f"❌ Error en traducción de bitácora {bitacora_db.id}: {e}")

        # Paso 2: Traducir clasificación de inglés a español (último paso)
        clasificacion_traducida = traducir_clasificacion(primer_analisis)
        if clasificacion_traducida != primer_analisis:
            bitacora_db.clasificacion = clasificacion_traducida
            db.commit()
            print(f"✅ Clasificación traducida: {primer_analisis[:50]}...")

        if segundo_analisis:
            return {"primer resultado": clasificacion_traducida, "segundo resultado": segundo_analisis}
        else:
            return {"primer resultado": clasificacion_traducida}

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
            "Fallas de Bomba HRSG" in b.clasificacion
        )]
        return {"message": "Consulta exitosa", "data": fallas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")







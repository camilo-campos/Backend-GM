from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelos.database import get_db
from modelos.modelos import GmBitacoraA, GmBitacoraB
from langchain_llm.analisis import llm_chain, llm_chain_2
from utils.traduccion_bitacoras import verificar_y_traducir_bitacora, traducir_clasificacion
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/gm-bitacoras", tags=["GM Bitacoras Bomba A"])


# ============================================
# SCHEMA PARA CLASIFICACION
# ============================================

class ClasificarBitacoraInput(BaseModel):
    id: int
    bitacora: str
    tabla: str = "a"  # "a" o "b"


# ============================================
# FUNCIONES AUXILIARES
# ============================================

async def _get_and_classify_gm_bitacoras_a(db: Session):
    """
    Obtiene todas las bitacoras de gm_bitacoras_a, clasifica las pendientes
    y retorna la lista completa.
    """
    bitacoras = (
        db.query(GmBitacoraA)
          .order_by(GmBitacoraA.id.desc())
          .all()
    )

    if not bitacoras:
        return []

    # Si WatsonX no esta disponible, solo retornar las bitacoras sin clasificar
    if llm_chain is None:
        return bitacoras

    # Filtrar sin clasificacion
    no_clasificadas = [b for b in bitacoras if b.clasificacion is None]
    if no_clasificadas:
        for b in no_clasificadas:
            primer_analisis = llm_chain.invoke({"bitacora": b.bitacora}).strip()
            # Si detecta fallo especifico
            if "HRSG Pump Failures" in primer_analisis:
                segundo_analisis = llm_chain_2.invoke({"bitacora": b.bitacora}).strip()
                b.clasificacion = primer_analisis
                b.alerta_aviso = segundo_analisis
            else:
                b.clasificacion = primer_analisis

            db.add(b)

        db.commit()

        # Traducir clasificaciones
        for b in no_clasificadas:
            db.refresh(b)

            if b.clasificacion:
                clasificacion_original = b.clasificacion
                b.clasificacion = traducir_clasificacion(clasificacion_original)
                if b.clasificacion != clasificacion_original:
                    db.add(b)

        db.commit()

    return bitacoras


async def _get_and_classify_gm_bitacoras_b(db: Session):
    """
    Obtiene todas las bitacoras de gm_bitacoras_b, clasifica las pendientes
    y retorna la lista completa.
    """
    bitacoras = (
        db.query(GmBitacoraB)
          .order_by(GmBitacoraB.id.desc())
          .all()
    )

    if not bitacoras:
        return []

    if llm_chain is None:
        return bitacoras

    no_clasificadas = [b for b in bitacoras if b.clasificacion is None]
    if no_clasificadas:
        for b in no_clasificadas:
            primer_analisis = llm_chain.invoke({"bitacora": b.bitacora}).strip()
            if "HRSG Pump Failures" in primer_analisis:
                segundo_analisis = llm_chain_2.invoke({"bitacora": b.bitacora}).strip()
                b.clasificacion = primer_analisis
                b.alerta_aviso = segundo_analisis
            else:
                b.clasificacion = primer_analisis

            db.add(b)

        db.commit()

        for b in no_clasificadas:
            db.refresh(b)
            if b.clasificacion:
                clasificacion_original = b.clasificacion
                b.clasificacion = traducir_clasificacion(clasificacion_original)
                if b.clasificacion != clasificacion_original:
                    db.add(b)

        db.commit()

    return bitacoras


# ============================================
# ENDPOINTS BOMBA A
# ============================================

@router.get(
    "/todas",
    summary="Obtener todas las bitacoras GM - Bomba A",
    description="""
Obtiene todas las bitacoras de gm_bitacoras_a con clasificacion automatica.

**Proceso automatico:**
- Las bitacoras sin clasificacion se analizan automaticamente con el modelo LLM
- Las clasificaciones se guardan para consultas futuras

**Informacion retornada por bitacora:**
- ID y texto de la bitacora
- Clasificacion (Fallas HRSG, Sin Fallas, etc.)
- Alerta/aviso adicional (si aplica)
- Timestamps
    """,
    response_description="Lista de todas las bitacoras clasificadas"
)
async def get_todas_gm_bitacoras(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_gm_bitacoras_a(db)
        return {"message": "Consulta exitosa", "data": bitacoras}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


@router.get(
    "/todas_fallas",
    summary="Obtener bitacoras con fallas HRSG - GM Bomba A",
    description="""
Obtiene las bitacoras de gm_bitacoras_a clasificadas como "HRSG Pump Failures".

**Filtro aplicado:**
Solo retorna bitacoras cuya clasificacion contiene:
- "HRSG Pump Failures" (en ingles)
- "Fallas de Bomba HRSG" o "Fallas de Bombas HRSG" (en espanol)
    """,
    response_description="Lista de bitacoras con fallas de bomba HRSG"
)
async def get_todas_gm_bitacoras_fallas(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_gm_bitacoras_a(db)
        fallas = [b for b in bitacoras if b.clasificacion and (
            "HRSG Pump Failures" in b.clasificacion or
            "Fallas de Bomba HRSG" in b.clasificacion or
            "Fallas de Bombas HRSG" in b.clasificacion
        )]
        return {"message": "Consulta exitosa", "data": fallas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


# ============================================
# ENDPOINTS BOMBA B
# ============================================

@router.get(
    "/b/todas",
    summary="Obtener todas las bitacoras GM - Bomba B",
    description="Obtiene las ultimas 40 bitacoras de gm_bitacoras_b con clasificacion automatica.",
    response_description="Lista de todas las bitacoras clasificadas"
)
async def get_todas_gm_bitacoras_b(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_gm_bitacoras_b(db)
        return {"message": "Consulta exitosa", "data": bitacoras}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


@router.get(
    "/b/todas_fallas",
    summary="Obtener bitacoras con fallas HRSG - GM Bomba B",
    description="Obtiene las bitacoras de gm_bitacoras_b clasificadas como HRSG Pump Failures.",
    response_description="Lista de bitacoras con fallas de bomba HRSG"
)
async def get_todas_gm_bitacoras_fallas_b(db: Session = Depends(get_db)):
    try:
        bitacoras = await _get_and_classify_gm_bitacoras_b(db)
        fallas = [b for b in bitacoras if b.clasificacion and (
            "HRSG Pump Failures" in b.clasificacion or
            "Fallas de Bomba HRSG" in b.clasificacion or
            "Fallas de Bombas HRSG" in b.clasificacion
        )]
        return {"message": "Consulta exitosa", "data": fallas}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")


# ============================================
# ENDPOINT PARA CLASIFICACION (usado por listener)
# ============================================

@router.post(
    "/clasificar-pendientes",
    summary="Clasificar bitacoras pendientes en lote",
    description="""
Clasifica todas las bitacoras pendientes (sin clasificacion) en lotes.

**Parametros opcionales:**
- tabla: "a" o "b" (default: "a")
- limite: Cantidad maxima a procesar (default: 50)

**Proceso:**
1. Obtiene bitacoras sin clasificacion
2. Analiza cada una con el LLM (mismas categorias que el sistema original)
3. Si detecta HRSG Pump Failures, ejecuta segundo analisis (AVISO/ALERTA)
4. Actualiza clasificacion en la base de datos
    """,
    response_description="Resultado del procesamiento en lote"
)
async def clasificar_pendientes(
    tabla: str = "a",
    limite: int = 50,
    db: Session = Depends(get_db)
):
    try:
        if llm_chain is None:
            raise HTTPException(status_code=503, detail="Servicio LLM no disponible")

        # Seleccionar modelo y tabla
        if tabla == "a":
            Model = GmBitacoraA
        else:
            Model = GmBitacoraB

        # Obtener pendientes
        pendientes = (
            db.query(Model)
            .filter(Model.clasificacion == None)
            .order_by(Model.id)
            .limit(limite)
            .all()
        )

        if not pendientes:
            return {"message": "No hay bitacoras pendientes", "procesadas": 0}

        resultados = []
        for b in pendientes:
            try:
                texto = b.bitacora or b.observaciones or "Sin observacion"
                primer_analisis = llm_chain.invoke({"bitacora": texto}).strip()

                if "HRSG Pump Failures" in primer_analisis:
                    segundo_analisis = llm_chain_2.invoke({"bitacora": texto}).strip()
                    b.clasificacion = primer_analisis
                    b.alerta_aviso = segundo_analisis
                else:
                    b.clasificacion = primer_analisis

                # Traducir clasificacion
                clasificacion_original = b.clasificacion
                b.clasificacion = traducir_clasificacion(clasificacion_original)

                db.add(b)
                resultados.append({
                    "id": b.id,
                    "clasificacion": b.clasificacion,
                    "alerta_aviso": b.alerta_aviso
                })

            except Exception as e:
                resultados.append({"id": b.id, "error": str(e)})

        db.commit()

        # Contar pendientes restantes
        restantes = db.query(Model).filter(Model.clasificacion == None).count()

        return {
            "message": f"Procesadas {len(resultados)} bitacoras",
            "procesadas": len(resultados),
            "pendientes_restantes": restantes,
            "resultados": resultados
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/clasificar",
    summary="Clasificar una bitacora especifica",
    description="""
Clasifica una bitacora especifica usando el LLM de WatsonX.
Este endpoint es llamado por el listener cuando detecta un nuevo INSERT.

**Entrada:**
- id: ID de la bitacora
- bitacora: Texto a clasificar
- tabla: "a" o "b" (indica gm_bitacoras_a o gm_bitacoras_b)

**Proceso:**
1. Analiza el texto con el LLM
2. Si detecta falla HRSG, ejecuta segundo analisis
3. Actualiza la clasificacion en la base de datos
    """,
    response_description="Resultado de la clasificacion"
)
async def clasificar_bitacora(data: ClasificarBitacoraInput, db: Session = Depends(get_db)):
    try:
        if llm_chain is None:
            raise HTTPException(status_code=503, detail="Servicio LLM no disponible")

        # Seleccionar tabla
        if data.tabla == "a":
            bitacora_db = db.query(GmBitacoraA).filter(GmBitacoraA.id == data.id).first()
        else:
            bitacora_db = db.query(GmBitacoraB).filter(GmBitacoraB.id == data.id).first()

        if not bitacora_db:
            raise HTTPException(status_code=404, detail="Bitacora no encontrada")

        # Clasificar
        primer_analisis = llm_chain.invoke({"bitacora": data.bitacora}).strip()

        if "HRSG Pump Failures" in primer_analisis:
            segundo_analisis = llm_chain_2.invoke({"bitacora": data.bitacora}).strip()
            bitacora_db.clasificacion = primer_analisis
            bitacora_db.alerta_aviso = segundo_analisis
        else:
            segundo_analisis = None
            bitacora_db.clasificacion = primer_analisis

        db.commit()

        # Traducir clasificacion
        clasificacion_traducida = traducir_clasificacion(primer_analisis)
        if clasificacion_traducida != primer_analisis:
            bitacora_db.clasificacion = clasificacion_traducida
            db.commit()

        return {
            "id": data.id,
            "clasificacion": bitacora_db.clasificacion,
            "alerta_aviso": bitacora_db.alerta_aviso,
            "procesado": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

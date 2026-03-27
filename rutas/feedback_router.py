from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from io import BytesIO
import uuid
import os

import ibm_boto3
from ibm_botocore.client import Config

from modelos.database import get_db
from modelos.modelos import Feedback
from auth.dependencies import get_current_user


router = APIRouter(prefix="/feedback", tags=["Feedback"])

ADMIN_EMAIL = "sd_fallabombas@generadora.cl"

# IBM Cloud Object Storage
COS_ENDPOINT = os.getenv("COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud")
COS_BUCKET = os.getenv("COS_BUCKET", "bucket-s2m0nf1559d6cx6")
COS_ACCESS_KEY = os.getenv("COS_ACCESS_KEY", "1fcf7c82f917457a9504e0be3b78b3b0")
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY", "f37b17df24bea3ac7043d0786b33bf73e967d8e2be38efc5")

cos_client = ibm_boto3.client(
    "s3",
    endpoint_url=COS_ENDPOINT,
    aws_access_key_id=COS_ACCESS_KEY,
    aws_secret_access_key=COS_SECRET_KEY,
)


class TipoFeedback(str, Enum):
    funcionamiento = "funcionamiento"
    datos = "datos"
    felicidades = "felicidades"


class EstadoFeedback(str, Enum):
    pendiente = "pendiente"
    revisado = "revisado"
    resuelto = "resuelto"


class FeedbackActualizarEstado(BaseModel):
    estado: EstadoFeedback


async def _subir_imagen_cos(file: UploadFile) -> str:
    """Sube una imagen a IBM COS y retorna la key del objeto."""
    contenido = await file.read()
    extension = file.filename.split(".")[-1] if "." in file.filename else "png"
    key = f"feedback/{uuid.uuid4().hex}.{extension}"

    cos_client.put_object(
        Bucket=COS_BUCKET,
        Key=key,
        Body=BytesIO(contenido),
        ContentType=file.content_type or "image/png",
    )

    # Guardar solo la key, no la URL completa
    return key


def _generar_url_imagen(key: str) -> str:
    """Genera una presigned URL temporal (válida 7 días) para una imagen en COS."""
    if not key:
        return None
    # Si es una URL completa vieja, extraer solo la key
    if key.startswith("http"):
        key = key.split(f"{COS_BUCKET}/")[-1]
    return cos_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": COS_BUCKET, "Key": key},
        ExpiresIn=604800,  # 7 días
    )


@router.post(
    "/",
    summary="Crear un nuevo feedback",
    description="Permite al usuario enviar feedback con imagen opcional.",
)
async def crear_feedback(
    tipo: TipoFeedback = Form(...),
    mensaje: str = Form(..., min_length=1, max_length=2000),
    imagen: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        imagen_url = None
        if imagen and imagen.filename:
            imagen_url = await _subir_imagen_cos(imagen)

        nuevo = Feedback(
            usuario_email=current_user.get("email") or current_user.get("sub", "desconocido"),
            tipo=tipo.value,
            mensaje=mensaje,
            estado="pendiente",
            imagen_url=imagen_url,
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        return {
            "mensaje": "Feedback creado exitosamente",
            "feedback": {
                "id": nuevo.id,
                "tipo": nuevo.tipo,
                "estado": nuevo.estado,
                "imagen_url": _generar_url_imagen(nuevo.imagen_url),
                "fecha_creacion": nuevo.fecha_creacion.isoformat() if nuevo.fecha_creacion else None,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear feedback: {str(e)}")


@router.get(
    "/todos",
    summary="Listar feedback (solo admin)",
    description="Solo sd_fallabombas@generadora.cl puede ver todos los feedback.",
)
async def listar_feedback(
    tipo: Optional[TipoFeedback] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoFeedback] = Query(None, description="Filtrar por estado"),
    dias: Optional[int] = Query(None, description="Ultimos N dias", ge=1),
    email: Optional[str] = Query(None, description="Email del usuario autenticado"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_email = email or current_user.get("email", "")
    es_admin = user_email == ADMIN_EMAIL or current_user.get("auth_method") == "api_key"
    if not es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver los feedback")

    try:
        query = db.query(Feedback)

        if tipo:
            query = query.filter(Feedback.tipo == tipo.value)
        if estado:
            query = query.filter(Feedback.estado == estado.value)
        if dias:
            fecha_limite = datetime.now() - timedelta(days=dias)
            query = query.filter(Feedback.fecha_creacion >= fecha_limite)

        registros = query.order_by(Feedback.fecha_creacion.desc()).all()

        return {
            "total": len(registros),
            "feedback": [
                {
                    "id": r.id,
                    "usuario_email": r.usuario_email,
                    "tipo": r.tipo,
                    "mensaje": r.mensaje,
                    "estado": r.estado,
                    "imagen_url": _generar_url_imagen(r.imagen_url),
                    "fecha_creacion": r.fecha_creacion.isoformat() if r.fecha_creacion else None,
                    "fecha_actualizacion": r.fecha_actualizacion.isoformat() if r.fecha_actualizacion else None,
                }
                for r in registros
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar feedback: {str(e)}")


@router.patch(
    "/{feedback_id}/estado",
    summary="Actualizar estado de feedback (solo admin)",
    description="Solo sd_fallabombas@generadora.cl puede cambiar el estado.",
)
async def actualizar_estado_feedback(
    feedback_id: int,
    datos: FeedbackActualizarEstado,
    email: Optional[str] = Query(None, description="Email del usuario autenticado"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_email = email or current_user.get("email", "")
    es_admin = user_email == ADMIN_EMAIL or current_user.get("auth_method") == "api_key"
    if not es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar feedback")

    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback no encontrado")

        feedback.estado = datos.estado.value
        feedback.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(feedback)

        return {
            "mensaje": "Estado actualizado exitosamente",
            "feedback": {
                "id": feedback.id,
                "estado": feedback.estado,
                "fecha_actualizacion": feedback.fecha_actualizacion.isoformat() if feedback.fecha_actualizacion else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado: {str(e)}")


@router.delete(
    "/{feedback_id}",
    summary="Eliminar un feedback (solo admin)",
    description="Solo sd_fallabombas@generadora.cl puede eliminar feedback.",
)
async def eliminar_feedback(
    feedback_id: int,
    email: Optional[str] = Query(None, description="Email del usuario autenticado"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_email = email or current_user.get("email", "")
    es_admin = user_email == ADMIN_EMAIL or current_user.get("auth_method") == "api_key"
    if not es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar feedback")

    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()

        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback no encontrado")

        db.delete(feedback)
        db.commit()

        return {"mensaje": f"Feedback {feedback_id} eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar feedback: {str(e)}")

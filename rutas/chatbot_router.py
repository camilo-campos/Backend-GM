from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import asyncio
import json
import os
import logging

from modelos.database import get_db
from modelos.modelos import ChatHistorial
from auth.dependencies import get_current_user
from langchain_llm.rag_engine import rag

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

CHATBOT_MODEL = "ibm/granite-3-8b-instruct"

_chatbot_llm = None
try:
    from langchain_ibm import WatsonxLLM
    _proyecto_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("project_id")
    _api_key = os.getenv("WATSONX_APIKEY") or os.getenv("apikey")
    if _proyecto_id and _api_key:
        _chatbot_llm = WatsonxLLM(
            model_id=CHATBOT_MODEL,
            url="https://us-south.ml.cloud.ibm.com",
            project_id=_proyecto_id,
            apikey=_api_key,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 256,
                "min_new_tokens": 0,
                "repetition_penalty": 1.1,
            },
        )
        logger.info(f"Chatbot WatsonX inicializado: {CHATBOT_MODEL}")
    else:
        logger.warning("Chatbot: faltan credenciales WATSONX_PROJECT_ID / WATSONX_APIKEY")
except Exception as e:
    logger.warning(f"Chatbot: no se pudo inicializar WatsonX: {e}")

# ─── Respuestas rapidas sin LLM (0ms) ───
_SALUDOS = {"hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "hi", "hello", "que tal", "buenas"}

def _respuesta_rapida(pregunta: str) -> str:
    """Retorna respuesta directa para saludos y preguntas triviales. None si necesita LLM."""
    pregunta_clean = pregunta.lower().strip().rstrip("!?.,:;")
    if pregunta_clean in _SALUDOS:
        return "Hola! En que puedo ayudarte sobre la aplicacion?"
    if pregunta_clean in ("gracias", "muchas gracias", "thanks"):
        return "De nada! Si tienes otra pregunta, aqui estoy."
    if pregunta_clean in ("chao", "adios", "bye", "hasta luego"):
        return "Hasta luego! Si necesitas algo mas, no dudes en preguntar."
    return None

# ─── System prompt base (corto, el RAG inyecta contexto relevante) ───
SYSTEM_PROMPT = """Eres un asistente virtual del Dashboard GM, una aplicacion de monitoreo predictivo de bombas de agua en la planta termoelectrica Nueva Renca (HRSG).

REGLAS:
- Responde en espanol, conciso y directo. Maximo 2-3 oraciones.
- Si el usuario saluda, responde con un saludo breve y pregunta en que puedes ayudar.
- Responde SOLO sobre la aplicacion usando la INFORMACION RELEVANTE proporcionada.
- Si no tienes informacion suficiente, di que no tienes esa informacion disponible.
- NO inventes datos ni umbrales. Usa solo la informacion proporcionada.
- Responde solo lo que se pregunta, no agregues informacion extra."""


CONTEXTO_PAGINAS = {
    "vision_general": "El usuario esta en Vision General, ve alertas recientes y bitacoras de ambas bombas.",
    "anomalias_a": "El usuario esta en Anomalias Bomba A, ve graficos de sensores con valores normales (verde) y anomalias (rojo).",
    "anomalias_b": "El usuario esta en Anomalias Bomba B, mismos graficos para sensores de Bomba B.",
    "sensores_a": "El usuario esta en Sensores Bomba A, ve datos en tiempo real de todos los sensores.",
    "sensores_b": "El usuario esta en Sensores Bomba B, datos en tiempo real de sensores Bomba B.",
    "bitacoras_a": "El usuario esta en Bitacoras Bomba A, ve registros operativos clasificados por IA.",
    "bitacoras_b": "El usuario esta en Bitacoras Bomba B.",
    "feedback": "El usuario esta en Feedback, puede enviar comentarios sobre funcionamiento, datos o felicidades.",
}


class PreguntaInput(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=1000)
    pagina_actual: Optional[str] = None
    session_id: str = Field(..., min_length=1)


def _format_llama(system: str, historial: list, pregunta: str) -> str:
    """Formato para meta-llama/llama-3-3-70b-instruct"""
    prompt = f"<|begin_of_text|>\n<|start_header_id|>system<|end_header_id|>\n{system}<|eot_id|>\n"
    for msg in historial[-10:]:
        role = "user" if msg.rol == "user" else "assistant"
        prompt += f"<|start_header_id|>{role}<|end_header_id|>\n{msg.mensaje}<|eot_id|>\n"
    prompt += f"<|start_header_id|>user<|end_header_id|>\n{pregunta}<|eot_id|>\n"
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
    return prompt


def _format_granite(system: str, historial: list, pregunta: str) -> str:
    """Formato para ibm/granite-3-3-8b-instruct y ibm/granite-3-8b-instruct"""
    prompt = f"<|start_of_role|>system<|end_of_role|>{system}<|end_of_text|>\n"
    for msg in historial[-10:]:
        role = "user" if msg.rol == "user" else "assistant"
        prompt += f"<|start_of_role|>{role}<|end_of_role|>{msg.mensaje}<|end_of_text|>\n"
    prompt += f"<|start_of_role|>user<|end_of_role|>{pregunta}<|end_of_text|>\n"
    prompt += "<|start_of_role|>assistant<|end_of_role|>"
    return prompt


def _format_mistral(system: str, historial: list, pregunta: str) -> str:
    """Formato para mistralai/mistral-small-3-1-24b-instruct-2503"""
    prompt = f"<s>[SYSTEM_PROMPT]{system}[/SYSTEM_PROMPT]"
    for msg in historial[-10:]:
        if msg.rol == "user":
            prompt += f"[INST]{msg.mensaje}[/INST]"
        else:
            prompt += f"{msg.mensaje}</s>"
    prompt += f"[INST]{pregunta}[/INST]"
    return prompt


def _construir_prompt(pregunta: str, pagina_actual: str, historial: list) -> str:
    """Construye el prompt usando RAG para inyectar solo informacion relevante."""
    # Buscar chunks relevantes via RAG
    chunks_relevantes = rag.buscar(pregunta, top_k=5)

    # Determinar intencion para logging
    intencion = "tecnico" if chunks_relevantes else "general"

    # Construir system con chunks
    system = SYSTEM_PROMPT
    if chunks_relevantes:
        system += "\n\nINFORMACION RELEVANTE:\n"
        for chunk in chunks_relevantes:
            system += f"- {chunk}\n"

    # Agregar contexto de pagina
    if pagina_actual and pagina_actual in CONTEXTO_PAGINAS:
        system += f"\nCONTEXTO ACTUAL: {CONTEXTO_PAGINAS[pagina_actual]}\n"

    # Seleccionar formato segun modelo
    model_lower = CHATBOT_MODEL.lower()
    if "granite" in model_lower:
        prompt = _format_granite(system, historial, pregunta)
    elif "mistral" in model_lower:
        prompt = _format_mistral(system, historial, pregunta)
    else:
        prompt = _format_llama(system, historial, pregunta)

    logger.info(f"[CHATBOT] Formato: {'granite' if 'granite' in model_lower else 'mistral' if 'mistral' in model_lower else 'llama'} | Chunks: {len(chunks_relevantes)}")
    return prompt, intencion


@router.post(
    "/preguntar",
    summary="Hacer una pregunta al chatbot",
    description="Envia una pregunta sobre la aplicacion y recibe una respuesta en streaming (SSE).",
)
async def preguntar(
    datos: PreguntaInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import time as _t
    _t0 = _t.time()

    logger.info(f"[CHATBOT] Pregunta: '{datos.pregunta}' | Pagina: {datos.pagina_actual} | Session: {datos.session_id[:8]}...")

    # Respuesta rapida para saludos (sin LLM)
    respuesta_rapida = _respuesta_rapida(datos.pregunta)
    if respuesta_rapida:
        logger.info(f"[CHATBOT] Respuesta rapida: {(_t.time()-_t0)*1000:.0f}ms | '{respuesta_rapida}'")
        # Guardar en historial
        db.add(ChatHistorial(session_id=datos.session_id, rol="user", mensaje=datos.pregunta, pagina=datos.pagina_actual))
        db.add(ChatHistorial(session_id=datos.session_id, rol="assistant", mensaje=respuesta_rapida, pagina=datos.pagina_actual))
        db.commit()

        async def stream_rapido():
            yield f"data: {json.dumps({'token': respuesta_rapida}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(stream_rapido(), media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})

    if _chatbot_llm is None:
        logger.error("[CHATBOT] WatsonX no disponible")
        raise HTTPException(503, "WatsonX no esta disponible. Verificar credenciales WATSONX_PROJECT_ID y WATSONX_APIKEY.")

    # Cargar historial de la sesion
    historial = db.query(ChatHistorial).filter(
        ChatHistorial.session_id == datos.session_id
    ).order_by(ChatHistorial.timestamp.asc()).limit(20).all()
    logger.info(f"[CHATBOT] Historial: {len(historial)} mensajes previos")

    # Construir prompt
    prompt, intencion = _construir_prompt(datos.pregunta, datos.pagina_actual, historial)
    logger.info(f"[CHATBOT] Intencion: {intencion.upper()} | Prompt: {len(prompt)} chars (~{len(prompt)//4} tokens)")

    # Guardar pregunta del usuario
    msg_user = ChatHistorial(
        session_id=datos.session_id,
        rol="user",
        mensaje=datos.pregunta,
        pagina=datos.pagina_actual,
    )
    db.add(msg_user)
    db.commit()

    _t1 = _t.time()
    logger.info(f"[CHATBOT] Preparacion: {(_t1-_t0)*1000:.0f}ms | Enviando a WatsonX...")

    # Streaming con SSE
    async def generar_stream():
        respuesta_completa = ""
        _t_stream = _t.time()
        _first_token = True
        try:
            for chunk in _chatbot_llm.stream(prompt):
                if chunk:
                    if _first_token:
                        logger.info(f"[CHATBOT] Primer token: {(_t.time()-_t1)*1000:.0f}ms desde envio")
                        _first_token = False
                    # Agregar salto de linea despues de punto seguido de espacio
                    chunk_formateado = chunk.replace(". ", ".\n")
                    respuesta_completa += chunk
                    data = json.dumps({"token": chunk_formateado}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
        except Exception as e:
            logger.error(f"[CHATBOT] Error streaming WatsonX: {e}")
            error_msg = "Lo siento, ocurrio un error al procesar tu pregunta."
            respuesta_completa = error_msg
            yield f"data: {json.dumps({'token': error_msg})}\n\n"
        finally:
            _t_end = _t.time()
            _total = _t_end - _t0
            _tokens_aprox = len(respuesta_completa.split())
            logger.info(f"[CHATBOT] Respuesta completa: {len(respuesta_completa)} chars, ~{_tokens_aprox} tokens")
            logger.info(f"[CHATBOT] Tiempo total: {_total*1000:.0f}ms | Respuesta: '{respuesta_completa[:100]}...'")

            # Guardar respuesta completa en historial
            if respuesta_completa.strip():
                try:
                    from modelos.database import SessionLocal
                    db_save = SessionLocal()
                    msg_assistant = ChatHistorial(
                        session_id=datos.session_id,
                        rol="assistant",
                        mensaje=respuesta_completa.strip(),
                        pagina=datos.pagina_actual,
                    )
                    db_save.add(msg_assistant)
                    db_save.commit()
                    db_save.close()
                    logger.info(f"[CHATBOT] Historial guardado OK")
                except Exception as e:
                    logger.error(f"[CHATBOT] Error guardando historial: {e}")

            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generar_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/preguntar-sync",
    summary="Hacer una pregunta al chatbot (sin streaming)",
    description="Version sin streaming para clientes que no soportan SSE.",
)
async def preguntar_sync(
    datos: PreguntaInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if _chatbot_llm is None:
        raise HTTPException(503, "WatsonX no esta disponible. Verificar credenciales WATSONX_PROJECT_ID y WATSONX_APIKEY.")

    # Cargar historial
    historial = db.query(ChatHistorial).filter(
        ChatHistorial.session_id == datos.session_id
    ).order_by(ChatHistorial.timestamp.asc()).limit(20).all()

    # Construir prompt y ejecutar
    prompt, intencion = _construir_prompt(datos.pregunta, datos.pagina_actual, historial)
    logger.info(f"[CHATBOT-SYNC] Intencion: {intencion.upper()} | Prompt: {len(prompt)} chars")

    loop = asyncio.get_event_loop()
    respuesta = await loop.run_in_executor(None, lambda: _chatbot_llm.invoke(prompt))
    respuesta = respuesta.strip()

    # Guardar en historial
    db.add(ChatHistorial(session_id=datos.session_id, rol="user", mensaje=datos.pregunta, pagina=datos.pagina_actual))
    db.add(ChatHistorial(session_id=datos.session_id, rol="assistant", mensaje=respuesta, pagina=datos.pagina_actual))
    db.commit()

    return {"respuesta": respuesta, "session_id": datos.session_id}

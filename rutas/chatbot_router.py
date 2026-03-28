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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

CHATBOT_MODEL = "ibm/granite-3-3-8b-instruct"

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

# ─── PROMPT GENERAL: uso de la app, navegacion, funcionalidades ───
PROMPT_GENERAL = """
Eres un asistente virtual del Dashboard GM, una aplicacion de monitoreo predictivo de bombas de agua en la planta termoelectrica Nueva Renca.

PAGINAS DE LA APLICACION:
- Vision General: resumen de alertas recientes de ambas bombas y bitacoras con alertas.
- Analisis de Anomalias A/B: graficos de cada sensor con valores normales (verde) y anomalias (rojo).
- Analisis de Sensores A/B: datos en tiempo real de todos los sensores, valores actuales y tendencias.
- Analisis de Bitacoras A/B: registros operativos de los operadores, clasificados por IA.
- Feedback: enviar comentarios sobre funcionamiento, datos o felicidades. Se pueden adjuntar imagenes.

CONCEPTOS CLAVE:
- La planta tiene 2 bombas (A y B). Solo una esta activa a la vez.
- Cada bomba tiene ~25 sensores monitoreados en tiempo real (datos cada minuto).
- Cada sensor se clasifica con IA: 1 = Normal, -1 = Anomalia.
- Las anomalias se acumulan en 8 horas y generan alertas: AVISO (56+), ALERTA (86+), CRITICA (116+).
- Despues de una CRITICA el contador se reinicia.
- Las bitacoras son textos de operadores clasificados por IA en categorias y niveles (ALERTA/AVISO).
- Existe una prediccion global (Random Forest) que usa todos los sensores para predecir falla general.

REGLAS:
- Responde en espanol, conciso y directo. Maximo 2-3 oraciones.
- Si el usuario saluda, responde con un saludo breve y pregunta en que puedes ayudar.
- NO describas la pagina actual sin que te lo pidan.
- Responde solo lo que se pregunta.
- Si preguntan algo fuera de la app, indica amablemente que solo ayudas con la aplicacion.
"""

# ─── PROMPT TECNICO: sensores, valores, umbrales, datos especificos ───
PROMPT_TECNICO = """
Eres un asistente tecnico del Dashboard GM, especializado en los sensores y datos de la planta termoelectrica Nueva Renca.

SENSORES BOMBA A (25 sensores, 19 para prediccion global):
Principales:
  1. Corriente del motor - Amperios - Umbrales: 101/162/202
  2. Presion de agua AP - bar - Umbrales: 118/188/235
  3. MW brutos generacion gas - MW - Umbrales: 56/86/116
  4. Temperatura ambiental - Celsius - Umbrales: 56/86/116
  5. Temperatura descanso bomba 1A - Celsius - Umbrales: 86/137/171
  6. Temperatura empuje bomba 1A - Celsius - Umbrales: 56/86/116
  7. Temperatura motor bomba 1A - Celsius - Umbrales: 56/86/116
  8. Vibracion axial descanso - mm/s - Umbrales: 56/86/116
  9. Voltaje barra 6.6KV - kV - Umbrales: 56/86/116
  10. Excentricidad bomba - mm - Umbrales: 56/86/116
  11. Flujo agua domo AP - m3/h - Umbrales: 56/86/116
  12. Flujo domo AP compensado - m3/h - Umbrales: 56/86/116
  13. Flujo agua domo MP - m3/h - Umbrales: 56/86/116
  14. Flujo agua recalentador - m3/h - Umbrales: 56/86/116
  15. Flujo agua vapor alta - m3/h - Umbrales: 56/86/116
  16. Posicion valvula recirculacion - % - Umbrales: 56/86/116
  17. Presion agua MP - bar - Umbrales: 56/86/116
  18. Presion succion BAA - bar - Umbrales: 56/86/116
  19. Temperatura estator - Celsius - Umbrales: 56/86/116
Extra (solo monitoreo individual):
  20. Flujo salida 12FPMFC - m3/h
  21. Vibracion X descanso interno - um - Umbrales: 67/106/133
  22. Vibracion Y descanso interno - um
  23. Vibracion X descanso externo - um - Umbrales: 60/96/120
  24. Vibracion Y descanso externo - um
  25. Temperatura agua alimentacion domo MP - Celsius

SENSORES BOMBA B (26 sensores, 15 para prediccion global):
Principales:
  1. Corriente motor 1B - Amperios - Umbrales: 56/86/116
  2. Presion agua econ AP - bar - Umbrales: 56/86/116
  3. Temperatura ambiental - Celsius (compartido) - Umbrales: 56/86/116
  4. Excentricidad bomba 1B - mm - Umbrales: 56/86/116
  5. Flujo descarga AP - m3/h - Umbrales: 66/106/132
  6. Flujo agua domo AP - m3/h - Umbrales: 56/86/116
  7. Flujo agua domo MP - m3/h - Umbrales: 56/86/116
  8. Flujo agua recalentador - m3/h - Umbrales: 56/86/116
  9. Flujo agua vapor alta AP - m3/h - Umbrales: 56/86/116
  10. Temperatura agua alimentacion AP - Celsius - Umbrales: 56/86/116
  11. Temperatura estator motor 1B - Celsius - Umbrales: 56/86/116
  12. Vibracion axial empuje 1B - mm/s - Umbrales: 56/86/116
  13. Vibracion X descanso interno 1B - um - Umbrales: 67/106/133
  14. Vibracion Y descanso interno 1B - um - Umbrales: 56/86/116
  15. Voltaje barra 6.6KV - kV - Umbrales: 56/86/116
Extra:
  16-26. Temperaturas descanso, vibraciones externas, presion succion, posicion valvula, MW gas, flujos adicionales.

SENSORES COMPARTIDOS (ambas bombas): Temperatura ambiental, MW brutos gas, Voltaje barra 6.6KV.

UMBRALES (formato AVISO/ALERTA/CRITICA):
- Representan cantidad de anomalias en 8 horas para cada nivel de alerta.
- Ejemplo: Corriente Bomba A 101/162/202 = 101 anomalias para AVISO, 162 para ALERTA, 202 para CRITICA.
- Umbral base: 56/86/116 (mayoria de sensores).
- Sensores criticos (corriente, presion Bomba A) tienen umbrales mas altos.

CLASIFICACION ML:
- Isolation Forest por sensor: 1=Normal, -1=Anomalia.
- Random Forest global: usa todos los sensores principales, predice falla general (0=Normal, 1=Falla).
- Bomba A usa 19 features, Bomba B usa 15 features.

REGLAS:
- Responde en espanol, conciso y tecnico.
- Si el usuario pregunta por un sensor, incluye su unidad de medida y umbrales.
- Contextualiza segun la pagina donde esta el usuario.
- Responde solo lo que se pregunta.
"""

# ─── Keywords para detectar intencion ───
_KEYWORDS_TECNICO = [
    "sensor", "sensores", "valor", "valores", "anomalia", "anomalias", "alerta", "alertas",
    "umbral", "umbrales", "grafico", "graficos", "clasificacion", "clasificaciones",
    "-1", "normal", "critica", "aviso",
    "corriente", "vibracion", "temperatura", "presion", "flujo", "voltaje",
    "excentricidad", "estator", "recalentador", "domo", "valvula",
    "bomba a", "bomba b", "bomba 1a", "bomba 1b",
    "isolation forest", "random forest", "modelo", "prediccion",
    "mw", "bar", "celsius", "amperios", "mm/s",
    "bitacora", "bitacoras", "hrsg",
    "cuantos", "cuantas", "que mide", "que significa", "que es",
]


def _detectar_intencion(pregunta: str) -> str:
    """Detecta si la pregunta es sobre uso general o datos tecnicos."""
    pregunta_lower = pregunta.lower()
    for kw in _KEYWORDS_TECNICO:
        if kw in pregunta_lower:
            return "tecnico"
    return "general"


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
    """Construye el prompt seleccionando GENERAL o TECNICO y el formato segun el modelo."""
    intencion = _detectar_intencion(pregunta)
    system = PROMPT_TECNICO if intencion == "tecnico" else PROMPT_GENERAL

    # Agregar contexto de pagina al system prompt
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

    logger.info(f"[CHATBOT] Formato: {'granite' if 'granite' in model_lower else 'mistral' if 'mistral' in model_lower else 'llama'}")
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

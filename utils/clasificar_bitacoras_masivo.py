"""
Script para clasificar bitacoras existentes en lote usando WatsonX LLM
"""

import psycopg2
import json
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print(f"[{datetime.now()}] Iniciando clasificacion masiva de bitacoras...")

# Conectar a WatsonX
print(f"[{datetime.now()}] Conectando a WatsonX...")
try:
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai import Credentials

    credentials = Credentials(
        url=os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.environ.get("WATSONX_APIKEY")
    )

    model = ModelInference(
        model_id="ibm/granite-3-3-8b-instruct",
        credentials=credentials,
        project_id=os.environ.get("WATSONX_PROJECT_ID"),
        params={"max_new_tokens": 150, "temperature": 0.1}
    )
    print(f"[{datetime.now()}] WatsonX conectado OK")
except Exception as e:
    print(f"[{datetime.now()}] Error conectando WatsonX: {e}")
    sys.exit(1)

# Conectar a BD
print(f"[{datetime.now()}] Conectando a PostgreSQL...")
conn = psycopg2.connect(
    dbname="ibmclouddb",
    user="ibm_cloud_b5b9ac51_d025_4f9b_87db_83ea915f7533",
    password="Jzy68YQhoFvdLxjuToK6rbK589uFauyt",
    host="c9ebb3a5-1401-420c-b4a0-089168266b2d.c5kmhkid0ujpmrucb800.databases.appdomain.cloud",
    port=30226,
    sslmode="require"
)
conn.autocommit = True
cur = conn.cursor()
print(f"[{datetime.now()}] PostgreSQL conectado OK")

# Prompt para clasificacion
PROMPT = """Analiza esta observacion de bitacora de planta electrica y clasifica.

Observacion: {obs}

Responde SOLO en formato JSON valido:
{{"clasificacion": "FALLA_CRITICA|OPERACION_NORMAL|SOLICITUD_DESPACHO|MANTENIMIENTO|ALARMA|INFORMATIVO", "prioridad": "ALTA|MEDIA|BAJA"}}"""

# Obtener total pendientes
cur.execute("SELECT COUNT(*) FROM gm_bitacoras_a WHERE clasificacion IS NULL")
total_pendientes = cur.fetchone()[0]
print(f"[{datetime.now()}] Total pendientes: {total_pendientes}")

# Procesar en lotes
BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 50
print(f"[{datetime.now()}] Procesando lote de {BATCH_SIZE} bitacoras...")

cur.execute(f"SELECT id, bitacora FROM gm_bitacoras_a WHERE clasificacion IS NULL ORDER BY id LIMIT {BATCH_SIZE}")
pendientes = cur.fetchall()

exitosos = 0
errores = 0

for i, (id_bit, texto) in enumerate(pendientes):
    try:
        # Preparar texto
        texto_limpio = (texto or "Sin observacion")[:500]

        # Clasificar con LLM
        prompt = PROMPT.format(obs=texto_limpio)
        response = model.generate_text(prompt).strip()

        # Parsear respuesta JSON
        try:
            # Limpiar markdown si viene
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            resultado = json.loads(response)
            clasificacion = resultado.get("clasificacion", "INFORMATIVO")
            # Tomar solo la primera opcion si viene con |
            if "|" in clasificacion:
                clasificacion = clasificacion.split("|")[0]
            prioridad = resultado.get("prioridad", "MEDIA")
            if "|" in prioridad:
                prioridad = prioridad.split("|")[0]
        except json.JSONDecodeError:
            clasificacion = "INFORMATIVO"
            prioridad = "MEDIA"

        # Actualizar BD
        cur.execute("""
            UPDATE gm_bitacoras_a
            SET clasificacion = %s, prioridad = %s, procesado_llm = TRUE, fecha_procesado = NOW()
            WHERE id = %s
        """, (clasificacion, prioridad, id_bit))

        exitosos += 1

        # Mostrar progreso
        if (i + 1) % 10 == 0 or (i + 1) == len(pendientes):
            print(f"[{datetime.now()}] Progreso: {i+1}/{len(pendientes)} | OK: {exitosos} | Err: {errores} | Clase: {clasificacion}")

        # Rate limiting - esperar entre requests
        time.sleep(0.3)

    except Exception as e:
        errores += 1
        print(f"[{datetime.now()}] Error id={id_bit}: {str(e)[:50]}")
        time.sleep(1)  # Esperar mas si hay error

cur.close()
conn.close()

print(f"")
print(f"[{datetime.now()}] === LOTE COMPLETADO ===")
print(f"  Procesados: {exitosos + errores}")
print(f"  Exitosos: {exitosos}")
print(f"  Errores: {errores}")
print(f"  Pendientes restantes: {total_pendientes - exitosos}")

"""
Script para clasificar bitacoras existentes usando el sistema CORRECTO de LLM
Usa el mismo llm_chain y llm_chain_2 que usa el router gm_bitacoras_router.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from modelos.database import SessionLocal
from modelos.modelos import GmBitacoraA, GmBitacoraB
from langchain_llm.analisis import llm_chain, llm_chain_2
from utils.traduccion_bitacoras import traducir_clasificacion
import time

print(f"[{datetime.now()}] Iniciando clasificacion de bitacoras existentes...")

# Verificar LLM
if llm_chain is None:
    print(f"[{datetime.now()}] ERROR: LLM no disponible")
    sys.exit(1)

print(f"[{datetime.now()}] LLM conectado OK")

# Conectar a BD
db = SessionLocal()

# Parametros
TABLA = sys.argv[1] if len(sys.argv) > 1 else "a"
BATCH_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 50

Model = GmBitacoraA if TABLA == "a" else GmBitacoraB

# Contar pendientes
total_pendientes = db.query(Model).filter(Model.clasificacion == None).count()
print(f"[{datetime.now()}] Total pendientes en tabla {TABLA}: {total_pendientes}")

if total_pendientes == 0:
    print(f"[{datetime.now()}] No hay bitacoras pendientes")
    db.close()
    sys.exit(0)

# Obtener lote
print(f"[{datetime.now()}] Procesando lote de {BATCH_SIZE}...")
pendientes = (
    db.query(Model)
    .filter(Model.clasificacion == None)
    .order_by(Model.id)
    .limit(BATCH_SIZE)
    .all()
)

exitosos = 0
errores = 0

for i, b in enumerate(pendientes):
    try:
        texto = b.bitacora or b.observaciones or "Sin observacion"

        # Clasificar con llm_chain (sistema correcto)
        primer_analisis = llm_chain.invoke({"bitacora": texto}).strip()

        # Si detecta HRSG Pump Failures, usar llm_chain_2
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
        db.commit()  # Guardar cada registro inmediatamente
        exitosos += 1

        # Mostrar progreso
        if (i + 1) % 10 == 0 or (i + 1) == len(pendientes):
            print(f"[{datetime.now()}] Progreso: {i+1}/{len(pendientes)} | OK: {exitosos} | Err: {errores}")
            print(f"  Ultima: {b.clasificacion[:60]}...")

        # Rate limiting
        time.sleep(0.5)

    except Exception as e:
        errores += 1
        print(f"[{datetime.now()}] Error id={b.id}: {str(e)[:80]}")
        time.sleep(1)

db.close()

print(f"")
print(f"[{datetime.now()}] === LOTE COMPLETADO ===")
print(f"  Procesados: {exitosos + errores}")
print(f"  Exitosos: {exitosos}")
print(f"  Errores: {errores}")
print(f"  Pendientes restantes: {total_pendientes - exitosos}")

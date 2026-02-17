"""
Script para verificar las alertas generadas y probar los nuevos endpoints.
Consulta las alertas y prueba los endpoints de datos de anomalia.

Uso:
1. Asegurate de que el backend este corriendo
2. Ejecutar: python utils/verificar_alertas.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def consultar_todas_alertas():
    """Consulta todas las alertas del sistema"""
    print("=" * 60)
    print("CONSULTANDO ALERTAS")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/alertas_umbral/todas_alertas", timeout=10)
        response.raise_for_status()
        data = response.json()

        alertas = data.get("data", [])
        print(f"\nTotal alertas: {len(alertas)}")

        # Separar alertas con y sin timestamps
        con_timestamps = [a for a in alertas if a.get("tiene_datos_anomalia")]
        sin_timestamps = [a for a in alertas if not a.get("tiene_datos_anomalia")]

        print(f"Con datos de anomalia: {len(con_timestamps)}")
        print(f"Sin datos de anomalia: {len(sin_timestamps)}")

        return alertas, con_timestamps

    except Exception as e:
        print(f"[!] Error: {e}")
        return [], []


def probar_endpoint_datos_anomalia(alerta_id):
    """Prueba el endpoint de datos de anomalia"""
    print(f"\n  Probando: GET /{alerta_id}/datos_anomalia")

    try:
        response = requests.get(
            f"{BASE_URL}/alertas_umbral/{alerta_id}/datos_anomalia",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            periodo = data.get("periodo_anomalo", {})
            stats = data.get("estadisticas", {})
            datos = data.get("datos", [])

            print(f"    [OK] Respuesta exitosa")
            print(f"    Periodo: {periodo.get('timestamp_inicio')} -> {periodo.get('timestamp_fin')}")
            print(f"    Duracion: {periodo.get('duracion_minutos')} minutos")
            print(f"    Registros: {stats.get('total_registros')}")
            print(f"    Anomalias: {stats.get('registros_anomalos')} ({stats.get('porcentaje_anomalias')}%)")

            return True
        elif response.status_code == 400:
            print(f"    [!] Sin datos de anomalia para esta alerta")
            return False
        else:
            print(f"    [!] Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"    [!] Error: {e}")
        return False


def probar_endpoint_contexto(alerta_id, minutos_antes=30, minutos_despues=30):
    """Prueba el endpoint de datos con contexto extendido"""
    print(f"\n  Probando: GET /{alerta_id}/datos_anomalia_contexto")
    print(f"    Params: minutos_antes={minutos_antes}, minutos_despues={minutos_despues}")

    try:
        response = requests.get(
            f"{BASE_URL}/alertas_umbral/{alerta_id}/datos_anomalia_contexto",
            params={
                "minutos_antes": minutos_antes,
                "minutos_despues": minutos_despues
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            periodo_anomalo = data.get("periodo_anomalo", {})
            periodo_consulta = data.get("periodo_consulta", {})
            stats = data.get("estadisticas", {})
            datos = data.get("datos", [])

            print(f"    [OK] Respuesta exitosa")
            print(f"    Periodo anomalo: {periodo_anomalo.get('duracion_minutos')} min")
            print(f"    Rango consulta: {periodo_consulta.get('timestamp_inicio_contexto')}")
            print(f"                 -> {periodo_consulta.get('timestamp_fin_contexto')}")
            print(f"    Total registros: {stats.get('total_registros')}")

            # Contar registros dentro y fuera del periodo anomalo
            en_periodo = sum(1 for d in datos if d.get("en_periodo_anomalo"))
            fuera_periodo = len(datos) - en_periodo
            print(f"    En periodo anomalo: {en_periodo}")
            print(f"    Contexto (antes/despues): {fuera_periodo}")

            return True
        elif response.status_code == 400:
            print(f"    [!] Sin datos de anomalia para esta alerta")
            return False
        else:
            print(f"    [!] Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"    [!] Error: {e}")
        return False


def mostrar_ejemplo_respuesta(alerta_id):
    """Muestra un ejemplo de la respuesta JSON completa"""
    print(f"\n{'='*60}")
    print(f"EJEMPLO DE RESPUESTA - Alerta {alerta_id}")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/alertas_umbral/{alerta_id}/datos_anomalia_contexto",
            params={"minutos_antes": 15, "minutos_despues": 15},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            # Limitar datos para no mostrar demasiado
            if "datos" in data and len(data["datos"]) > 5:
                data["datos"] = data["datos"][:3] + ["..."] + data["datos"][-2:]

            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    print("\n" + "=" * 60)
    print("VERIFICACION DE ENDPOINTS DE ANOMALIAS")
    print("=" * 60)
    print(f"URL Backend: {BASE_URL}")

    # Verificar conexion
    print("\n[*] Verificando conexion al backend...")
    try:
        requests.get(f"{BASE_URL}/docs", timeout=5)
        print("[OK] Backend disponible")
    except Exception as e:
        print(f"[!] Error: No se puede conectar al backend")
        print(f"    Ejecuta: uvicorn main:app --reload")
        return

    # Consultar alertas
    alertas, con_timestamps = consultar_todas_alertas()

    if not alertas:
        print("\n[!] No hay alertas en el sistema")
        print("    Ejecuta primero: python utils/simular_envio_sensores.py")
        return

    # Probar endpoints con alertas que tienen timestamps
    if con_timestamps:
        print("\n" + "=" * 60)
        print("PROBANDO ENDPOINTS CON ALERTAS QUE TIENEN TIMESTAMPS")
        print("=" * 60)

        # Probar con la primera alerta que tiene timestamps
        alerta = con_timestamps[0]
        alerta_id = alerta["id"]

        print(f"\nAlerta seleccionada:")
        print(f"  ID: {alerta_id}")
        print(f"  Sensor: {alerta['tipo_sensor']}")
        print(f"  Origen: {alerta['origen']}")
        print(f"  Timestamp: {alerta['timestamp']}")

        # Probar endpoint basico
        probar_endpoint_datos_anomalia(alerta_id)

        # Probar endpoint con contexto
        probar_endpoint_contexto(alerta_id, 30, 30)

        # Mostrar ejemplo de respuesta
        mostrar_ejemplo_respuesta(alerta_id)

    else:
        print("\n[!] No hay alertas con timestamps de anomalia")
        print("    Las alertas existentes son anteriores a la implementacion")
        print("    Ejecuta: python utils/simular_envio_sensores.py")
        print("    para generar nuevas alertas con timestamps")

        # Intentar probar con cualquier alerta (deberia dar error 400)
        if alertas:
            print("\n[*] Probando con alerta sin timestamps (deberia dar error 400)...")
            probar_endpoint_datos_anomalia(alertas[0]["id"])

    print("\n" + "=" * 60)
    print("[OK] Verificacion completada")
    print("=" * 60)


if __name__ == "__main__":
    main()

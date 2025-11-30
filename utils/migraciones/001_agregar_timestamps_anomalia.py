"""
Migracion 001: Agregar campos de timestamps de anomalia a tablas de alertas
Relacionado con: COTIZACION_FEATURE_DATOS_ANOMALOS.md

Cambios:
- Agrega timestamp_inicio_anomalia a alertas y alertas_b
- Agrega timestamp_fin_anomalia a alertas y alertas_b
- Crea indices para optimizar consultas de rango temporal
"""

import sqlite3
import os

# Ruta de la base de datos SQLite local
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db_local.sqlite")


def verificar_columna_existe(cursor, tabla, columna):
    """Verifica si una columna existe en una tabla"""
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [info[1] for info in cursor.fetchall()]
    return columna in columnas


def verificar_indice_existe(cursor, nombre_indice):
    """Verifica si un indice existe"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (nombre_indice,))
    return cursor.fetchone() is not None


def migrar_alertas(cursor):
    """Agrega las nuevas columnas a las tablas de alertas"""

    tablas_alertas = ["alertas", "alertas_b"]
    nuevas_columnas = [
        ("timestamp_inicio_anomalia", "DATETIME"),
        ("timestamp_fin_anomalia", "DATETIME")
    ]

    for tabla in tablas_alertas:
        print(f"\n  Procesando tabla: {tabla}")

        for columna, tipo in nuevas_columnas:
            if verificar_columna_existe(cursor, tabla, columna):
                print(f"    [=] Columna '{columna}' ya existe")
            else:
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
                print(f"    [+] Columna '{columna}' agregada")


def crear_indices(cursor):
    """Crea indices para optimizar consultas de rango temporal"""

    # Indices para tablas de alertas
    indices_alertas = [
        ("idx_alertas_timestamp", "alertas", "timestamp"),
        ("idx_alertas_tipo_sensor", "alertas", "tipo_sensor"),
        ("idx_alertas_b_timestamp", "alertas_b", "timestamp"),
        ("idx_alertas_b_tipo_sensor", "alertas_b", "tipo_sensor"),
    ]

    # Indices para tablas de sensores (Bomba A)
    tablas_sensores_a = [
        "sensores_corriente",
        "sensores_salida_agua",
        "sensores_presion_agua",
        "mw_brutos_generacion_gas",
        "temperatura_ambiental",
        "temperatura_descanso_interna_empuje_bomba_1a",
        "temperatura_descanso_interna_motor_bomba_1a",
        "temperatura_descanso_interno_bomba_1a",
        "vibracion_axial_descanso",
        "voltaje_barra",
        "excentricidad_bomba",
        "flujo_agua_domo_ap",
        "flujo_agua_domo_mp",
        "flujo_agua_recalentador",
        "flujo_agua_vapor_alta",
        "posicion_valvula_recirc",
        "presion_agua_mp",
        "presion_succion_baa",
        "temperatura_estator",
        "flujo_salida_12fpmfc",
    ]

    # Indices para tablas de sensores (Bomba B)
    tablas_sensores_b = [
        "sensores_corriente_b",
        "excentricidad_bomba_b",
        "flujo_descarga_b",
        "flujo_agua_domo_ap_b",
        "flujo_agua_domo_mp_b",
        "flujo_agua_recalentador_b",
        "flujo_agua_vapor_alta_b",
        "presion_agua_b",
        "temperatura_ambiental_b",
        "temperatura_agua_alim_b",
        "temperatura_estator_b",
        "vibracion_axial_empuje_b",
        "vibracion_x_descanso_b",
        "vibracion_y_descanso_b",
        "voltaje_barra_b",
    ]

    # Generar indices para tiempo_ejecucion de sensores
    indices_sensores = []
    for tabla in tablas_sensores_a + tablas_sensores_b:
        indices_sensores.append((f"idx_{tabla}_tiempo", tabla, "tiempo_ejecucion"))

    todos_indices = indices_alertas + indices_sensores

    print("\n  Creando indices...")

    creados = 0
    existentes = 0

    for nombre_indice, tabla, columna in todos_indices:
        if verificar_indice_existe(cursor, nombre_indice):
            existentes += 1
        else:
            try:
                cursor.execute(f"CREATE INDEX {nombre_indice} ON {tabla}({columna})")
                creados += 1
            except Exception as e:
                print(f"    [!] Error creando indice {nombre_indice}: {e}")

    print(f"    [+] Indices creados: {creados}")
    print(f"    [=] Indices ya existentes: {existentes}")


def main():
    print("=" * 60)
    print("MIGRACION 001: Timestamps de Anomalia")
    print("=" * 60)

    # Verificar que existe la base de datos
    if not os.path.exists(DB_PATH):
        print(f"\n[!] Error: No se encontro la base de datos en:")
        print(f"    {DB_PATH}")
        print("\n    Ejecuta primero: python utils/crear_db_local.py")
        return False

    print(f"\n[+] Base de datos: {DB_PATH}")

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Agregar columnas a tablas de alertas
        print("\n" + "-" * 40)
        print("PASO 1: Agregando columnas a alertas")
        print("-" * 40)
        migrar_alertas(cursor)

        # 2. Crear indices
        print("\n" + "-" * 40)
        print("PASO 2: Creando indices de optimizacion")
        print("-" * 40)
        crear_indices(cursor)

        # Confirmar cambios
        conn.commit()

        # Mostrar estructura final
        print("\n" + "-" * 40)
        print("ESTRUCTURA FINAL DE ALERTAS")
        print("-" * 40)

        for tabla in ["alertas", "alertas_b"]:
            print(f"\n  {tabla}:")
            cursor.execute(f"PRAGMA table_info({tabla})")
            for info in cursor.fetchall():
                print(f"    - {info[1]}: {info[2]}")

        print("\n" + "=" * 60)
        print("[OK] Migracion completada exitosamente!")
        print("=" * 60)

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[!] Error durante la migracion: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    main()

-- ============================================================
-- MIGRACION 001: Agregar campos de timestamps de anomalia
-- Base de datos: PostgreSQL (Produccion)
-- Relacionado con: COTIZACION_FEATURE_DATOS_ANOMALOS.md
-- ============================================================

-- Agregar columnas a tabla alertas (Bomba A)
ALTER TABLE alertas
ADD COLUMN IF NOT EXISTS timestamp_inicio_anomalia TIMESTAMP;

ALTER TABLE alertas
ADD COLUMN IF NOT EXISTS timestamp_fin_anomalia TIMESTAMP;

-- Agregar columnas a tabla alertas_b (Bomba B)
ALTER TABLE alertas_b
ADD COLUMN IF NOT EXISTS timestamp_inicio_anomalia TIMESTAMP;

ALTER TABLE alertas_b
ADD COLUMN IF NOT EXISTS timestamp_fin_anomalia TIMESTAMP;

-- Crear indices para optimizar consultas de alertas
CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo_sensor ON alertas(tipo_sensor);
CREATE INDEX IF NOT EXISTS idx_alertas_b_timestamp ON alertas_b(timestamp);
CREATE INDEX IF NOT EXISTS idx_alertas_b_tipo_sensor ON alertas_b(tipo_sensor);

-- Crear indices para optimizar consultas de rango temporal en sensores (Bomba A)
CREATE INDEX IF NOT EXISTS idx_sensores_corriente_tiempo ON sensores_corriente(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_sensores_salida_agua_tiempo ON sensores_salida_agua(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_sensores_presion_agua_tiempo ON sensores_presion_agua(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_mw_brutos_generacion_gas_tiempo ON mw_brutos_generacion_gas(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temperatura_ambiental_tiempo ON temperatura_ambiental(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temp_descanso_empuje_1a_tiempo ON temperatura_descanso_interna_empuje_bomba_1a(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temp_descanso_motor_1a_tiempo ON temperatura_descanso_interna_motor_bomba_1a(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temp_descanso_interno_1a_tiempo ON temperatura_descanso_interno_bomba_1a(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_vibracion_axial_descanso_tiempo ON vibracion_axial_descanso(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_voltaje_barra_tiempo ON voltaje_barra(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_excentricidad_bomba_tiempo ON excentricidad_bomba(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_domo_ap_tiempo ON flujo_agua_domo_ap(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_domo_mp_tiempo ON flujo_agua_domo_mp(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_recalentador_tiempo ON flujo_agua_recalentador(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_vapor_alta_tiempo ON flujo_agua_vapor_alta(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_posicion_valvula_recirc_tiempo ON posicion_valvula_recirc(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_presion_agua_mp_tiempo ON presion_agua_mp(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_presion_succion_baa_tiempo ON presion_succion_baa(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temperatura_estator_tiempo ON temperatura_estator(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_salida_12fpmfc_tiempo ON flujo_salida_12fpmfc(tiempo_ejecucion);

-- Crear indices para optimizar consultas de rango temporal en sensores (Bomba B)
CREATE INDEX IF NOT EXISTS idx_sensores_corriente_b_tiempo ON sensores_corriente_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_excentricidad_bomba_b_tiempo ON excentricidad_bomba_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_descarga_b_tiempo ON flujo_descarga_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_domo_ap_b_tiempo ON flujo_agua_domo_ap_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_domo_mp_b_tiempo ON flujo_agua_domo_mp_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_recalentador_b_tiempo ON flujo_agua_recalentador_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_flujo_agua_vapor_alta_b_tiempo ON flujo_agua_vapor_alta_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_presion_agua_b_tiempo ON presion_agua_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temperatura_ambiental_b_tiempo ON temperatura_ambiental_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temperatura_agua_alim_b_tiempo ON temperatura_agua_alim_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_temperatura_estator_b_tiempo ON temperatura_estator_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_vibracion_axial_empuje_b_tiempo ON vibracion_axial_empuje_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_vibracion_x_descanso_b_tiempo ON vibracion_x_descanso_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_vibracion_y_descanso_b_tiempo ON vibracion_y_descanso_b(tiempo_ejecucion);
CREATE INDEX IF NOT EXISTS idx_voltaje_barra_b_tiempo ON voltaje_barra_b(tiempo_ejecucion);

-- ============================================================
-- VERIFICACION
-- ============================================================
-- Ejecutar despues de la migracion para verificar:
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'alertas' AND column_name LIKE 'timestamp%';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'alertas_b' AND column_name LIKE 'timestamp%';

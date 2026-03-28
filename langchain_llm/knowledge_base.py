"""
Base de conocimiento para el chatbot del Dashboard GM.
Cada chunk incluye sinonimos y variaciones para mejorar la busqueda TF-IDF.
"""

CHUNKS = [
    # ─── SENSORES BOMBA A - Principales (19) ───
    "Sensor Corriente del motor Bomba A: mide la corriente electrica del motor en Amperios. Umbrales de alerta: 101 anomalias para AVISO, 162 para ALERTA, 202 para CRITICA en ventana de 8 horas. Es uno de los sensores mas criticos. Tambien conocido como corriente motor, amperaje, consumo electrico.",
    "Sensor Presion de agua AP Bomba A: mide la presion del agua de alimentacion de alta presion en bar. Umbrales: 118 AVISO, 188 ALERTA, 235 CRITICA. Tambien llamado presion agua alta presion, presion AP.",
    "Sensor MW brutos generacion gas Bomba A: mide la potencia de generacion en megavatios (MW). Umbrales: 56/86/116. Sensor compartido con Bomba B. Tambien conocido como megavatios, potencia, generacion.",
    "Sensor Temperatura ambiental Bomba A: mide la temperatura del ambiente en grados Celsius. Umbrales: 56/86/116. Sensor compartido con Bomba B, ambas bombas usan la misma fuente de datos. Tambien llamado temp ambiente, temperatura exterior.",
    "Sensor Temperatura descanso bomba 1A: mide la temperatura del descanso interno de la bomba en Celsius. Umbrales: 86/137/171. Tiene umbrales altos por ser sensor critico. Tambien conocido como temp descanso, temperatura rodamiento.",
    "Sensor Temperatura empuje bomba 1A: mide la temperatura del empuje de la bomba en Celsius. Umbrales: 56/86/116. Tambien llamado temp empuje, temperatura thrust.",
    "Sensor Temperatura motor bomba 1A: mide la temperatura del motor de la bomba en Celsius. Umbrales: 56/86/116. Tambien conocido como temp motor, calentamiento motor.",
    "Sensor Vibracion axial descanso Bomba A: mide la vibracion axial en mm/s. Umbrales: 56/86/116. Vibraciones altas pueden indicar desalineacion o desgaste de rodamientos. Tambien llamado vibracion axial, vibraciones.",
    "Sensor Voltaje barra 6.6KV Bomba A: mide el voltaje de la barra en kilovoltios (kV). Umbrales: 56/86/116. Sensor compartido con Bomba B. Tambien conocido como tension, voltaje electrico.",
    "Sensor Excentricidad bomba Bomba A: mide la excentricidad del rotor en milimetros (mm). Umbrales: 56/86/116. Valores altos indican desalineacion del eje. Tambien llamado desalineacion, runout.",
    "Sensor Flujo agua domo AP Bomba A: mide el flujo de agua alimentacion al domo de alta presion en m3/h. Umbrales: 56/86/116. Tambien conocido como caudal domo AP, flujo alta presion.",
    "Sensor Flujo domo AP compensado Bomba A: flujo de agua al domo AP con compensacion en m3/h. Umbrales: 56/86/116. Tambien llamado flujo compensado, caudal compensado.",
    "Sensor Flujo agua domo MP Bomba A: mide el flujo de agua al domo de media presion en m3/h. Umbrales: 56/86/116. Tambien conocido como caudal domo MP, flujo media presion.",
    "Sensor Flujo agua recalentador Bomba A: mide el flujo de agua al recalentador en m3/h. Umbrales: 56/86/116. Tambien llamado caudal recalentador, flujo reheat.",
    "Sensor Flujo agua vapor alta Bomba A: mide el flujo de agua/atemperacion de vapor de alta presion en m3/h. Umbrales: 56/86/116. Tambien conocido como flujo vapor, caudal vapor alta.",
    "Sensor Posicion valvula recirculacion Bomba A: mide la posicion de la valvula de recirculacion en porcentaje (%). Umbrales: 56/86/116. Tambien llamado apertura valvula, posicion valvula.",
    "Sensor Presion agua MP Bomba A: mide la presion del agua de media presion en bar. Umbrales: 56/86/116. Tambien conocido como presion media presion.",
    "Sensor Presion succion BAA Bomba A: mide la presion de succion de la bomba de agua de alimentacion en bar. Umbrales: 56/86/116. Tambien llamado presion succion, presion entrada bomba.",
    "Sensor Temperatura estator Bomba A: mide la temperatura del estator del motor en Celsius. Umbrales: 56/86/116. Tambien conocido como temp estator, temperatura bobinado.",

    # ─── SENSORES BOMBA A - Extra (6) ───
    "Sensor Flujo salida 12FPMFC Bomba A: sensor extra que mide flujo de salida en m3/h. Umbrales: 56/86/116. No se usa en la prediccion global, solo monitoreo individual.",
    "Sensor Vibracion X descanso interno Bomba A: mide vibracion en eje X del descanso interno en micrometros (um). Umbrales: 67/106/133. Sensor extra, no usado en prediccion global.",
    "Sensor Vibracion Y descanso interno Bomba A: mide vibracion en eje Y del descanso interno en micrometros (um). Sensor extra.",
    "Sensor Vibracion X descanso externo Bomba A: mide vibracion en eje X del descanso externo en um. Umbrales: 60/96/120. Sensor extra.",
    "Sensor Vibracion Y descanso externo Bomba A: mide vibracion en eje Y del descanso externo en um. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Temperatura agua alimentacion domo MP Bomba A: mide temperatura del agua de alimentacion al domo MP en Celsius. Umbrales: 56/86/116. Sensor extra.",

    # ─── SENSORES BOMBA B - Principales (15) ───
    "Sensor Corriente motor 1B Bomba B: mide la corriente del motor de la bomba B en Amperios. Umbrales: 56/86/116. Tambien conocido como amperaje bomba B, consumo electrico 1B.",
    "Sensor Presion agua econ AP Bomba B: mide presion de agua alimentacion economizador alta presion en bar. Umbrales: 56/86/116.",
    "Sensor Temperatura ambiental Bomba B: sensor compartido con Bomba A, misma fuente de datos. Celsius. Umbrales: 56/86/116.",
    "Sensor Excentricidad bomba 1B Bomba B: mide excentricidad del rotor en mm. Umbrales: 56/86/116. Tambien llamado desalineacion bomba B.",
    "Sensor Flujo descarga AP Bomba B: mide flujo de descarga alta presion en m3/h. Umbrales: 66/106/132. Tambien conocido como caudal descarga.",
    "Sensor Flujo agua domo AP Bomba B: flujo agua al domo alta presion en m3/h. Umbrales: 56/86/116.",
    "Sensor Flujo agua domo MP Bomba B: flujo agua al domo media presion en m3/h. Umbrales: 56/86/116.",
    "Sensor Flujo agua recalentador Bomba B: flujo al recalentador en m3/h. Umbrales: 56/86/116.",
    "Sensor Flujo agua vapor alta AP Bomba B: flujo agua/atemp vapor alta presion en m3/h. Umbrales: 56/86/116.",
    "Sensor Temperatura agua alimentacion AP Bomba B: temperatura del agua de alimentacion alta presion en Celsius. Umbrales: 56/86/116.",
    "Sensor Temperatura estator motor 1B Bomba B: temperatura del estator del motor en Celsius. Umbrales: 56/86/116.",
    "Sensor Vibracion axial empuje 1B Bomba B: vibracion axial del descanso empuje en mm/s. Umbrales: 56/86/116.",
    "Sensor Vibracion X descanso interno 1B Bomba B: vibracion eje X descanso interno en um. Umbrales: 67/106/133.",
    "Sensor Vibracion Y descanso interno 1B Bomba B: vibracion eje Y descanso interno en um. Umbrales: 56/86/116.",
    "Sensor Voltaje barra 6.6KV Bomba B: sensor compartido con Bomba A. kV. Umbrales: 56/86/116.",

    # ─── SENSORES BOMBA B - Extra (11) ───
    "Sensor Temperatura descanso bomba 1B Bomba B: temperatura descanso interno bomba en Celsius. Umbrales: 86/137/171. Sensor extra.",
    "Sensor Temperatura descanso empuje 1B Bomba B: temperatura descanso empuje en Celsius. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Temperatura descanso motor 1B Bomba B: temperatura descanso motor en Celsius. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Vibracion X descanso externo 1B Bomba B: vibracion eje X externo en um. Umbrales: 60/96/120. Sensor extra.",
    "Sensor Vibracion Y descanso externo 1B Bomba B: vibracion eje Y externo en um. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Presion succion BAA 1B Bomba B: presion succion bomba en bar. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Posicion valvula recirculacion 1B Bomba B: posicion valvula en %. Umbrales: 56/86/116. Sensor extra.",
    "Sensor MW brutos generacion gas Bomba B: sensor compartido con Bomba A. MW. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Presion agua econ AP Bomba B extra: presion en bar. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Flujo domo AP compensado Bomba B: flujo compensado m3/h. Umbrales: 56/86/116. Sensor extra.",
    "Sensor Flujo atemp vapor alta AP Bomba B: flujo atemperacion vapor alta presion en m3/h. Umbrales: 56/86/116. Sensor extra.",

    # ─── INFORMACION GENERAL DEL SISTEMA ───
    "El Dashboard GM es una aplicacion web de monitoreo predictivo de bombas de agua en la planta termoelectrica de ciclo combinado Nueva Renca. Monitorea las bombas del HRSG (Heat Recovery Steam Generator). Tambien conocido como sistema de monitoreo, plataforma, app, aplicacion, dashboard, panel de control.",
    "La planta tiene 2 bombas de agua de alimentacion: Bomba A y Bomba B. Solo una bomba esta activa a la vez, se puede alternar entre ellas. La bomba activa se puede consultar en el sistema. Cuando ninguna esta activa el valor es O.",
    "La Bomba A tiene 25 sensores en total: 19 principales usados en la prediccion global y 6 extras monitoreados individualmente. La bomba A tambien se conoce como equipo A, equipos A.",
    "La Bomba B tiene 26 sensores en total: 15 principales usados en la prediccion global y 11 extras monitoreados individualmente. La bomba B tambien se conoce como equipo B, equipos B.",
    "Los sensores compartidos entre ambas bombas son: Temperatura ambiental, MW brutos generacion gas, y Voltaje barra 6.6KV. Son sensores generales que usan la misma fuente de datos para ambas bombas.",
    "Los datos de sensores llegan cada minuto en tiempo real desde el sistema SCADA de la planta a traves de PostgreSQL. Cada dato incluye valor del sensor, tiempo del sensor y se clasifica automaticamente con IA.",

    # ─── SISTEMA DE ALERTAS ───
    "El sistema de alertas cuenta anomalias (clasificacion -1) en una ventana deslizante de 8 horas. Hay 3 niveles de alerta: AVISO (amarillo, nivel bajo), ALERTA (naranja, nivel medio), CRITICA (rojo, nivel alto). Tambien llamado sistema de notificaciones, avisos, alarmas.",
    "Los umbrales base son 56 anomalias para AVISO, 86 para ALERTA, y 116 para CRITICA. Algunos sensores criticos como corriente y presion de Bomba A tienen umbrales mas altos. Los umbrales tambien se conocen como limites, valores de corte, thresholds.",
    "Despues de una alerta CRITICA, el contador se reinicia automaticamente. Se cuenta desde el timestamp de la ultima CRITICA, no se modifican los datos originales. El ciclo de alertas empieza de nuevo: AVISO, ALERTA, CRITICA.",
    "Las alertas se generan automaticamente y aparecen en la pagina de Vision General del dashboard. Cada alerta incluye el sensor afectado, nivel de severidad, intervalo de tiempo y accion recomendada. Se puede ver el grafico de la anomalia.",
    "Los umbrales representan la cantidad de anomalias necesarias en 8 horas para generar cada nivel. Ejemplo: si un sensor tiene umbral 56/86/116, necesita 56 anomalias en 8h para AVISO, 86 para ALERTA, 116 para CRITICA. Cuanto mayor el umbral, menos sensible es el sensor.",
    "Los colores de las alertas son: amarillo para AVISO (alerta leve, revisar), naranja para ALERTA (atencion, actuar pronto), rojo para CRITICA (urgente, accion inmediata). Los colores ayudan a priorizar la atencion.",

    # ─── MODELOS DE MACHINE LEARNING ───
    "El modelo que se usa para cada sensor individual es Isolation Forest. Cada sensor tiene su propio modelo de Isolation Forest que clasifica valores: 1 = Normal, -1 = Anomalia. Es un modelo no supervisado de deteccion de outliers. Se usa para la clasificacion individual de cada sensor. Tambien llamado modelo de anomalias, detector de anomalias, modelo predictivo.",
    "El modelo que se usa para la prediccion global de falla es Random Forest (Arbol Aleatorio). Toma TODOS los sensores principales de una bomba y predice si hay una falla general: 0 = Normal, 1 = Falla. Es diferente al Isolation Forest que se usa por sensor individual. Tambien conocido como prediccion general, modelo global.",
    "La prediccion global de Bomba A usa 19 sensores (features). La de Bomba B usa 15 sensores (features). Se ejecuta cuando llegan todos los valores de un mismo timestamp. Usa el modelo Random Forest.",
    "Los modelos de machine learning estan pre-entrenados y guardados como archivos .pkl. Se cargan en memoria la primera vez que se usan (lazy loading) y permanecen en cache. Hay dos tipos: Isolation Forest (por sensor) y Random Forest (prediccion global).",
    "La clasificacion -1 significa anomalia: el valor del sensor esta fuera del rango normal aprendido por el modelo Isolation Forest. Clasificacion 1 significa normal. Tambien se dice que -1 es outlier, valor atipico, fuera de rango. 1 es valor esperado, dentro del rango.",
    "Hay dos tipos de modelos en el sistema: 1) Isolation Forest para cada sensor individual (clasifica -1 anomalia o 1 normal), 2) Random Forest para prediccion global por bomba (clasifica 0 normal o 1 falla). Son modelos diferentes con propositos diferentes.",

    # ─── PAGINAS DE LA APLICACION ───
    "La pagina Vision General es la pantalla principal, muestra un resumen de todas las alertas recientes de sensores de ambas bombas (AVISO, ALERTA, CRITICA) y las bitacoras con alertas y avisos. Tambien conocida como inicio, home, resumen, vista principal, pantalla de inicio.",
    "La pagina Analisis de Anomalias A muestra graficos de cada sensor de la Bomba A con valores clasificados como normales (verde, clasificacion 1) y anomalias (rojo, clasificacion -1) a lo largo del tiempo. Puedes hacer clic en una alerta para ver el grafico detallado. Tambien llamada anomalias, graficos, monitoreo anomalias.",
    "La pagina Analisis de Anomalias B muestra los mismos graficos de anomalias pero para los sensores de la Bomba B. Mismo formato que Anomalias A.",
    "La pagina Analisis de Sensores A muestra datos en tiempo real de todos los sensores de la Bomba A: valores actuales, tendencias, historico y estado. Se actualiza con cada nuevo dato. Tambien llamada datos de sensores, monitoreo sensores, valores en vivo, datos en tiempo real.",
    "La pagina Analisis de Sensores B muestra datos en tiempo real de los sensores de la Bomba B. Misma funcionalidad que Sensores A.",
    "La pagina Analisis de Bitacoras A muestra los registros operativos de la Bomba A escritos por los operadores, clasificados automaticamente por IA en categorias y niveles de alerta. Tambien llamada registros, logs, historial operativo, notas de operadores.",
    "La pagina Analisis de Bitacoras B muestra las bitacoras de la Bomba B. Misma funcionalidad que Bitacoras A.",
    "La pagina de Feedback permite enviar opiniones, comentarios, sugerencias, quejas, reclamos, reportes de problemas o felicidades sobre la aplicacion. Se pueden adjuntar imagenes como capturas de pantalla. Tambien conocida como comentarios, opiniones, sugerencias, reportar problema, enviar queja, dejar mensaje.",

    # ─── NAVEGACION Y USO DE LA APP ───
    "Para navegar entre paginas usa el menu lateral izquierdo (sidebar). Las secciones estan organizadas en: General (Vision General, Feedback), Bomba A (Anomalias, Sensores, Bitacoras), Bomba B (Anomalias, Sensores, Bitacoras). Tambien conocido como menu, barra lateral, navegacion.",
    "Para ver el detalle de una alerta, haz clic en el boton 'Ver grafico de anomalia' dentro de cada alerta en Vision General. Esto muestra el grafico del sensor durante el periodo de la anomalia.",
    "Para filtrar alertas puedes usar el selector de tiempo (ultimos 2 dias, 7 dias, 30 dias, 3 meses). Tambien puedes filtrar por nivel: Criticas, Alertas, Avisos.",
    "Para cambiar entre Bomba A y Bomba B, selecciona la seccion correspondiente en el menu lateral. Cada bomba tiene sus propias paginas de Anomalias, Sensores y Bitacoras.",

    # ─── BITACORAS ───
    "Las bitacoras son registros de texto libre escritos por los operadores de la planta describiendo eventos operativos, incidentes, observaciones o novedades del turno. Tambien llamadas registros operativos, logs de operacion, notas de turno, reportes de turno.",
    "Las categorias de las bitacoras son 7: 1) Fallas de bombas HRSG, 2) Fugas y filtraciones, 3) Eventos de frecuencia y carga, 4) Mediciones operativas, 5) Cambio de combustible, 6) Otras fallas de bombas, 7) Otros eventos operativos. Un modelo de IA (Llama 3.3 70B de IBM WatsonX) clasifica automaticamente cada bitacora en una de estas categorias. Tambien conocido como tipos de bitacora, clasificacion de bitacoras, en que se clasifican las bitacoras.",
    "Las bitacoras se clasifican en ALERTA (falla que ya ocurrio en la planta, requiere accion) o AVISO (posible falla o situacion que debe ser revisada por el operador). Esto lo hace automaticamente la IA.",
    "Las subcategorias de fallas HRSG incluyen: sobrecalentamiento de componentes, fugas de agua en HRSG, problemas de bajo flujo, variaciones anormales de presion, eventos en sistemas relacionados (turbina de vapor, caldera), y vibraciones en bombas.",

    # ─── FEEDBACK ───
    "Para enviar feedback, comentarios, opiniones, sugerencias, quejas o reportar un problema, ve a la seccion Feedback en el menu lateral y haz clic en 'Enviar Feedback'. Puedes escribir un mensaje y adjuntar una imagen. Tambien conocido como donde dejar comentario, como reportar, como enviar queja, donde opinar, como enviar sugerencia, donde poner reclamo.",
    "El sistema de feedback tiene 3 tipos: Funcionamiento (reportar problemas con la app, errores, cosas que no funcionan), Datos (reportar problemas con los datos mostrados, valores incorrectos), Felicidades (reconocer el buen trabajo del equipo). Tambien conocidos como categorias de comentarios.",
    "Al enviar feedback se puede adjuntar una imagen como captura de pantalla para mostrar el problema. Las imagenes se almacenan de forma segura. Tambien conocido como subir foto, adjuntar captura, enviar screenshot.",
    "Solo el administrador (sd_fallabombas@generadora.cl) puede ver todos los feedback recibidos, actualizar su estado y eliminarlos. Los usuarios normales solo pueden enviar. Tambien conocido como quien ve los comentarios, quien gestiona el feedback, quien administra.",
    "Los estados de un feedback son: Pendiente (recien enviado, aun no revisado), Revisado (alguien lo leyo y esta en revision), Resuelto (el problema fue atendido o la sugerencia implementada). Tambien conocido como seguimiento, estado del comentario, que paso con mi feedback.",

    # ─── DATOS TECNICOS ───
    "Las unidades de medida de los sensores son: Amperios (corriente), bar (presion), Celsius (temperatura), mm/s (vibracion axial), kV (voltaje), mm (excentricidad), m3/h (flujo), um o micrometros (vibraciones X/Y), MW (potencia), porcentaje (valvulas).",
    "Los datos se actualizan cada minuto en tiempo real. Si ves que los datos no se actualizan, puede ser un problema de conexion con el sistema SCADA o con los listeners que procesan los datos.",
    "El sistema usa PostgreSQL como base de datos, alojada en IBM Cloud. Los datos de sensores se reciben via triggers y LISTEN/NOTIFY de PostgreSQL.",
]

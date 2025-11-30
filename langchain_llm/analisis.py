from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Verificar si estamos en modo local (sin WatsonX)
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

# Configurar los parámetros del modelo
parameters = {
    "decoding_method": "greedy",
  "max_new_tokens": 4096,
  "min_new_tokens": 0,
  "repetition_penalty": 1
}
proyecto_id=os.getenv("project_id")
api_key=os.getenv("apikey")
#print(proyecto_id)
#print(api_key)
#meta-llama/llama-3-3-70b-instruct

# Inicializar el modelo WatsonxLLM solo si no estamos en modo local
watsonx_llm = None
if not USE_LOCAL_DB:
    try:
        from langchain_ibm import WatsonxLLM
        watsonx_llm = WatsonxLLM(
            model_id="meta-llama/llama-3-3-70b-instruct",
            url="https://us-south.ml.cloud.ibm.com",
            project_id=proyecto_id,
            apikey=api_key,
            params=parameters
        )
    except Exception as e:
        print(f"[WARN] No se pudo inicializar WatsonX: {e}")
        watsonx_llm = None
else:
    print("[INFO] Modo local activo - WatsonX deshabilitado")

# Crear un PromptTemplate
template = """<|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are an IA assistant in charge of a combined cycle thermoelectric power generating plant , your task is to detect faults related to the water pump of the steam generator heat recovery system (HRSG) in the Renca Power Plant. Analyze the following operating record and classify it in one of the following categories HRSG Pump Failures , Leaks and Leakages , Frequency and Load Events , Operational Measurements , Fuel Changeover , Other Operational Events and remember that the category HRSG Pump Failures is divided into subcategories so if the record is within the category HRSG Pump Failures then you must indicate which subcategory corresponds , in your answer you must only return the corresponding classification and nothing else:
        glossary :
            HRSG:heat recovery steam generator.
            Sump pumps, diesel pumps, well pumps and transfer pumps are related to other types of failures that do not fall under the HRSG pump failure detection target.
        Categories:
            
            1-HRSG Pump Failures: Anomalies or failures in pumps, with special focus on the HRSG system.HRSG pump failures are subdivided into different subcategories where you will only have to return one if it corresponds to one of the following.
                1.1-Overheating events in components associated with water pumps: Unexpected temperature increase in the boiler feed pump.
                1.2-Leakage in the HRSG (Water Leaks): Leakage of water could influence the thermal efficiency of the system and water consumption.
                1.3-Low flow problems in feed pumps: Significant flow reduction in the feed water system, flow lower than the minimum threshold, affecting the stability of the system.
                1.4-Abnormal pressure variations in the HRSG system: Fluctuating pressure in the feed circuit, Pressure oscillations in the HRSG.
                1.5-Events to Related HRSG Systems (e.g., Steam Turbine , boiler,evaporator, condenser): Failures in other HRSG-related systems like the steam turbine or boiler that indirectly impact pump operation or sensors.
                1.6-Vibrations associated with water pumps.
            2-Other Pump Failures: Failures in pumps not directly tied to the HRSG system, such as diesel transfer pumps, well pumps, or other auxiliary pumps.
            3-Leaks and Leakages: Reports of water, gas, oil or other fluids leaks.
            4-Frequency and Load Events: Load and frequency settings, including primary frequency control (CPF) and automatic generation control (AGC).
            5-Operational Measurements: Parameters such as chlorides, temperature, pressure, or other physicochemical variables monitored.
            6-Fuel Changeover: Transitions between different types of fuels used in the plant.
            7-Other operational events: Activities such as maintenance, testing, noise measurements or events not classified in the other categories.
            


        these examples should only be used as a guide to give your answer and never return information within the examples :
            Examples  HRSG Pump Failures:
                +log to be analyzed:Steam Turbine lubrication pond mist extractor forced shutdown due to failure, (it is serious) and oil leakage from shaft detected
                +answer:HRSG Pump Failures -  Failures in HRSG-related systems

                +log to be analyzed:NÂ°15052 por fuga de gases en parte superior Caldera: HEAT RECOVERY STEAM GENERATOR. 
                +answer:HRSG Pump Failures -  Events to Related HRSG Systems 

                +log to be analyzed:Opera detector de liquido generador Turbina a Vapor, retira 500[cc] de agua. 
                +answer:HRSG Pump Failures - Events to Related HRSG Systems 

                +log to be analyzed: AVISOS: NÂ° 3846 por ADFT033,por oscilaciones en FT de agua de atemperaciÃ³n del By Pass de Alta presiÃ³n
                +answer:HRSG Pump Failures - Events to Related HRSG Systems 

                +log to be analyzed:Nota: 88QV-2 no realiza rotación por alta vibración, crea aviso N°18390
                +answer:HRSG Pump Failures - Vibrations associated with water pumps

                +log to be analyzed:Sincroniza Turbina a Vapor. desconexiÃ³n forzada por falla (es grave) Turbina a Vapor opera maestro generador Turbina a Vapor por falla aparente de barra generador Turbina a Vapor sobre G60. Empuja Turbina a Vapor a 3000 rpm. Sincroniza Turbina a Vapor
                +answer: HRSG Pump Failures - Failures in Related HRSG

                +log to be analyzed:Aviso N°12538 Filtración en línea de descarga en bba circulación equipos B
                +answer:HRSG Pump Failures – Leakage in the HRSG (Water Leaks)
                
                +log to be analyzed:Rotación de bba de alimentación por alta T° estator bba equipos A, en inspección en terreno se observan filtros motor sucios
                +answer:HRSG Pump Failures -Overheating events in components associated with water pumps

                +log to be analyzed:Llamadas de servicio - #10526, filtración agua desmineraliza por sello de bomba transferencia 1A
                +answer:HRSG Pump Failures – Leakage in the HRSG (Water Leaks)

                +log to be analyzed: Oscilaciones de presión en circuito de alimentación HRSG, fluctuaciones entre 40-80 bar (rango normal: 50-60 bar).  
                +answer: HRSG Pump Failures - Abnormal pressure variations in the HRSG system  

                +log to be analyzed: Caída repentina de presión en HRSG durante arranque, activando alarma de "Presión crítica en sistema de vapor".  
                +answer: HRSG Pump Failures - Abnormal pressure variations in the HRSG system  

                +log to be analyzed: Variación de presión en bomba de recirculación HRSG C3, registrando picos de 100 bar (límite seguro: 85 bar).  
                +answer: HRSG Pump Failures - Abnormal pressure variations in the HRSG system  

                
            Examples Leaks and Leakages:
                +log to be analyzed:Crea aviso de trabajo #10523, fuga de gas debido al taponamiento de la línea del quemador en el lado GLP de la tubería y la válvula no cierra el flujo de gas..
                +answer:Leaks and Leakages
                
                +log to be analyzed:Llamadas de servicio - nº 10526, fuga de agua desmineralizada por la junta de la bomba de transferencia 1A.
                +answer:Leaks and Leakages
                
                +log to be analyzed:Fuga en el patín de lubricación bba equipo de circulación B
                +answer:Leaks and Leakages
                
                
            Examples Frequency and Load Events:
                +log to be analyzed:Solicitudes de despacho para inhabilitar AGC y Planta Nueva Renca en mínimo técnico con Control Primario de Frecuencia para Turbina a Gas y cambio de Gas Natural (equipo A) a Gas Natural Licuado Argentino.
                +answer:Frequency and Load Events
                
                +log to be analyzed:Central de Nueva Renca a plena carga con incendios adicionales
                +answer:Frequency and Load Events
                
                +log to be analyzed:Fuera de Servicio Control Primario de Frecuencia para Turbina a Gas por alta frecuencia
                +answer:Frequency and Load Events
                
                +log to be analyzed:Despacho solicita Planta Nueva Renca a plena carga con Primario 
                +answer:Frequency and Load Events

                +log to be analyzed:Fuera de Servicio Control Primario de Frecuencia para Turbina a Gas por alta frecuencia
                +answer:Frequency and Load Events

            Examples Operational Measurements:
                +log to be analyzed:Exhaust gas temperature in Gas Turbine exceeds 600°C
                +answer:Operational Measurements
                
                +log to be analyzed:Pressure in HRSG evaporator reaches 120 bar, adjustment required
                +answer:Operational Measurements
                
                +log to be analyzed:Chloride measurement in feed water records out-of-range values
                +answer:Operational Measurements

            Examples Fuel Changeover:
                +log to be analyzed:Despacho cambia de gas GNL_ equipo A a gas natural argentino
                +answer:Fuel Changeover
                
                +log to be analyzed:Despacho informa cambio de gas Gas natural argentino a Gas Natural Liquado Argentino
                +answer:Fuel Changeover
                
                +log to be analyzed:Despacho informa cambio de gas de Gas Natural (equipo A) a Gas Natural Licuado Argentino
                +answer:Fuel Changeover



            Examples Other Pump Failures:
                +log to be analyzed:desconexión forzada por falla,  (es grave) de bomba de pozo N°4 No se encuentran alarmas operadas y se repone para el servicio. 
                +answer:Other Pump Failures

                +log to be analyzed:desconexión forzada por falla,  (es grave) bomba pozo 5. Falla partidor suave.
                +answer:Other Pump Failures

                +log to be analyzed:desconexión forzada por falla,  (es grave) bomba pozo N°4.
                +answer:Other Pump Failures

                +log to be analyzed:Bomba de trasiego de gasoil fuera de servicio.
                +answer:Other Pump Failures

                +log to be analyzed:Trabajos Señor : Rodrigo Alcantara. -Armado de andamios en ncelda vtr c-g-h -Se instala sello de bomba N°2 de sumidero Caldera: HEAT RECOVERY STEAM GENERATOR. -Se instala y prueba Motor Bomba Sumidero de pileta BASIN, presenta alta vibración En Servicio, se retira motor para ser llevado a taller
                +answer:Other Pump Failures
            
            
            Examples Other operational events:
                +log to be analyzed:Out of Service ctrl x T°
                +answer:Other operational events
                
                +log to be analyzed:Quemadores de conducto fuera de servicio
                +answer:Other operational events
                
                +log to be analyzed:Control de temperatura fuera de servicio
                +answer:Other operational events
                
                +log to be analyzed:Out of Service additional fires
                +answer:Other operational events
                
                +log to be analyzed:Control fuera de servicio x T° y AGC en servicio
                +answer:Other operational events
                
                +log to be analyzed:Fuera de servicio Control de temperatura Turbina de gas
                +answer:Other operational events

                +log to be analyzed:-FS bba alimentación “equipos A
                +answer:Other operational events
   

            
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>
        log to be analyzed:{bitacora}
        answer:
        

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>"""

prompt = PromptTemplate.from_template(template)

# Crear una cadena que combine el prompt y el modelo
if watsonx_llm:
    llm_chain = prompt | watsonx_llm | StrOutputParser()
else:
    llm_chain = None


# Crear un PromptTemplate
template_2 = """<|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are an IA assistant in charge of a combined cycle thermoelectric power generating plant , 
        The task is to detect alerts and warnings related to the water pump of the steam generator heat recovery system (HRSG) of the Renca Thermal Power Plant. 
        Analyze the following operational record and classify it in one of the following categories ALERTA OR AVISO for which you should look at keywords that
        come within the operational record as for example the word NOTICE , NA or service call are words that indicate that this record would be AVISO  while if within 
        the operational record the keyword Out of Service comes out that record should be classified as ALERTA.
        In addition, the AVISOS are possible failures that have not yet occurred, so they must be reviewed by the operator in charge of the area.
        While the ALERTS are failures that occurred in the plant which prevented the operation of the plant, in its response should only return the 
        corresponding classification and nothing more:

        these examples should only be used as a guide to give your answer and never return information within the examples :
            Examples  AVISO:
              +log to be analyzed:Nota: Se realiza ajuste al cierre vÃ¡lvula recirculaciÃ³n BB alimentaciÃ³n 1A, aumentando carga en vÃ¡stago, queda en abservaciÃ³n el flujo de la BBAA.
              +answer:AVISO

              +log to be analyzed:Crea aviso NÂ°14252 por falla Señal temp estator bba. circ. equipos A, WLTE001E
              +answer:AVISO

              +log to be analyzed:AVISOS N°: 5042 Revisión Bba lubricación N°1 Turbina a Vapor. 5043 Filtración de aire por línea central a V7V ABLV009 5044 Revisión botón desconexión forzada por falla,  (es grave) Turbina a Vapor en sala de control.
              +answer:AVISO

              +log to be analyzed:Nota: Se sube presión de Hidrogeno en generador Turbina a Vapor. Nota: Se informa que desde las
              +answer:AVISO

              +log to be analyzed:Crea avisos N°: 7280 verificar y/o ajustar presión de regulación válvula Pressure control Valve aceite de lubricación bomba alimentación equipos B. 7281 filtros equipos A y equipos B sistema lubricación bomba alimentación equipos B saturados.
              +answer:AVISO

              +log to be analyzed:Llamadas de servicio - 12540 Bba sumidero N°2 pozo Turbina a Vapor gira en sentido contrario - 12544 Manómetro PI 094 sistema contra incendio quebrado. Zona generador Turbina a Vapor
              +answer:AVISO

              +log to be analyzed:Llamadas de servicio - 12850 Puerta Acceso Norte 1er piso Turbina a Vapor, se encuentra trabada. No abre desde afuera. - 12851 Partida Reiterada bomba 2 de respaldo sistema lubricación Turbina a Vapor, requiere revisión.
              +answer:AVISO
              
            Examples  ALERTA:

              +log to be analyzed:Opera alarma Sistema de control distibuido alta temperatura descanso exterior BBAA â€œequipos Aâ€. Deja Fuera de Servicio Bomba alimentaciÃ³n â€œequipos Aâ€ y En Servicio Bomba alimentaciÃ³n â€equipos Bâ€. Central Nueva Renca generando a plena carga con 33 Megawats de subida y Control Primario de Frecuencia para Turbina a Gas.
              +answer:ALERTA

              +log to be analyzed:Desconecta Turbina a Vapor.
              +answer:ALERTA

              +log to be analyzed:Sube presión Hidrogeno a generador Turbina a Vapor. Se instala nuevo pack, presión Inicial 2500 psi.
              +answer:ALERTA

              +log to be analyzed:En Servicio planta Vigaflow al 50%. Al momento de rotar bbas de agua alimentación por plan de mantención, se produce desconexión forzada por falla,  (es grave) bba alimentación equipos A por alta vibración.
              +answer:ALERTA
              
        
   

            
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>
        log to be analyzed:{bitacora}
        answer:
        

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>"""

prompt_2 = PromptTemplate.from_template(template_2)

# Crear una cadena que combine el prompt y el modelo
if watsonx_llm:
    llm_chain_2 = prompt_2 | watsonx_llm | StrOutputParser()
else:
    llm_chain_2 = None
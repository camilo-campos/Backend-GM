"""
Módulo para verificación y traducción automática de bitácoras de inglés a español.
Enfocado en traducir el texto original de la bitácora, no las clasificaciones.
Implementación asíncrona para soporte de múltiples usuarios.
"""

import asyncio
from typing import Dict, List, Optional, Union
from langdetect import detect, DetectorFactory
from langchain_core.prompts import PromptTemplate
from langchain_ibm import WatsonxLLM
from sqlalchemy.orm import Session
from modelos.modelos import Bitacora, BitacoraB
import os
from dotenv import load_dotenv

# Configurar semilla para resultados consistentes en detección de idioma
DetectorFactory.seed = 0

# Cargar variables de entorno
load_dotenv()

class TraductorBitacoras:
    """Clase para manejar la traducción asíncrona de bitácoras industriales."""
    
    def __init__(self):
        """Inicializar el traductor con configuración de LLM."""
        self.llm = WatsonxLLM(
            model_id="meta-llama/llama-3-3-70b-instruct",
            url=os.getenv("WATSONX_URL"),
            apikey=os.getenv("WATSONX_APIKEY"),
            project_id=os.getenv("WATSONX_PROJECT_ID"),
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "repetition_penalty": 1.1
            }
        )
        
        # Template especializado para traducción de bitácoras industriales
        self.template_traduccion = PromptTemplate(
            input_variables=["texto_bitacora"],
            template="""Eres un traductor especializado en terminología industrial y de plantas de energía.

Tu tarea es traducir el siguiente texto de bitácora industrial del inglés al español, manteniendo:
- Terminología técnica precisa
- Nombres de equipos y componentes
- Códigos y referencias técnicas
- Contexto operacional

TEXTO A TRADUCIR:
{texto_bitacora}

INSTRUCCIONES:
- Traduce ÚNICAMENTE el contenido, no agregues explicaciones
- Mantén la estructura y formato original
- Conserva códigos, números y referencias técnicas exactamente como están
- Usa terminología industrial estándar en español
- Si hay términos muy específicos sin traducción directa, manténlos en inglés entre paréntesis

TRADUCCIÓN:"""
        )
        
        self.chain_traduccion = self.template_traduccion | self.llm

    async def detectar_idioma(self, texto: str) -> str:
        """
        Detectar el idioma de un texto de forma asíncrona.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Código de idioma detectado ('en', 'es', etc.)
        """
        try:
            # Ejecutar detección en un hilo separado para no bloquear
            loop = asyncio.get_event_loop()
            idioma = await loop.run_in_executor(None, detect, texto.strip())
            return idioma
        except Exception as e:
            print(f"Error en detección de idioma: {e}")
            return "unknown"

    async def traducir_con_llm(self, texto: str) -> str:
        """
        Traducir texto usando LLM de forma asíncrona.
        
        Args:
            texto: Texto a traducir
            
        Returns:
            Texto traducido al español
        """
        try:
            # Ejecutar traducción en un hilo separado
            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(
                None, 
                lambda: self.chain_traduccion.invoke({"texto_bitacora": texto}).strip()
            )
            return resultado
        except Exception as e:
            print(f"Error en traducción con LLM: {e}")
            return texto  # Retornar texto original si falla

    async def validar_y_traducir_bitacora(self, bitacora_id: int, db: Session) -> Dict:
        """
        Función principal para validar y traducir una bitácora por ID de forma asíncrona.
        
        Args:
            bitacora_id: ID de la bitácora a procesar
            db: Sesión de base de datos
            
        Returns:
            Diccionario con resultado de la operación
        """
        resultado = {
            "bitacora_id": bitacora_id,
            "traduccion_realizada": False,
            "texto_original": None,
            "texto_traducido": None,
            "idioma_detectado": None,
            "errores": []
        }
        
        try:
            # Buscar primero en tabla Bitacora
            bitacora = db.query(Bitacora).filter(Bitacora.id == bitacora_id).first()
            tabla_origen = "Bitacora"
            
            # Si no se encuentra, buscar en BitacoraB
            if not bitacora:
                bitacora = db.query(BitacoraB).filter(BitacoraB.id == bitacora_id).first()
                tabla_origen = "BitacoraB"
            
            if not bitacora:
                resultado["errores"].append(f"Bitácora con ID {bitacora_id} no encontrada")
                return resultado
            
            # Verificar que existe el campo bitacora
            if not hasattr(bitacora, 'bitacora') or not bitacora.bitacora:
                resultado["errores"].append("Campo 'bitacora' vacío o inexistente")
                return resultado
            
            texto_bitacora = bitacora.bitacora.strip()
            resultado["texto_original"] = texto_bitacora
            
            # Detectar idioma del texto de la bitácora
            idioma = await self.detectar_idioma(texto_bitacora)
            resultado["idioma_detectado"] = idioma
            
            # Si está en inglés, traducir
            if idioma == "en":
                texto_traducido = await self.traducir_con_llm(texto_bitacora)
                
                # Actualizar el campo bitacora en la base de datos
                bitacora.bitacora = texto_traducido
                db.add(bitacora)
                db.commit()
                db.refresh(bitacora)
                
                resultado["traduccion_realizada"] = True
                resultado["texto_traducido"] = texto_traducido
                
                print(f"✅ Bitácora {bitacora_id} ({tabla_origen}) traducida exitosamente")
            else:
                print(f"ℹ️ Bitácora {bitacora_id} ({tabla_origen}) ya está en español o idioma no detectado como inglés")
                
        except Exception as e:
            error_msg = f"Error procesando bitácora {bitacora_id}: {str(e)}"
            resultado["errores"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return resultado

# Función de conveniencia para uso directo
async def verificar_y_traducir_bitacora(bitacora_id: int, db: Session) -> Dict:
    """
    Función asíncrona de conveniencia para verificar y traducir una bitácora.
    
    Args:
        bitacora_id: ID de la bitácora
        db: Sesión de base de datos
        
    Returns:
        Resultado de la traducción
    """
    traductor = TraductorBitacoras()
    return await traductor.validar_y_traducir_bitacora(bitacora_id, db)

async def procesar_bitacoras_batch(bitacoras_ids: List[int], db: Session) -> List[Dict]:
    """
    Procesar múltiples bitácoras de forma asíncrona y concurrente.
    
    Args:
        bitacoras_ids: Lista de IDs de bitácoras
        db: Sesión de base de datos
        
    Returns:
        Lista de resultados de traducción
    """
    traductor = TraductorBitacoras()
    
    # Crear tareas asíncronas para procesamiento concurrente
    tareas = [
        traductor.validar_y_traducir_bitacora(bitacora_id, db) 
        for bitacora_id in bitacoras_ids
    ]
    
    # Ejecutar todas las tareas concurrentemente
    resultados = await asyncio.gather(*tareas, return_exceptions=True)
    
    # Filtrar excepciones y convertir a resultados válidos
    resultados_validos = []
    for i, resultado in enumerate(resultados):
        if isinstance(resultado, Exception):
            resultados_validos.append({
                "bitacora_id": bitacoras_ids[i],
                "traduccion_realizada": False,
                "errores": [f"Excepción: {str(resultado)}"]
            })
        else:
            resultados_validos.append(resultado)
    
    return resultados_validos
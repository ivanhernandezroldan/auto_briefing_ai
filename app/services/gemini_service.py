import os
import base64
import json
import logging
import traceback
import time
import subprocess
from typing import Optional, Tuple

import google.generativeai as genai
from config.logging_config import setup_logger, log_api_error
from config.llm_config import (
    LLM_PROVIDER, LLM_MODEL, GEMINI_API_KEY,
    LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TOP_P, LLM_TOP_K,
    VIDEO_ANALYSIS_PROMPT
)
from app.models.video_analysis_model import VideoAnalysis

logger = setup_logger(__name__)

# Silenciar logs innecesarios
logging.getLogger("google.generativeai").setLevel(logging.ERROR)

class GeminiService:
    """Servicio para analizar videos usando Gemini API directamente"""
    
    def __init__(self, model=None):
        """Inicializa el servicio de análisis de video con Gemini"""
        self.model_name = model or LLM_MODEL
        
        logger.debug(f"Inicializando GeminiService")
        logger.debug(f"Modelo seleccionado: {self.model_name}")
        
        # Verificar API key
        if not GEMINI_API_KEY or GEMINI_API_KEY == "":
            logger.error("API key de Gemini no configurada")
            raise ValueError("API key de Gemini no configurada")
        
        # Configurar la API de Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Preparar el prompt template
        self.prompt_template = VIDEO_ANALYSIS_PROMPT
        
    def _reduce_video_size(self, video_path: str, max_size_mb: int = 10) -> Tuple[str, bool]:
        """Reduce el tamaño del video si es necesario"""
        logger.debug(f"Verificando si es necesario reducir el tamaño del video: {video_path}")
        
        # Obtener tamaño actual
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Si el tamaño es aceptable, no hacer nada
        if file_size_mb <= max_size_mb:
            logger.debug(f"El tamaño del video ({file_size_mb:.2f} MB) es aceptable")
            return video_path, False
            
        # Crear nombre para el archivo reducido
        base_name, ext = os.path.splitext(video_path)
        output_path = f"{base_name}_reduced{ext}"
        
        try:
            # Usar ffmpeg para reducir el tamaño
            logger.info(f"Reduciendo tamaño del video de {file_size_mb:.2f} MB a aproximadamente {max_size_mb} MB")
            
            # Comando para reducir el video
            cmd = [
                "ffmpeg", "-i", video_path, 
                "-vf", "scale=640:-1",  # Reducir resolución
                "-c:v", "libx264", "-crf", "28",  # Aumentar compresión
                "-preset", "fast", 
                "-y",  # Sobrescribir si existe
                output_path
            ]
            
            # Ejecutar comando
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            # Verificar resultado
            if process.returncode != 0:
                logger.error(f"Error al reducir el video: {stderr.decode()}")
                return video_path, False
                
            # Verificar que el archivo se creó correctamente
            if not os.path.exists(output_path):
                logger.error(f"No se pudo crear el archivo reducido: {output_path}")
                return video_path, False
                
            # Verificar el nuevo tamaño
            new_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Video reducido exitosamente. Nuevo tamaño: {new_size:.2f} MB")
            
            return output_path, True
            
        except Exception as e:
            logger.error(f"Error al reducir el video: {str(e)}")
            return video_path, False
    
    def analyze_video(self, video_path: str, max_retries: int = 3) -> Optional[VideoAnalysis]:
        """Analiza un video y genera recomendaciones usando Gemini API directamente"""
        logger.debug(f"Iniciando análisis de video con Gemini: {video_path}")

        # Verificar que el archivo existe
        if not os.path.exists(video_path):
            logger.error(f"No se encontró el archivo de video: {video_path}")
            raise FileNotFoundError(f"No se encontró el archivo de video: {video_path}")

        # Obtener información del archivo
        file_size = os.path.getsize(video_path)
        logger.debug(f"Tamaño del archivo de video: {file_size} bytes ({file_size / (1024 * 1024):.2f} MB)")

        # Verificar si el archivo es demasiado grande y reducirlo si es necesario
        if file_size > 15 * 1024 * 1024:  # 15 MB
            logger.warning(f"El archivo de video es muy grande ({file_size / (1024 * 1024):.2f} MB). Intentando reducir.")
            video_path, was_reduced = self._reduce_video_size(video_path)
            if was_reduced:
                file_size = os.path.getsize(video_path)
                logger.info(f"Video reducido a {file_size / (1024 * 1024):.2f} MB")

        # Leer el archivo de video
        logger.debug("Leyendo archivo de video")
        with open(video_path, "rb") as f:
            video_data = f.read()

        # Codificar el video en base64
        logger.debug(f"Codificando video en base64 (tamaño: {len(video_data)} bytes)")
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        logger.debug(f"Tamaño de la cadena base64: {len(video_base64)} caracteres")

        # Implementar reintentos con backoff exponencial
        retry_count = 0
        while retry_count <= max_retries:
            try:
                # Cargar el modelo de Gemini
                logger.debug(f"Cargando modelo Gemini: {self.model_name}")
                model = genai.GenerativeModel(self.model_name)
                
                # Crear objeto Part para el video
                video_part = {"mime_type": "video/mp4", "data": base64.b64decode(video_base64)}
                
                # Preparar el prompt
                prompt_text = self.prompt_template
                
                # Enviar la solicitud al modelo con el video y el prompt
                logger.info(f"Enviando video al modelo Gemini para análisis (intento {retry_count + 1}/{max_retries + 1})")
                
                try:
                    # Configurar parámetros de generación
                    generation_config = genai.types.GenerationConfig(
                        temperature=LLM_TEMPERATURE,
                        top_p=LLM_TOP_P,
                        top_k=LLM_TOP_K,
                        max_output_tokens=LLM_MAX_TOKENS
                    )
                    
                    # Crear la solicitud con el video y el prompt
                    parts = [
                        {
                            "inline_data": {
                                "mime_type": "video/mp4",
                                "data": video_base64
                            }
                        },
                        {
                            "text": prompt_text
                        }
                    ]
                    
                    # Enviar solicitud
                    response = model.generate_content(
                        parts,
                        generation_config=generation_config
                    )
                    
                    # Procesar la respuesta
                    cleaned_response = response.text
                    logger.debug(f"Respuesta original recibida: {cleaned_response[:200]}...")
                    
                    # Extraer el JSON de la respuesta
                    # Buscar el primer '{' y el último '}'
                    try:
                        start_idx = cleaned_response.find('{')
                        end_idx = cleaned_response.rfind('}')
                        
                        if start_idx >= 0 and end_idx > start_idx:
                            # Extraer solo la parte JSON
                            json_str = cleaned_response[start_idx:end_idx+1]
                            logger.debug(f"JSON extraído: {json_str[:200]}...")
                            
                            # Parsear el JSON
                            json_response = json.loads(json_str)
                            logger.debug("Análisis completado exitosamente")
                            
                            # Verificar que el JSON tiene los campos requeridos
                            required_fields = ["descripcion_original", "titulo_portada", "idea_video", "gancho_video", "acciones", 
                                              "dialogo", "musica", "expectativas_cumplidas", "caption_video"]
                            
                            # Mapear campos si es necesario (por si el modelo usa nombres diferentes)
                            field_mapping = {
                                "titulo": "titulo_portada",
                                "gancho_inicial": "gancho_video",
                                "caption": "caption_video"
                            }
                            
                            # Aplicar mapeo de campos
                            for old_field, new_field in field_mapping.items():
                                if old_field in json_response and new_field not in json_response:
                                    json_response[new_field] = json_response.pop(old_field)
                            
                            # Verificar campos requeridos
                            missing_fields = [field for field in required_fields if field not in json_response]
                            if missing_fields:
                                logger.warning(f"Faltan campos en la respuesta JSON: {missing_fields}")
                                # Intentar completar campos faltantes con valores por defecto
                                for field in missing_fields:
                                    if field == "hashtags":
                                        json_response[field] = ["#BarentBarefoot", "#EntrenamientoNatural", "#CuerpoFuerte"]
                                    else:
                                        json_response[field] = "No especificado"
                            
                            # Asegurarse de que el campo hashtags existe
                            if "hashtags" not in json_response:
                                # Extraer hashtags del caption si es posible
                                if "caption_video" in json_response:
                                    # Buscar palabras que empiezan con #
                                    caption = json_response["caption_video"]
                                    hashtags = [word for word in caption.split() if word.startswith("#")]
                                    if hashtags:
                                        json_response["hashtags"] = hashtags
                                    else:
                                        json_response["hashtags"] = ["#BarentBarefoot", "#EntrenamientoNatural", "#CuerpoFuerte"]
                                else:
                                    json_response["hashtags"] = ["#BarentBarefoot", "#EntrenamientoNatural", "#CuerpoFuerte"]
                            
                            # Devolver el resultado como objeto VideoAnalysis
                            return VideoAnalysis(**json_response)
                        else:
                            logger.error("No se pudo encontrar un objeto JSON válido en la respuesta")
                            logger.error(f"Respuesta original: {cleaned_response[:500]}...")
                            return None
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error al parsear la respuesta JSON: {e}")
                        logger.error(f"Respuesta original: {cleaned_response[:500]}...")
                        return None
                    
                except Exception as e:
                    # Manejar errores específicos de la API
                    logger.error(f"Error al invocar el modelo: {type(e).__name__}: {str(e)}")
                    logger.error(f"Detalles del error: {traceback.format_exc()}")
                    log_api_error(logger, e)
                    
                    # Implementar lógica de reintento para límites de tasa y problemas de cuota
                    error_str = str(e).lower()
                    if "quota" in error_str or "rate limit" in error_str:
                        if retry_count < max_retries:
                            wait_time = (2 ** retry_count) * 5  # Backoff exponencial
                            logger.warning(f"Se ha alcanzado el límite de cuota. Reintentando en {wait_time} segundos...")
                            time.sleep(wait_time)
                            retry_count += 1
                            continue  # Reintentar la llamada a la API
                        else:
                            logger.error("Se ha alcanzado el límite de cuota de la API y se agotaron los reintentos")
                            return None  # Salir del bucle de reintentos
                    
                    elif "too large" in error_str or "size limit" in error_str:
                        logger.error("El video parece ser demasiado grande para la API")
                        break  # Salir del bucle de reintentos
                    
                    return None  # Devolver None si no es un error recuperable
                
            except Exception as e:
                logger.error(f"Error al preparar el mensaje: {type(e).__name__}: {str(e)}")
                logger.error(f"Detalles del error: {traceback.format_exc()}")
                log_api_error(logger, e)
                return None
            
            finally:
                # Limpiar la cadena base64
                video_base64 = None
            
            # Si llegamos aquí sin continuar el bucle, salimos
            break
            
        return None 
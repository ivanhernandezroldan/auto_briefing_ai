import os
import base64
import logging
import traceback
import time
import subprocess
from typing import Optional, Tuple
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from config.logging_config import setup_logger, log_api_error
from config.llm_config import (
    LLM_PROVIDER, LLM_MODEL, GEMINI_API_KEY, OPENAI_API_KEY,
    LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TOP_P, LLM_TOP_K,
    VIDEO_ANALYSIS_PROMPT
)
from app.models.video_analysis_model import VideoAnalysis

logger = setup_logger(__name__)

# Silenciar logs de Langchain
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_core").setLevel(logging.ERROR)

class VideoAnalysisService:
    """Servicio para analizar videos usando modelos de lenguaje multimodales"""
    
    def __init__(self, provider=None, model=None):
        """Inicializa el servicio de análisis de video"""
        self.provider = (provider or LLM_PROVIDER).lower() # Convert to lowercase for consistency
        self.model = model or LLM_MODEL
        
        logger.debug(f"Inicializando VideoAnalysisService con proveedor: {self.provider}")
        logger.debug(f"Modelo seleccionado: {self.model}")
        
        # Verificar API key después de inicializar self.provider
        if self.provider == "gemini" and (not GEMINI_API_KEY or GEMINI_API_KEY == ""):
            logger.error("API key de Gemini no configurada")
            raise ValueError("API key de Gemini no configurada")
        elif self.provider == "openai" and (not OPENAI_API_KEY or OPENAI_API_KEY == ""):
            logger.error("API key de OpenAI no configurada")
            raise ValueError("API key de OpenAI no configurada")
        
        # Configurar el modelo según el proveedor
        if self.provider == "gemini":
            logger.debug("Configurando modelo Gemini")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=GEMINI_API_KEY,
                temperature=LLM_TEMPERATURE,
                top_p=LLM_TOP_P,
                top_k=LLM_TOP_K,
                max_output_tokens=LLM_MAX_TOKENS,
                convert_system_message_to_human=True
            )
        elif self.provider == "openai":
            logger.debug("Configurando modelo OpenAI")
            self.llm = ChatOpenAI(
                model=self.model,
                openai_api_key=OPENAI_API_KEY,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
        else:
            logger.error(f"Proveedor no soportado: {self.provider}")
            raise ValueError(f"Proveedor no soportado: {self.provider}")
        
        # Crear el prompt
        self.prompt_template = PromptTemplate(
            template=VIDEO_ANALYSIS_PROMPT,
            input_variables=[]
        )
        logger.debug("Servicio inicializado correctamente")
    
    def _reduce_video_size(self, video_path: str, max_size_mb: int = 10) -> Tuple[str, bool]:
        """
        Reduce el tamaño del video si es mayor que el tamaño máximo especificado
        
        Args:
            video_path: Ruta al archivo de video
            max_size_mb: Tamaño máximo en MB
            
        Returns:
            Tuple[str, bool]: Ruta al video reducido y un booleano indicando si se redujo
        """
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # Tamaño en MB
        
        if file_size <= max_size_mb:
            logger.debug(f"El video ya está por debajo del tamaño máximo ({file_size:.2f} MB)")
            return video_path, False
        
        # Crear nombre para el archivo reducido
        base_name, ext = os.path.splitext(video_path)
        reduced_path = f"{base_name}_reduced{ext}"
        
        # Calcular el bitrate objetivo (en kbps) para lograr el tamaño deseado
        # Fórmula aproximada: bitrate = (tamaño_deseado_en_bits) / (duración_en_segundos)
        try:
            # Obtener la duración del video
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", 
                   "default=noprint_wrappers=1:nokey=1", video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"No se pudo obtener la duración del video: {result.stderr}")
                # Usar un bitrate bajo por defecto
                target_bitrate = "500k"
            else:
                duration = float(result.stdout.strip())
                # Calcular bitrate objetivo (80% del máximo teórico para dejar margen)
                target_bitrate_kbps = int((max_size_mb * 8 * 1024 * 0.8) / duration)
                target_bitrate = f"{target_bitrate_kbps}k"
                
            logger.debug(f"Reduciendo video con bitrate objetivo: {target_bitrate}")
            
            # Reducir el video
            cmd = ["ffmpeg", "-i", video_path, "-b:v", target_bitrate, "-maxrate", target_bitrate, 
                   "-bufsize", f"{int(target_bitrate_kbps/2)}k", "-vf", "scale=-2:720", 
                   "-c:a", "aac", "-b:a", "128k", "-y", reduced_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error al reducir el video: {result.stderr}")
                return video_path, False
            
            # Verificar el tamaño del archivo reducido
            reduced_size = os.path.getsize(reduced_path) / (1024 * 1024)
            logger.info(f"Video reducido de {file_size:.2f} MB a {reduced_size:.2f} MB")
            
            return reduced_path, True
            
        except Exception as e:
            logger.error(f"Error al reducir el video: {str(e)}")
            return video_path, False

    def analyze_video(self, video_path: str, max_retries: int = 3) -> Optional[VideoAnalysis]:
        """Analiza un video y genera recomendaciones"""
        logger.debug(f"Iniciando análisis de video: {video_path}")

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
                # Preparar el mensaje con el video
                logger.debug("Preparando mensaje para el modelo")

                if self.provider == "gemini":  # Use the lowercase attribute for comparison
                    message_content = [
                        {"type": "text", "text": self.prompt_template.format()},
                        #{"type": "image_url", "image_url": {"url": f"data:video/mp4;base64,{video_base64}"}},
                    ]
                elif self.provider == "openai":
                    # Formato esperado por OpenAI
                    message_content = [
                        {"type": "text", "text": self.prompt_template.format()},
                        # {
                        #     "type": "image_url",
                        #     "image_url": {
                        #         "url": f"data:video/mp4;base64,{video_base64}",
                        #     },
                        # },
                    ]
                else:
                    logger.error(f"Proveedor no soportado: {self.provider}")
                    raise ValueError(f"Proveedor no soportado: {self.provider}")

                # Create the HumanMessage
                message = HumanMessage(content=message_content)

                # Obtener respuesta del modelo
                logger.info(f"Enviando video al modelo {self.provider} para análisis (intento {retry_count + 1}/{max_retries + 1})")

                try:
                    # Invoke the LLM
                    response = self.llm.invoke([message])

                    # Print content of the response
                    logger.debug(f"Response content: {response.content}")

                    # Log raw response and return if successful
                    logger.debug("Análisis completado exitosamente")

                    return VideoAnalysis(result=response.content)

                except Exception as e:
                    # Handle specific API errors
                    logger.error(f"Error al invocar el modelo: {type(e).__name__}: {str(e)}")
                    logger.error(f"Detalles del error: {traceback.format_exc()}")
                    log_api_error(logger, e)

                    # Implement retry logic for rate limits and quota issues
                    error_str = str(e).lower()
                    if "quota" in error_str or "rate limit" in error_str:
                        if retry_count < max_retries:
                            wait_time = (2 ** retry_count) * 5  # Exponential backoff
                            logger.warning(f"Se ha alcanzado el límite de cuota. Reintentando en {wait_time} segundos...")
                            time.sleep(wait_time)
                            retry_count += 1
                            continue  # Retry the API call
                        else:
                            logger.error("Se ha alcanzado el límite de cuota de la API y se agotaron los reintentos")
                            return None  # Exit retry loop

                    elif "too large" in error_str or "size limit" in error_str:
                        logger.error("El video parece ser demasiado grande para la API")
                        # You could potentially try reducing the video further here if possible
                        break  # Exit retry loop

                    return None  # Return None if not a recoverable error

            except Exception as e:
                logger.error(f"Error al preparar el mensaje: {type(e).__name__}: {str(e)}")
                logger.error(f"Detalles del error: {traceback.format_exc()}")
                log_api_error(logger, e)
                return None

            finally:
                # Clean up base64 string
                video_base64 = None

        return None
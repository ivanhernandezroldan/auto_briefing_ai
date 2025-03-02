import os
import cv2
from config.settings import CAPTURE_INTERVAL
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class ExtractionService:
    """Servicio para extraer contenido de videos"""
    
    @staticmethod
    def extract_frames(video_path, output_dir):
        """
        Extrae frames de un video cada X segundos
        
        Args:
            video_path: Ruta al archivo de video
            output_dir: Directorio donde guardar las capturas
        
        Returns:
            bool: True si la extracción fue exitosa, False en caso contrario
        """
        logger.debug(f"Iniciando extracción de frames del video: {video_path}")
        logger.debug(f"Directorio de salida: {output_dir}")
        logger.debug(f"Intervalo de captura: {CAPTURE_INTERVAL} segundos")
        
        # Crear directorio para las capturas si no existe
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Directorio de capturas asegurado: {output_dir}")
        
        # Abrir el video
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            logger.error(f"Error: No se pudo abrir el video {video_path}")
            return False
        
        # Obtener FPS y duración del video
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        logger.debug(f"Información del video:")
        logger.debug(f"  - FPS: {fps}")
        logger.debug(f"  - Total frames: {total_frames}")
        logger.debug(f"  - Duración: {duration:.2f} segundos")
        
        # Calcular en qué frames hacer las capturas
        frame_interval = int(fps * CAPTURE_INTERVAL)
        current_frame = 0
        frame_count = 0
        
        logger.info(f"Extrayendo frames cada {CAPTURE_INTERVAL} segundos...")
        
        while current_frame < total_frames:
            video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = video.read()
            
            if ret:
                # Guardar el frame como imagen
                output_path = os.path.join(output_dir, f"frame_{frame_count:03d}.jpg")
                cv2.imwrite(output_path, frame)
                logger.debug(f"Frame guardado: {output_path}")
                frame_count += 1
            else:
                logger.warning(f"No se pudo leer el frame {current_frame}")
            
            current_frame += frame_interval
        
        video.release()
        logger.info(f"Extracción completada. Se extrajeron {frame_count} frames")
        return True 
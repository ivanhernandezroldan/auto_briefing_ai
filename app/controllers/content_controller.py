import os
import json
from datetime import datetime
from app.services.download_service import DownloadService
from app.services.extraction_service import ExtractionService
from app.services.gemini_service import GeminiService
from app.services.excel_service import ExcelService
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class ContentController:
    """Controlador para la generación de contenido"""
    
    def __init__(self):
        self.download_service = DownloadService()
        self.extraction_service = ExtractionService()
        self.video_analysis_service = GeminiService()
        self.excel_service = ExcelService()
        logger.debug("ContentController inicializado con servicios: download, extraction, gemini, excel")
    
    def process_link(self, url, output_dir, index=1):
        """
        Procesa un enlace individual
        
        Args:
            url: URL del video
            output_dir: Directorio base de salida
            index: Índice del enlace (para nombrar archivos)
        
        Returns:
            dict: Resultados del procesamiento
        """
        logger.debug(f"Iniciando procesamiento del enlace #{index}: {url}")
        
        # Crear estructura de directorios
        content_dir = os.path.join(output_dir, f"archivo_{index}")
        video_path = os.path.join(content_dir, f"archivo_{index}_video.mp4")
        audio_path = os.path.join(content_dir, f"archivo_{index}_audio.mp3")
        captures_dir = os.path.join(content_dir, "capturas_del_video")
        
        logger.debug(f"Rutas configuradas para archivo_{index}:")
        logger.debug(f"  - Video: {video_path}")
        logger.debug(f"  - Audio: {audio_path}")
        logger.debug(f"  - Capturas: {captures_dir}")
        
        # Descargar video y audio
        logger.info(f"Procesando enlace #{index}: {url}")
        video_success = self.download_service.download_video(url, video_path)
        audio_success = self.download_service.extract_audio(url, audio_path)
        
        logger.debug(f"Resultado de descargas para archivo_{index}:")
        logger.debug(f"  - Video: {'✓' if video_success else '✗'}")
        logger.debug(f"  - Audio: {'✓' if audio_success else '✗'}")
        
        # Extraer frames si el video se descargó correctamente
        frames_success = False
        if video_success:
            logger.debug(f"Iniciando extracción de frames para archivo_{index}")
            frames_success = self.extraction_service.extract_frames(video_path, captures_dir)
            logger.debug(f"Extracción de frames: {'✓' if frames_success else '✗'}")
        
        # Análisis con LLM
        analysis = None
        if video_success:
            logger.info(f"Iniciando análisis de video con modelo multimodal para archivo_{index}")
            analysis = self.video_analysis_service.analyze_video(video_path)
            
            # Guardar el análisis en un archivo JSON
            if analysis:
                analysis_path = os.path.join(content_dir, f"archivo_{index}_analysis.json")
                with open(analysis_path, "w", encoding="utf-8") as f:
                    try:
                        # Intentar usar model_dump_json (Pydantic v2)
                        json_str = analysis.model_dump_json(indent=2)
                        f.write(json_str)
                    except AttributeError:
                        # Fallback a json.dumps (para cualquier versión de Pydantic)
                        try:
                            import json
                            result_dict = analysis.dict() if hasattr(analysis, 'dict') else analysis.model_dump()
                            f.write(json.dumps(result_dict, indent=2, ensure_ascii=False))
                        except Exception as e:
                            logger.error(f"Error al serializar el análisis: {e}")
                            # Último recurso: convertir a string y guardar
                            f.write(str(analysis))
                logger.debug(f"Análisis guardado en: {analysis_path}")
            else:
                logger.warning(f"No se pudo obtener análisis para archivo_{index}")
        
        return {
            "url": url,
            "video_success": video_success,
            "audio_success": audio_success,
            "frames_success": frames_success,
            "analysis": analysis
        }
    
    def process_links_file(self, file_path, output_dir):
        """
        Procesa un archivo con múltiples enlaces
        
        Args:
            file_path: Ruta al archivo de enlaces
            output_dir: Directorio base de salida
        
        Returns:
            list: Resultados del procesamiento
        """
        logger.info(f"Iniciando procesamiento de archivo de enlaces: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"El archivo {file_path} no existe.")
            return []
        
        if not os.path.exists(output_dir):
            logger.debug(f"Creando directorio de salida: {output_dir}")
            os.makedirs(output_dir)

        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir_with_date = os.path.join(output_dir, date_str)
        logger.debug(f"Directorio de salida con fecha: {output_dir_with_date}")
        
        results = []
        # Leer todas las líneas de una vez
        with open(file_path, 'r') as file:
            links = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
        
        logger.info(f"Se encontraron {len(links)} enlaces para procesar")
        
        # Procesar cada enlace
        for i, url in enumerate(links):
            result = self.process_link(url, output_dir_with_date, i+1)
            results.append(result)
        
        # Guardar los resultados en un archivo JSON
        results_file = os.path.join(output_dir_with_date, f"processing_results_{date_str}.json")
        try:
            # Convertir los resultados a un formato serializable
            serializable_results = []
            for result in results:
                serializable_result = {
                    "url": result["url"],
                    "video_success": result["video_success"],
                    "audio_success": result["audio_success"],
                    "frames_success": result["frames_success"],
                    # No incluimos el análisis completo porque ya está guardado en archivos individuales
                    "has_analysis": result["analysis"] is not None
                }
                serializable_results.append(serializable_result)
                
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            logger.debug(f"Resultados guardados en: {results_file}")
        except Exception as e:
            logger.error(f"Error al guardar los resultados: {e}")
        
        # Mostrar resumen
        self._print_summary(results)
        logger.info(f"Procesamiento completado. {len(results)} enlaces procesados.")
        
        # Generar archivo Excel con los análisis
        logger.info("Generando archivo Excel con los análisis")
        excel_generated = self.excel_service.generate_excel_from_directory(output_dir)
        if excel_generated:
            logger.info("Archivo Excel generado exitosamente")
        else:
            logger.warning("No se pudo generar el archivo Excel")
        
        return results
    
    def _print_summary(self, results):
        """
        Imprime un resumen de los resultados
        
        Args:
            results: Lista de resultados de procesamiento
        """
        logger.info("=== RESUMEN DE PROCESAMIENTO ===")
        for i, result in enumerate(results):
            status = []
            if result["video_success"]:
                status.append("Video ✓")
            else:
                status.append("Video ✗")
                
            if result["audio_success"]:
                status.append("Audio ✓")
            else:
                status.append("Audio ✗")
                
            if result.get("frames_success"):
                status.append("Frames ✓")
            else:
                status.append("Frames ✗")
            
            status_str = ', '.join(status)
            logger.info(f"{i+1}. {result['url']}: {status_str}")
            if result['analysis']:
                logger.debug(f"Análisis para enlace #{i+1}: {result['analysis']}")
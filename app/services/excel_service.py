import os
import json
import shutil
import pandas as pd
from typing import List, Dict, Any
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class ExcelService:
    """Servicio para generar archivos Excel a partir de análisis JSON"""
    
    def __init__(self):
        """Inicializa el servicio de generación de Excel"""
        logger.debug("ExcelService inicializado")
    
    def _cleanup_directory(self, date_path: str, excel_file: str) -> bool:
        """
        Elimina todos los archivos y carpetas en el directorio de fecha excepto el archivo Excel
        
        Args:
            date_path: Ruta al directorio de fecha
            excel_file: Ruta completa al archivo Excel que se debe conservar
            
        Returns:
            bool: True si la limpieza se realizó correctamente, False en caso contrario
        """
        try:
            logger.info(f"Iniciando limpieza del directorio: {date_path}")
            
            # Obtener la lista de todos los elementos en el directorio
            items = os.listdir(date_path)
            
            # Nombre del archivo Excel (sin la ruta)
            excel_filename = os.path.basename(excel_file)
            
            # Eliminar todos los elementos excepto el archivo Excel
            for item in items:
                item_path = os.path.join(date_path, item)
                
                # Conservar solo el archivo Excel
                if item == excel_filename:
                    logger.debug(f"Conservando archivo Excel: {item_path}")
                    continue
                
                # Eliminar el resto de archivos y carpetas
                try:
                    if os.path.isdir(item_path):
                        logger.debug(f"Eliminando directorio: {item_path}")
                        shutil.rmtree(item_path)
                    else:
                        logger.debug(f"Eliminando archivo: {item_path}")
                        os.remove(item_path)
                except Exception as e:
                    logger.error(f"Error al eliminar {item_path}: {str(e)}")
            
            logger.info(f"Limpieza completada para el directorio: {date_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error durante la limpieza del directorio {date_path}: {str(e)}")
            return False
    
    def generate_excel_from_directory(self, output_dir: str) -> bool:
        """
        Genera un archivo Excel para cada carpeta de fecha en el directorio de salida
        
        Args:
            output_dir: Directorio base de salida
            
        Returns:
            bool: True si se generó al menos un archivo Excel, False en caso contrario
        """
        logger.info(f"Generando archivos Excel para el directorio: {output_dir}")
        
        # Verificar que el directorio existe
        if not os.path.exists(output_dir):
            logger.error(f"El directorio {output_dir} no existe")
            return False
        
        # Buscar carpetas de fecha en el directorio de salida
        date_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        
        if not date_dirs:
            logger.warning(f"No se encontraron carpetas de fecha en {output_dir}")
            return False
        
        excel_generated = False
        
        # Procesar cada carpeta de fecha
        for date_dir in date_dirs:
            date_path = os.path.join(output_dir, date_dir)
            logger.debug(f"Procesando carpeta de fecha: {date_path}")
            
            # Buscar carpetas de archivos en la carpeta de fecha
            file_dirs = [d for d in os.listdir(date_path) if os.path.isdir(os.path.join(date_path, d))]
            
            if not file_dirs:
                logger.warning(f"No se encontraron carpetas de archivos en {date_path}")
                continue
            
            # Buscar el archivo de resultados del procesamiento
            results_data = {}
            results_files = [f for f in os.listdir(date_path) if f.startswith('processing_results_') and f.endswith('.json')]
            
            if results_files:
                results_file = os.path.join(date_path, results_files[0])
                logger.debug(f"Encontrado archivo de resultados: {results_file}")
                
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        processing_results = json.load(f)
                        
                    # Crear un diccionario con las URLs indexadas por número de archivo
                    for i, result in enumerate(processing_results):
                        if isinstance(result, dict) and 'url' in result:
                            results_data[i+1] = result['url']
                            
                    logger.debug(f"Cargadas {len(results_data)} URLs de videos originales")
                except Exception as e:
                    logger.error(f"Error al leer el archivo de resultados {results_file}: {str(e)}")
            else:
                logger.warning(f"No se encontró archivo de resultados en {date_path}")
            
            # Recopilar datos para el Excel
            excel_data = []
            
            # Procesar cada carpeta de archivo
            for file_dir in file_dirs:
                file_path = os.path.join(date_path, file_dir)
                logger.debug(f"Procesando carpeta de archivo: {file_path}")
                
                # Buscar el archivo de análisis JSON
                analysis_files = [f for f in os.listdir(file_path) if f.endswith('_analysis.json')]
                
                if not analysis_files:
                    logger.warning(f"No se encontró archivo de análisis en {file_path}")
                    continue
                
                # Obtener la URL del video original
                # Asumimos que el nombre de la carpeta es archivo_N donde N es el índice
                try:
                    index = int(file_dir.split('_')[-1]) if '_' in file_dir else 0
                except ValueError:
                    index = 0
                
                # Leer el archivo de análisis
                analysis_file = os.path.join(file_path, analysis_files[0])
                logger.debug(f"Leyendo archivo de análisis: {analysis_file}")
                
                try:
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    
                    # Crear un diccionario con los datos para el Excel
                    row_data = {}
                    
                    # Obtener la URL del video original desde los resultados
                    if index in results_data:
                        row_data['url_video_original'] = results_data[index]
                    else:
                        row_data['url_video_original'] = f"Video #{index}"
                    
                    # Añadir todos los campos del análisis
                    for key, value in analysis_data.items():
                        # Si el valor es un diccionario o lista, lo convertimos a string JSON
                        if isinstance(value, (dict, list)):
                            row_data[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            row_data[key] = value
                    
                    excel_data.append(row_data)
                    
                except Exception as e:
                    logger.error(f"Error al procesar el archivo {analysis_file}: {str(e)}")
                    continue
            
            # Generar el Excel si hay datos
            if excel_data:
                excel_file = os.path.join(date_path, f"analisis_{date_dir}.xlsx")
                logger.info(f"Generando archivo Excel: {excel_file}")
                
                try:
                    # Crear DataFrame y guardar como Excel
                    df = pd.DataFrame(excel_data)
                    
                    # Reordenar columnas para que url_video_original sea la primera
                    cols = ['url_video_original'] + [col for col in df.columns if col != 'url_video_original']
                    df = df[cols]
                    
                    # Guardar como Excel
                    df.to_excel(excel_file, index=False, engine='openpyxl')
                    logger.info(f"Archivo Excel generado exitosamente: {excel_file}")
                    excel_generated = True
                    
                    # Limpiar el directorio después de generar el Excel
                    cleanup_success = self._cleanup_directory(date_path, excel_file)
                    if cleanup_success:
                        logger.info(f"Limpieza exitosa del directorio: {date_path}")
                    else:
                        logger.warning(f"No se pudo completar la limpieza del directorio: {date_path}")
                    
                except Exception as e:
                    logger.error(f"Error al generar el archivo Excel {excel_file}: {str(e)}")
            else:
                logger.warning(f"No hay datos para generar el Excel en {date_path}")
        
        return excel_generated 
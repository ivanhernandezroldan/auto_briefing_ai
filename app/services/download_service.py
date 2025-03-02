import subprocess
import os
import shutil
from config.settings import (
    USER_AGENT, 
    INSTAGRAM_USERNAME, 
    INSTAGRAM_PASSWORD,
    INSTAGRAM_BROWSER,
    INSTAGRAM_PROFILE,
    INSTAGRAM_COOKIES_FILE
)
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class DownloadService:
    """Servicio para descargar videos y audio de plataformas sociales"""
    
    @staticmethod
    def download_video(url, output_path):
        """
        Descarga un video desde una URL
        
        Args:
            url: URL del video
            output_path: Ruta donde guardar el video
        
        Returns:
            bool: True si la descarga fue exitosa, False en caso contrario
        """
        logger.debug(f"Iniciando descarga de video: {url}")
        logger.debug(f"Ruta de salida: {output_path}")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.debug(f"Directorio de salida asegurado: {os.path.dirname(output_path)}")
        
        # Comando base
        cmd = [
            "yt-dlp", 
            url,
            "-f", "b",  # Usar 'b' en lugar de 'best' para evitar advertencias
            "--no-check-certificate",
            "--user-agent", USER_AGENT,
            "-o", output_path
        ]
        
        # Añadir credenciales si es una URL de Instagram
        if "instagram.com" in url:
            logger.debug("Detectada URL de Instagram, añadiendo credenciales")
            
            # Método 1: Usar archivo de cookies si existe
            if os.path.exists(INSTAGRAM_COOKIES_FILE):
                logger.debug(f"Usando archivo de cookies: {INSTAGRAM_COOKIES_FILE}")
                cmd.extend(["--cookies", INSTAGRAM_COOKIES_FILE])
            
            # Método 2: Usar nombre de usuario y contraseña
            elif INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                logger.debug("Usando credenciales de usuario y contraseña")
                cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
            
            # Método 3: Usar cookies del navegador (puede fallar por permisos)
            elif INSTAGRAM_BROWSER and INSTAGRAM_BROWSER.lower() in ["chrome", "firefox", "safari", "edge", "opera"]:
                try:
                    logger.debug(f"Usando cookies del navegador {INSTAGRAM_BROWSER}")
                    if INSTAGRAM_PROFILE:
                        cmd.extend(["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}"])
                    else:
                        cmd.extend(["--cookies-from-browser", INSTAGRAM_BROWSER])
                except Exception as e:
                    logger.warning(f"Error al acceder a cookies del navegador: {str(e)}")
                    # Fallback a credenciales si hay error con cookies
                    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                        logger.debug("Fallback a credenciales de usuario y contraseña")
                        cmd = [item for item in cmd if item not in ["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}", INSTAGRAM_BROWSER]]
                        cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
            
            # Si no hay credenciales configuradas, advertir
            else:
                logger.warning("No se han configurado credenciales para Instagram. Es posible que la descarga falle.")
        
        logger.debug(f"Comando de descarga: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        
        if success:
            logger.info(f"Video descargado exitosamente: {output_path}")
        else:
            logger.error(f"Error al descargar video: {result.stderr}")
            logger.debug(f"Código de salida: {result.returncode}")
            logger.debug(f"Salida de error: {result.stderr}")
            
            # Intentar con método alternativo si falló
            if "instagram.com" in url and ("error has occurred" in result.stderr.lower() or "permission denied" in result.stderr.lower()):
                logger.info("Intentando método alternativo de descarga para Instagram")
                
                # Si falló con cookies del navegador, intentar con credenciales
                if "--cookies-from-browser" in ' '.join(cmd) and INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                    logger.debug("Cambiando a autenticación por usuario/contraseña")
                    alt_cmd = [item for item in cmd if item not in ["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}", INSTAGRAM_BROWSER]]
                    alt_cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
                    
                    logger.debug(f"Comando alternativo: {' '.join(alt_cmd)}")
                    alt_result = subprocess.run(alt_cmd, capture_output=True, text=True)
                    success = alt_result.returncode == 0
                    
                    if success:
                        logger.info(f"Video descargado exitosamente con método alternativo: {output_path}")
                    else:
                        logger.error(f"Error al descargar video con método alternativo: {alt_result.stderr}")
                
                # Si falló con credenciales o cookies del navegador, intentar sin autenticación
                elif not success:
                    logger.debug("Intentando descarga sin autenticación")
                    basic_cmd = [
                        "yt-dlp", 
                        url,
                        "-f", "b",
                        "--no-check-certificate",
                        "--user-agent", USER_AGENT,
                        "-o", output_path
                    ]
                    
                    logger.debug(f"Comando básico: {' '.join(basic_cmd)}")
                    basic_result = subprocess.run(basic_cmd, capture_output=True, text=True)
                    success = basic_result.returncode == 0
                    
                    if success:
                        logger.info(f"Video descargado exitosamente sin autenticación: {output_path}")
                    else:
                        logger.error(f"Error al descargar video sin autenticación: {basic_result.stderr}")
        
        return success
    
    @staticmethod
    def extract_audio(url, output_path):
        """
        Extrae el audio de un video desde una URL
        
        Args:
            url: URL del video
            output_path: Ruta donde guardar el audio
        
        Returns:
            bool: True si la extracción fue exitosa, False en caso contrario
        """
        logger.debug(f"Iniciando extracción de audio: {url}")
        logger.debug(f"Ruta de salida: {output_path}")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.debug(f"Directorio de salida asegurado: {os.path.dirname(output_path)}")
        
        # Asegurar que la extensión sea correcta
        base_path = output_path.replace(".mp3", "")
        
        # Comando base
        cmd = [
            "yt-dlp", 
            url,
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--no-check-certificate",
            "--user-agent", USER_AGENT,
            "-o", f"{base_path}.%(ext)s"
        ]
        
        # Añadir credenciales si es una URL de Instagram
        if "instagram.com" in url:
            logger.debug("Detectada URL de Instagram, añadiendo credenciales")
            
            # Método 1: Usar archivo de cookies si existe
            if os.path.exists(INSTAGRAM_COOKIES_FILE):
                logger.debug(f"Usando archivo de cookies: {INSTAGRAM_COOKIES_FILE}")
                cmd.extend(["--cookies", INSTAGRAM_COOKIES_FILE])
            
            # Método 2: Usar nombre de usuario y contraseña
            elif INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                logger.debug("Usando credenciales de usuario y contraseña")
                cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
            
            # Método 3: Usar cookies del navegador (puede fallar por permisos)
            elif INSTAGRAM_BROWSER and INSTAGRAM_BROWSER.lower() in ["chrome", "firefox", "safari", "edge", "opera"]:
                try:
                    logger.debug(f"Usando cookies del navegador {INSTAGRAM_BROWSER}")
                    if INSTAGRAM_PROFILE:
                        cmd.extend(["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}"])
                    else:
                        cmd.extend(["--cookies-from-browser", INSTAGRAM_BROWSER])
                except Exception as e:
                    logger.warning(f"Error al acceder a cookies del navegador: {str(e)}")
                    # Fallback a credenciales si hay error con cookies
                    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                        logger.debug("Fallback a credenciales de usuario y contraseña")
                        cmd = [item for item in cmd if item not in ["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}", INSTAGRAM_BROWSER]]
                        cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
            
            # Si no hay credenciales configuradas, advertir
            else:
                logger.warning("No se han configurado credenciales para Instagram. Es posible que la extracción falle.")
        
        logger.debug(f"Comando de extracción: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        
        if success:
            logger.info(f"Audio extraído exitosamente: {output_path}")
        else:
            logger.error(f"Error al extraer audio: {result.stderr}")
            logger.debug(f"Código de salida: {result.returncode}")
            logger.debug(f"Salida de error: {result.stderr}")
            
            # Intentar con método alternativo si falló
            if "instagram.com" in url and ("error has occurred" in result.stderr.lower() or "permission denied" in result.stderr.lower()):
                logger.info("Intentando método alternativo de extracción para Instagram")
                
                # Si falló con cookies del navegador, intentar con credenciales
                if "--cookies-from-browser" in ' '.join(cmd) and INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
                    logger.debug("Cambiando a autenticación por usuario/contraseña")
                    alt_cmd = [item for item in cmd if item not in ["--cookies-from-browser", f"{INSTAGRAM_BROWSER}:{INSTAGRAM_PROFILE}", INSTAGRAM_BROWSER]]
                    alt_cmd.extend(["--username", INSTAGRAM_USERNAME, "--password", INSTAGRAM_PASSWORD])
                    
                    logger.debug(f"Comando alternativo: {' '.join(alt_cmd)}")
                    alt_result = subprocess.run(alt_cmd, capture_output=True, text=True)
                    success = alt_result.returncode == 0
                    
                    if success:
                        logger.info(f"Audio extraído exitosamente con método alternativo: {output_path}")
                    else:
                        logger.error(f"Error al extraer audio con método alternativo: {alt_result.stderr}")
                
                # Si falló con credenciales o cookies del navegador, intentar sin autenticación
                elif not success:
                    logger.debug("Intentando extracción sin autenticación")
                    basic_cmd = [
                        "yt-dlp", 
                        url,
                        "--extract-audio",
                        "--audio-format", "mp3",
                        "--audio-quality", "0",
                        "--no-check-certificate",
                        "--user-agent", USER_AGENT,
                        "-o", f"{base_path}.%(ext)s"
                    ]
                    
                    logger.debug(f"Comando básico: {' '.join(basic_cmd)}")
                    basic_result = subprocess.run(basic_cmd, capture_output=True, text=True)
                    success = basic_result.returncode == 0
                    
                    if success:
                        logger.info(f"Audio extraído exitosamente sin autenticación: {output_path}")
                    else:
                        logger.error(f"Error al extraer audio sin autenticación: {basic_result.stderr}")
        
        return success 
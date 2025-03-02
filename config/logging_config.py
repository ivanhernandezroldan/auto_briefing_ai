import logging
import os
from datetime import datetime

# Niveles de logging disponibles
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Configuración por defecto (se puede sobrescribir con variables de entorno)
DEFAULT_LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Directorio para los archivos de log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name):
    """
    Configura y devuelve un logger con el nombre especificado
    
    Args:
        name: Nombre del logger (normalmente __name__)
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Obtener el nivel de log de la variable de entorno o usar el valor por defecto
    log_level = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()
    numeric_level = LOG_LEVELS.get(log_level, LOG_LEVELS[DEFAULT_LOG_LEVEL])
    
    # Crear el logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evitar duplicación de handlers
    if not logger.handlers:
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo
        log_file = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger 

# Añadir esta función para facilitar el diagnóstico
def log_api_error(logger, error):
    """
    Registra detalles específicos de errores de API
    """
    logger.error(f"Error de API: {type(error).__name__}")
    
    # Extraer información útil según el tipo de error
    if hasattr(error, 'status_code'):
        logger.error(f"Código de estado: {error.status_code}")
    
    if hasattr(error, 'response'):
        if hasattr(error.response, 'text'):
            # Truncar respuesta larga
            response_text = error.response.text
            if len(response_text) > 500:
                response_text = response_text[:500] + "... [truncado]"
            logger.error(f"Respuesta: {response_text}")
        
        if hasattr(error.response, 'status_code'):
            logger.error(f"Código de estado de respuesta: {error.response.status_code}")
    
    # Información adicional
    if hasattr(error, 'message'):
        logger.error(f"Mensaje: {error.message}")
    
    # Para errores de Google API
    if hasattr(error, 'details'):
        logger.error(f"Detalles: {error.details}")
    
    # Para errores de OpenAI
    if hasattr(error, 'code'):
        logger.error(f"Código de error: {error.code}")
    
    # Para errores de límite de tamaño
    error_str = str(error).lower()
    if 'too large' in error_str or 'size limit' in error_str:
        logger.error("Posible error de tamaño de archivo excedido")
    elif 'rate limit' in error_str or 'quota' in error_str:
        logger.error("Posible error de límite de tasa o cuota excedida")
    elif 'format' in error_str:
        logger.error("Posible error de formato no soportado")
    elif 'authentication' in error_str or 'auth' in error_str:
        logger.error("Posible error de autenticación")
    elif 'timeout' in error_str:
        logger.error("Posible error de tiempo de espera agotado")
    elif 'connection' in error_str:
        logger.error("Posible error de conexión") 
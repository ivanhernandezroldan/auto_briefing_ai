# Configuración general de la aplicación
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de captura de video
CAPTURE_INTERVAL = 3  # Intervalo en segundos entre capturas

# Configuración de rutas
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
DEFAULT_LINKS_FILE = "links.txt"

# Configuración de descarga
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Credenciales de Instagram
# Obtener credenciales desde variables de entorno
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")  # Tu nombre de usuario de Instagram
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")  # Tu contraseña de Instagram
# Alternativamente, puedes usar cookies de un navegador
# Opciones: "chrome", "firefox", "safari", "edge", "opera"
INSTAGRAM_BROWSER = os.getenv("INSTAGRAM_BROWSER", "chrome")  # Navegador del que obtener cookies
INSTAGRAM_PROFILE = os.getenv("INSTAGRAM_PROFILE", "")  # Perfil del navegador (dejar vacío para el perfil por defecto)

# Ruta a un archivo de cookies (alternativa si --cookies-from-browser no funciona)
# Puedes exportar cookies usando extensiones como "EditThisCookie" o "Cookie-Editor"
# Formato: archivo de texto con cookies en formato Netscape/Mozilla
INSTAGRAM_COOKIES_FILE = os.getenv("INSTAGRAM_COOKIES_FILE", "data/input/instagram_cookies.txt")  # Ruta relativa al archivo de cookies 
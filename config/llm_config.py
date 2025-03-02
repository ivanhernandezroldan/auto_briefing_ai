# Configuración para integración con LLMs
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

# Configuración de API
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Configuración de temperatura y otros parámetros
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 8192
LLM_TOP_P = 0.95
LLM_TOP_K = 40

# Configuración de prompts
VIDEO_ANALYSIS_PROMPT = """
Quiero inspirarme en el video adjuntado para crear un video para mi empresa "Barent Barefoot" que tiene el siguiente posicionamiento: ENTRENAMIENTO NATURAL PARA UN CUERPO FUERTE Y SALUDABLE

Para ello, analiza el video y piensa paso a paso como debe ser el video. Ten en cuenta que queremos que los videos se hagan virales y los 3 primeros segundos deben ser un gancho para que se queden viendo el resto del video (el usuario espera que el final del video cumpla con la expectativa que se ha creado con el principio del video).

IMPORTANTE: RESPONDE ÚNICAMENTE EN FORMATO JSON, SIN TEXTO ADICIONAL ANTES O DESPUÉS. El JSON debe tener exactamente esta estructura:

{
    "descripcion_original": "Descripción detallada del video original que estás analizando",
    "titulo_portada": "Título para la portada del video",
    "idea_video": "Idea principal del video",
    "gancho_video": "Descripción del gancho inicial (3 primeros segundos)",
    "acciones": ["Acción 1", "Acción 2", "..."],
    "dialogo": {
        "hay_dialogo": true/false,
        "dialogo": [["Hablante", "Texto"], ["Hablante", "Texto"], "..."]
    },
    "musica": {
        "hay_musica": true/false,
        "recomendacion": {
            "nombre_cancion": "Nombre de la canción",
            "artista": "Nombre del artista"
        }
    },
    "expectativas_cumplidas": "Explicación de cómo el final cumple las expectativas",
    "caption_video": "Texto para la descripción/caption del video",
    "hashtags": ["hashtag1", "hashtag2", "..."]
}

RECUERDA: 
1. NO INVENTES MUCHO, QUIERO QUE EL VIDEO SEA PRÁCTICAMENTE IGUAL. SOLO CAMBIA EL ENFOQUE PARA QUE SE ADAPTE AL MUNDO BAREFOOT PARA ENTRENAMIENTO.
2. LO QUE MAS ME IMPORTA ES QUE SE MANTENGA LA ESENCIA DEL VIDEO.
3. RESPONDE ÚNICAMENTE CON EL JSON, SIN NINGÚN TEXTO ADICIONAL.
"""
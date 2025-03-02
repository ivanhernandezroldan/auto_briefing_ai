# Generador de Contenido desde Videos

Este proyecto es una herramienta automatizada para analizar videos de redes sociales (TikTok, Instagram, etc.) y generar contenido estructurado a partir de ellos. El sistema descarga videos, extrae audio, captura fotogramas clave y utiliza modelos de IA generativa para analizar y crear contenido basado en estos videos.

## Características

- Descarga de videos desde plataformas como TikTok e Instagram
- Extracción de audio de los videos
- Captura de fotogramas clave
- Análisis de contenido mediante IA generativa (Gemini, OpenAI)
- Generación de resúmenes, transcripciones y análisis
- Exportación de resultados a Excel

## Requisitos

- Python 3.8+
- FFmpeg (para procesamiento de audio/video)
- API Key de Google Gemini o OpenAI

## Instalación

1. Clona este repositorio:
   ```
   git clone <url-del-repositorio>
   cd content-creation
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv .venv
   # En Windows
   .venv\Scripts\activate
   # En macOS/Linux
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   ```
   cp .env.example .env
   ```
   Edita el archivo `.env` y añade tus claves API.

## Uso

1. Coloca las URLs de los videos en el archivo `data/input/links.txt`, una URL por línea.

2. Ejecuta el programa:
   ```
   python main.py
   ```

3. Los resultados se guardarán en la carpeta `data/output/`, organizados por video.

## Estructura del Proyecto

```
content-creation/
├── app/                    # Código principal de la aplicación
│   ├── controllers/        # Controladores de la lógica de negocio
│   ├── services/           # Servicios para diferentes funcionalidades
│   └── models/             # Modelos de datos
├── config/                 # Configuración de la aplicación
├── data/                   # Datos de entrada y salida
│   ├── input/              # Archivos de entrada (links.txt)
│   └── output/             # Resultados generados
├── jobs/                   # Trabajos y procesos principales
├── logs/                   # Archivos de registro
├── .env.example            # Plantilla para variables de entorno
├── main.py                 # Punto de entrada principal
└── requirements.txt        # Dependencias del proyecto
```

## Dependencias Principales

- python-dotenv: Gestión de variables de entorno
- google-generativeai: API de Google Gemini
- langchain: Framework para aplicaciones de IA
- ffmpeg-python: Procesamiento de audio y video
- pandas/openpyxl: Manipulación y exportación de datos

## Configuración

El archivo `.env` permite configurar:
- Claves API para modelos de IA (Gemini, OpenAI)
- Selección del proveedor de IA a utilizar
- Modelo específico a utilizar para el análisis

## Licencia

[Especificar la licencia del proyecto]

## Contribuciones

[Instrucciones para contribuir al proyecto]
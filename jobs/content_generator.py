import os
import sys

# Añadir el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.controllers.content_controller import ContentController
from config.settings import INPUT_DIR, OUTPUT_DIR, DEFAULT_LINKS_FILE

def main():
    """
    Función principal que ejecuta el proceso de generación de contenido
    """
    # Definir rutas
    input_file = os.path.join(INPUT_DIR, DEFAULT_LINKS_FILE)
    
    # Verificar que el archivo de enlaces existe
    if not os.path.exists(input_file):
        print(f"Error: No se encuentra el archivo {input_file}")
        return
    
    # Crear el directorio de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print("=== Iniciando proceso de generación de contenido ===")
    print(f"Archivo de enlaces: {input_file}")
    print(f"Directorio de salida: {OUTPUT_DIR}")
    
    # Iniciar el controlador y procesar los enlaces
    controller = ContentController()
    controller.process_links_file(input_file, OUTPUT_DIR)
    
    print("\n=== Proceso de generación de contenido completado ===")

if __name__ == "__main__":
    main() 
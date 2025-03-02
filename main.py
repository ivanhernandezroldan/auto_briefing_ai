import os
import sys
from jobs.content_generator import main as generate_content

def main():
    """
    Punto de entrada principal de la aplicación
    """
    # Crear estructura de directorios si no existe
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    
    # Verificar que existe el archivo de enlaces
    if not os.path.exists("data/input/links.txt"):
        print("Creando archivo de enlaces de ejemplo...")
        with open("data/input/links.txt", "w") as f:
            f.write("# Añade URLs de videos aquí, una por línea\n")
            f.write("# Ejemplo: https://www.tiktok.com/@usuario/video/123456789\n")
    
    # Ejecutar el generador de contenido
    generate_content()

if __name__ == "__main__":
    main() 
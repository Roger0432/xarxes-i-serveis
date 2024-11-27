import os
import sys

# Agregar directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from part1.b64decoder import base64_decoder

def parse_headers(headers_section):
    headers = {}
    for line in headers_section.strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.strip()] = value.strip()
    return headers

def decode_mime_message():
    # Leer el archivo MIME
    with open("mimemail.txt", "r") as file:
        mime_content = file.read()

    # Separar encabezados y cuerpo
    headers_section, body_section = mime_content.split("\n\n", 1)

    # Extraer y guardar encabezados en `header.txt`
    headers = parse_headers(headers_section)
    
    # Crear el directorio `decoder` si no existe
    os.makedirs("decoder", exist_ok=True)
    
    with open("decoder/header.txt", "w") as header_file:
        for key, value in headers.items():
            header_file.write(f"{key}: {value}\n")

    # Identificar el límite (boundary) en el encabezado Content-Type
    content_type = headers.get("Content-Type", "")
    if "boundary=" not in content_type:
        raise ValueError("No se encontró el boundary en el encabezado Content-Type.")
    boundary = content_type.split("boundary=")[1].strip("\"")

    # Dividir el cuerpo en partes usando el límite
    parts = body_section.split(f"--{boundary}")

    # Procesar cada parte
    for part in parts:
        part = part.strip()
        if part == "--" or not part:  # Ignorar el cierre del boundary o partes vacías
            continue
        # Procesar cada parte (por ejemplo, guardar texto en body.txt, decodificar y guardar adjuntos)
        # ...

if __name__ == "__main__":
    decode_mime_message()
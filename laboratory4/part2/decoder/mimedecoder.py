import os
from part1.b64decoder import base64_decoder

def parse_headers(headers_section):
    headers = {}
    # Split the header section into lines and separate key:value pairs
    for line in headers_section.strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.strip()] = value.strip()
    # Return dictionary of headers
    return headers

def decode_mime_message():
    # Read the MIME file
    with open("mimemail.txt", "r") as file:
        mime_content = file.read()

    # Split header and body sections
    headers_section, body_section = mime_content.split("\n\n", 1)

    # Extract and save headers in header.txt
    headers = parse_headers(headers_section)
    with open("header.txt", "w") as header_file:
        for key, value in headers.items():
            header_file.write(f"{key}: {value}\n")

    # Identify boundary in the Content-Type header
    content_type = headers.get("Content-Type", "")
    boundary = None
    if "boundary=" in content_type:
        boundary = content_type.split("boundary=")[1].strip("\"")

    if not boundary:
        raise ValueError("No se encontró el boundary en el encabezado Content-Type.")

    # Split the body into parts using the boundary
    parts = body_section.split(f"--{boundary}")

    # Process each part: save text to body.txt, decode and save attachments
    for part in parts:
        part = part.strip()
        if part == "--" or not part:
            continue  # Ignorar la última parte vacía o el cierre del boundary

        # Separar encabezados y cuerpo de la parte
        part_headers_section, part_body = part.split("\n\n", 1)
        part_headers = parse_headers(part_headers_section)

        # Procesar contenido según el tipo
        content_disposition = part_headers.get("Content-Disposition", "")
        content_transfer_encoding = part_headers.get("Content-Transfer-Encoding", "")
        content_type = part_headers.get("Content-Type", "")

        if "attachment" in content_disposition:
            # Es un archivo adjunto
            filename = content_disposition.split("filename=")[1].strip("\"")
            if content_transfer_encoding == "base64":
                decoded_data = base64_decoder(part_body)
                with open(os.path.join("decoder", filename), "wb") as attachment_file:
                    attachment_file.write(decoded_data)
        elif "text" in content_type:
            # Es texto (por ejemplo, cuerpo del mensaje)
            with open("body.txt", "w", encoding="utf-8") as body_file:
                body_file.write(part_body)

if __name__ == "__main__":
    decode_mime_message()
    print("MIME message decodificada. Encabezados y partes guardadas.")

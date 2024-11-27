import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from part1.b64decoder import base64_decoder


def parse_headers(headers_section):
    headers = {}
    lines = headers_section.strip().split("\n")  # Split headers into lines
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)  # Split the line into key and value
            headers[key] = value  # Store in dictionary
    return headers


def decode_mime_message():
    # Open the MIME message file and read its contents
    with open('part2/decoder/mimemail.txt', 'r') as file:
        mime_message = file.read()

    # Split the MIME message into headers and body
    headers_section, body_section = mime_message.split("\n\n", 1)
    headers = parse_headers(headers_section)  # Parse the headers

    # Save the headers to a file
    with open('part2/decoder/header.txt', 'w') as header_file:
        for key, value in headers.items():
            header_file.write(f"{key}: {value}\n")

    # Extract the boundary from the Content-Type header
    content_type = headers.get("Content-Type", "")
    boundary = content_type.split("boundary=")[-1].strip('"')

    # Split the body into parts using the boundary
    parts = body_section.split(f"--{boundary}")

    for part in parts:
        if "--" in part:  # Skip the final boundary
            continue
        part = part.strip()  # Remove whitespace
        if not part:  # Skip empty parts
            continue

        # Split the part into headers and body
        part_headers, part_body = part.split("\n\n", 1)
        part_headers = parse_headers(part_headers)  # Parse part headers

        # Get filename and encoding from headers
        content_disposition = part_headers.get("Content-Disposition", "")
        content_transfer_encoding = part_headers.get("Content-Transfer-Encoding", "7bit")  # Default encoding
        filename = content_disposition.split('filename="')[-1].strip('"') if "filename=" in content_disposition else None

        # Decode the body if it's Base64 encoded
        if content_transfer_encoding == "base64":
            decoded_data = base64_decoder(part_body)  # Decode Base64 data
            if filename:  # Save as a file if there's a filename
                with open(f"part2/decoder/{filename}", "wb") as file:
                    file.write(decoded_data)
            else:  # Save as the message body if no filename
                with open("part2/decoder/body.txt", "w") as file:
                    file.write(decoded_data.decode("utf-8"))
        else:
            # Save as plain text if not Base64
            if filename:  # Save as a file if there's a filename
                with open(f"part2/decoder/{filename}", "w") as file:
                    file.write(part_body)
            else:  # Save as the message body
                with open("part2/decoder/body.txt", "w") as file:
                    file.write(part_body)

    print("MIME message decoded successfully.")  # Indicate successful decoding


if __name__ == "__main__":
    decode_mime_message()  # Execute the decoding function

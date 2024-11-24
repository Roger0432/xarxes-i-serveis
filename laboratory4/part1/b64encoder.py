# b64encoder.py
def base64_encoder(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    encoded_str = ""

    # Calculate padding based on data length
    padding = (3 - len(data) % 3) % 3
    binary_str = "".join(f"{byte:08b}" for byte in data)

    # Encode
    for i in range(0, len(binary_str), 6):
        chunk = binary_str[i:i+6]
        if len(chunk) < 6: 
            chunk += "0" * (6 - len(chunk))
        encoded_str += base64_chars[int(chunk, 2)]

    # Add padding ('=') if necessary
    encoded_str += "=" * padding

    # Return the Base64 encoded string
    return encoded_str


if __name__ == "__main__":
    input_file = "part1/decoded_image.jpg"
    with open(input_file, "rb") as file:
        file_data = file.read()

    encoded_data = base64_encoder(file_data)

    with open("part1/enncoded_image.txt", "w") as output_file:
        output_file.write(encoded_data)

    print(f"Archivo codificado en Base64 y guardado en 'image.txt'.")

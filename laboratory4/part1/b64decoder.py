# b64decoder.py
def base64_decoder(encoded_str):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    decoded_bytes = bytearray()

    # Clean the encoded string (remove spaces and newline characters)
    # Remove padding and adjust the length if needed
    encoded_str = encoded_str.replace(" ", "").replace("\n", "")
    padding = encoded_str.count('=')
    encoded_str = encoded_str.rstrip('=')

    # Decode
    binary_str = ""
    for char in encoded_str:
        if char in base64_chars:
            binary_str += f"{base64_chars.index(char):06b}"
        else:
            raise ValueError(f"Carácter inválido en Base64: {char}")

    # Return decoded bytes
    for i in range(0, len(binary_str) - padding * 6, 8):
        byte = binary_str[i:i+8]
        decoded_bytes.append(int(byte, 2))

    return decoded_bytes


if __name__ == "__main__":
    with open("part1/image.txt", "r") as file:
        encoded_image = file.read()

    decoded_image = base64_decoder(encoded_image)

    with open("part1/decoded_image.jpg", "wb") as output_file:
        output_file.write(decoded_image)

    print("Image decoded and saved")
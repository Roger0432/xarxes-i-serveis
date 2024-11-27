# b64decoder.py

def base64_decoder(encoded_str):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    decoded_bytes = bytearray()  # Store the decoded bytes

    # Clean the encoded string (remove spaces and newline characters)
    encoded_str = encoded_str.replace(" ", "").replace("\n", "")
    padding = encoded_str.count('=')  # Count padding characters
    encoded_str = encoded_str.rstrip('=')  # Remove padding characters from the end

    # Decode Base64 characters to binary string
    binary_str = ""
    for char in encoded_str:
        if char in base64_chars:  # Check if character is valid Base64
            binary_str += f"{base64_chars.index(char):06b}"  # Convert Base64 to 6-bit binary
        else:
            raise ValueError(f"Invalid character in Base64: {char}")  # Raise error for invalid characters

    # Convert binary string to bytes
    for i in range(0, len(binary_str) - padding * 6, 8):  # Process 8 bits at a time
        byte = binary_str[i:i+8]  # Extract 8-bit chunk
        decoded_bytes.append(int(byte, 2))  # Convert binary to integer and append to byte array

    return decoded_bytes  # Return decoded bytes


if __name__ == "__main__":
    # Open the file containing the Base64-encoded image
    with open("part1/image.txt", "r") as file:
        encoded_image = file.read()

    # Decode the image from Base64
    decoded_image = base64_decoder(encoded_image)

    # Save the decoded image as a binary file
    with open("part1/decoded_image.jpg", "wb") as output_file:
        output_file.write(decoded_image)

    print("Image decoded and saved")  # Notify that the image was decoded and saved

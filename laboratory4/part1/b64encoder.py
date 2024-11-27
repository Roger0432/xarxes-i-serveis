# b64encoder.py

def base64_encoder(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    encoded_str = ""  # Store the encoded Base64 string

    # Calculate padding based on the length of the input data
    padding = (3 - len(data) % 3) % 3  # Padding needed to make length a multiple of 3
    binary_str = "".join(f"{byte:08b}" for byte in data)  # Convert data to a binary string

    # Encode the binary string to Base64
    for i in range(0, len(binary_str), 6):  # Process 6 bits at a time
        chunk = binary_str[i:i+6]  # Extract 6-bit chunk
        if len(chunk) < 6:  # Pad with zeros if the chunk is less than 6 bits
            chunk += "0" * (6 - len(chunk))
        encoded_str += base64_chars[int(chunk, 2)]  # Convert binary to Base64 character

    # Add padding characters ('=') to make the length a multiple of 4
    encoded_str += "=" * padding

    # Return the Base64 encoded string
    return encoded_str


if __name__ == "__main__":
    input_file = "part1/decoded_image.jpg"  # Input file to encode
    with open(input_file, "rb") as file:
        file_data = file.read()  # Read the file in binary mode

    # Encode the file data to Base64
    encoded_data = base64_encoder(file_data)

    # Save the encoded data to a text file
    with open("part1/encoded_image.txt", "w") as output_file:
        output_file.write(encoded_data)

    print(f"File encoded in Base64 and saved in 'encoded_image.txt'.")  # Notify that the file was encoded and saved

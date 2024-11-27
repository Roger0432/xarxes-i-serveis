import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from part1.b64encoder import base64_encoder

import random
import string
import quopri

# Function to generate a random boundary string
def generate_boundary(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to build the MIME message with headers, body, and attachments
def build_mime_message(from_addr, to_addr, cc_addr, subject, body_text, attachments):
    # Generate boundary for separating the parts of the message
    boundary = generate_boundary()

    # MIME headers
    headers = [
        f"From: {from_addr}",
        f"To: {to_addr}",
        f"CC: {cc_addr}",
        f"Subject: {subject}",
        "MIME-Version: 1.0",
        f"Content-Type: multipart/mixed; boundary=\"{boundary}\""
    ]

    # Prepare the MIME message
    mime_message = "\n".join(headers) + "\n\n"

    # Add the body section
    mime_message += f"--{boundary}\n"
    mime_message += 'Content-Type: text/plain; charset="UTF-8"\n'
    mime_message += "Content-Transfer-Encoding: quoted-printable\n\n"
    
    # Encode the body text using quoted-printable
    quoted_body = quopri.encodestring(body_text.encode('utf-8')).decode('utf-8')
    mime_message += quoted_body + "\n\n"

    # Add the attachments
    for filename in attachments:
        filepath = os.path.join("part2/encoder/attachments", filename)
        with open(filepath, "rb") as file:
            file_data = file.read()

        # Encode the file content to Base64
        encoded_data = base64_encoder(file_data)

        # Prepare the attachment headers and content
        mime_message += f"--{boundary}\n"
        mime_message += f"Content-Type: application/octet-stream; name=\"{filename}\"\n"
        mime_message += f"Content-Disposition: attachment; filename=\"{filename}\"\n"
        mime_message += "Content-Transfer-Encoding: base64\n\n"

        # Add the encoded data (split into lines of 76 characters)
        for i in range(0, len(encoded_data), 76):
            mime_message += encoded_data[i:i+76] + "\n"
        mime_message += "\n"

    # End the MIME message with the final boundary
    mime_message += f"--{boundary}--\n"

    return mime_message

def main():
    # Read the body of the email from body.txt
    with open("part2/encoder/body.txt", "r") as body_file:
        body_text = body_file.read()

    # List the files in the attachments folder
    attachments = [f for f in os.listdir("part2/encoder/attachments") if os.path.isfile(os.path.join("part2/encoder/attachments", f))]

    # Set the message details
    from_addr = "sender@gmail.com"
    to_addr = "receiver@gmail.com"
    cc_addr = "examplecc@gmail.com"
    subject = "MIME encoded email"

    # Build the MIME message
    mime_message = build_mime_message(from_addr, to_addr, cc_addr, subject, body_text, attachments)

    # Write the MIME message to mimemail.txt
    with open("part2/encoder/mimemail.txt", "w") as mime_file:
        mime_file.write(mime_message)

    print("MIME message encoded and saved in 'mimemail.txt'.")

if __name__ == "__main__":
    main()

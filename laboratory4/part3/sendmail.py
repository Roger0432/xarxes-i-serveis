# sendmail.py
import smtplib
from email import message_from_file
import os

def send_email():
    # SMTP server configuration and credentials
    smtp_server = "smtp.smtp2go.com"
    smtp_port = 2525
    smtp_user = "tecnocampus"
    smtp_password = "Fx5eff49VgoynPtj"

    # Path to the MIME file to be sent
    mime_file_path = "part2/encoder/mimemail.txt"

    try:
        # Check if the MIME file exists
        if not os.path.exists(mime_file_path):
            print(f"Error: File {mime_file_path} not found.")
            return

        # Read the MIME file and load it as a message
        with open(mime_file_path, "r") as mime_file:
            mime_message = message_from_file(mime_file)

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Establish a secure connection using TLS
            server.login(smtp_user, smtp_password)  # Log in with credentials
            server.send_message(mime_message)  # Send the MIME message
            print("Email sent successfully.")

    except Exception as e:
        # Print an error message if something goes wrong
        print(f"Error sending the email: {e}")

# Execute the function to send the email
if __name__ == "__main__":
    send_email()

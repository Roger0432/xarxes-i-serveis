import socket
import struct
import argparse
import os

# TFTP protocol configuration
BUFFER_SIZE = 516  # Block size (512 bytes) + header (4 bytes)
TIMEOUT = 1  # Timeout in seconds

# TFTP opcodes (protocol operations)
RRQ = 1     # Read Request
WRQ = 2     # Write Request
DATA = 3    # Data Packet
ACK = 4     # Acknowledgment
ERROR = 5   # Error Packet

def send_rrq(sock, server_address, filename):
    # Sends a read request (RRQ) to the server with the filename in "octet" mode
    packet = struct.pack("!H", RRQ) + filename.encode() + b'\0' + b'octet\0'
    sock.sendto(packet, server_address)
    print(f"Starting TFTP transfer to IP={server_address[0]} and PORT={server_address[1]} to get FILE={filename}")

def send_wrq(sock, server_address, filename):
    # Sends a write request (WRQ) to the server with the filename in "octet" mode
    packet = struct.pack("!H", WRQ) + filename.encode() + b'\0' + b'octet\0'
    sock.sendto(packet, server_address)
    print(f"Starting TFTP transfer to IP={server_address[0]} and PORT={server_address[1]} to put FILE={filename}")

def send_ack(sock, server_address, block_number):
    # Sends an acknowledgment (ACK) packet to the server to confirm receipt of a data block
    packet = struct.pack("!HH", ACK, block_number)
    sock.sendto(packet, server_address)

def send_data(sock, server_address, block_number, data):
    # Sends a data packet (DATA) with the block number and file content
    packet = struct.pack("!HH", DATA, block_number) + data
    sock.sendto(packet, server_address)

def receive_file(sock, server_address, filename):
    # Function to receive a file from the server and save it locally
    with open(filename, 'wb') as file:  # Opens the file in binary write mode
        block_number = 1  # Initializes the expected block number
        while True:
            try:
                sock.settimeout(TIMEOUT)  # Sets the timeout
                data, address = sock.recvfrom(BUFFER_SIZE)  # Receives data from the server
                
                opcode = struct.unpack("!H", data[:2])[0]  # Extracts the opcode from the packet
                if opcode == DATA:  # If the packet is a data packet
                    received_block = struct.unpack("!H", data[2:4])[0]
                    if received_block == block_number:  # Verifies that the block is as expected
                        print(f"Received block #{block_number}")
                        file.write(data[4:])  # Writes the block content to the file
                        print("Write data to file")
                        send_ack(sock, server_address, block_number)  # Sends ACK for the block
                        block_number += 1
                    if len(data) < BUFFER_SIZE:  # If the block is smaller than the max size, it's the last block
                        print("Finished!")
                        break
                elif opcode == ERROR:  # Handles error messages
                    print("Server error:", data[4:].decode())
                    break
            except socket.timeout:  # Handles timeouts
                print("Timeout exceeded.")
                break

def send_file(sock, server_address, filename):
    # Function to send a file to the server in 512-byte blocks
    if not os.path.isfile(filename):  # Checks if the file exists
        print("File not found.")
        return
    
    with open(filename, 'rb') as file:  # Opens the file in binary read mode
        block_number = 1  # Initializes the block number to send
        while True:
            data = file.read(512)  # Reads a 512-byte block
            print(f"Write data to file: Sending block #{block_number}")
            send_data(sock, server_address, block_number, data)  # Sends the block to the server
            
            try:
                sock.settimeout(TIMEOUT)  # Sets the timeout
                ack, address = sock.recvfrom(4)  # Waits for ACK from the server
                opcode = struct.unpack("!H", ack[:2])[0]
                if opcode == ACK:  # If an ACK is received
                    received_block = struct.unpack("!H", ack[2:4])[0]
                    if received_block == block_number:  # Confirms the ACK is for the correct block
                        print(f"Received ACK for block #{block_number}")
                        block_number += 1
                    if len(data) < 512:  # If the block is smaller than 512 bytes, it's the last block
                        print("Finished!")
                        break
                elif opcode == ERROR:  # Handles error messages
                    print("Server error:", ack[4:].decode())
                    break
            except socket.timeout:  # Handles timeouts
                print("Timeout exceeded.")
                break

def main():
    # Program argument configuration
    parser = argparse.ArgumentParser(description="TFTP Client")
    parser.add_argument("-m", choices=["rx", "tx"], required=True, help="Operation mode: rx to read, tx to write")
    parser.add_argument("filename", help="Filename")
    parser.add_argument("-p", type=int, default=6969, help="TFTP server port")
    parser.add_argument("--server", default="127.0.0.1", help="TFTP server address")
    args = parser.parse_args()

    server_address = (args.server, args.p)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creates a UDP socket

    # Executes the selected operation mode
    if args.m == "rx":
        send_rrq(sock, server_address, args.filename)  # Requests file read
        receive_file(sock, server_address, args.filename)  # Receives the file
    elif args.m == "tx":
        send_wrq(sock, server_address, args.filename)  # Requests file write
        send_file(sock, server_address, args.filename)  # Sends the file

    sock.close()  # Closes the socket

if __name__ == "__main__":
    main()

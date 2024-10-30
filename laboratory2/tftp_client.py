import socket
import struct
import argparse

def send_rrq(sock, filename, mode, server_address):
    # Create RRQ packet
    rrq_packet = struct.pack("!H", 1) + filename.encode() + b'\0' + mode.encode() + b'\0'
    sock.sendto(rrq_packet, server_address)
    print(f"Starting TFTP transfer to IP={server_address[0]} and PORT={server_address[1]} to get FILE={filename}")

def receive_data(sock, file):
    block_number = 1
    while True:
        try:
            data, server = sock.recvfrom(516)  # Receive data (516 bytes: 512 data + 4 header)
            opcode = struct.unpack("!H", data[:2])[0]
            if opcode == 3:  # DATA opcode
                received_block_number = struct.unpack("!H", data[2:4])[0]
                if received_block_number == block_number:
                    print(f"Received block #{block_number}")
                    file.write(data[4:])  # Write data to file
                    # Send ACK
                    ack_packet = struct.pack("!HH", 4, block_number)
                    sock.sendto(ack_packet, server)
                    block_number += 1
                    if len(data) < 516:  # End of transfer when data packet is less than 512 bytes
                        print("Finished!")
                        break
        except socket.timeout:
            print("Timeout: No response received")
            break

def main():
    parser = argparse.ArgumentParser(description="Python TFTP Client")
    parser.add_argument('-m', type=str, required=True, help="Transfer mode (use 'rx' for receive)")
    parser.add_argument('-p', type=int, required=True, help="TFTP server port")
    parser.add_argument('filename', type=str, help="Name of the file to transfer")
    args = parser.parse_args()

    server_address = ("127.0.0.1", args.p)

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    try:
        if args.m == 'rx':
            send_rrq(sock, args.filename, 'octet', server_address)
            with open(args.filename, 'wb') as file:
                receive_data(sock, file)
        else:
            print("Unsupported mode.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()

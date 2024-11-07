import socket
import struct
import argparse

def send_rrq(sock, filename, mode, server_address):
    # Crear paquete RRQ
    rrq_packet = struct.pack("!H", 1) + bytes(filename, 'utf-8') + b'\0' + bytes(mode, 'utf-8') + b'\0'
    sock.sendto(rrq_packet, server_address)
    print(f"Starting TFTP transfer to IP={server_address[0]} and PORT={server_address[1]} to get FILE={filename}")

def receive_data(sock, filename):
    block_number = 1
    with open(filename, 'wb') as file:  # Abrir archivo en modo de escritura binaria
        while True:
            try:
                data, server = sock.recvfrom(516)  # Recibir datos (516 bytes: 512 de datos + 4 de cabecera)
                opcode = struct.unpack("!H", data[:2])[0]
                
                if opcode == 3:  # DATA opcode
                    received_block_number = struct.unpack("!H", data[2:4])[0]
                    if received_block_number == block_number:
                        print(f"Received block #{block_number}")
                        file.write(data[4:])  # Escribir datos en el archivo
                        print("Write data to file")
                        
                        # Enviar ACK solo después de confirmar que el bloque es el esperado
                        ack_packet = struct.pack("!HH", 4, block_number)
                        sock.sendto(ack_packet, server)
                        block_number += 1
                        
                        # Verificar si este es el último paquete (paquete de datos < 512 bytes)
                        if len(data[4:]) < 512:  
                            print("Finished!")
                            break
                    else:
                        # Reenviar ACK del último bloque en caso de recibir un bloque duplicado
                        ack_packet = struct.pack("!HH", 4, received_block_number)
                        sock.sendto(ack_packet, server)
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

    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    try:
        if args.m == 'rx':
            send_rrq(sock, args.filename, 'octet', server_address)
            receive_data(sock, args.filename)
        else:
            print("Unsupported mode.")
    finally:
        sock.close()



if __name__ == "__main__":
    main()

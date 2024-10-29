import socket
import struct
import argparse
import os
import sys

# Opcodes para el protocolo TFTP
OPCODE_RRQ = 1  # Read request
OPCODE_WRQ = 2  # Write request
OPCODE_DATA = 3
OPCODE_ACK = 4
OPCODE_ERROR = 5
BLOCK_SIZE = 512  # Tamaño máximo de datos por paquete

def create_request_packet(opcode, filename, mode='octet'):
    """Crea un paquete de solicitud de lectura o escritura."""
    return struct.pack(f'!H{len(filename) + 1}s{len(mode) + 1}s', opcode, filename.encode(), mode.encode())

def create_data_packet(block_num, data):
    """Crea un paquete de datos."""
    return struct.pack(f'!HH{len(data)}s', OPCODE_DATA, block_num, data)

def create_ack_packet(block_num):
    """Crea un paquete de confirmación (ACK)."""
    return struct.pack('!HH', OPCODE_ACK, block_num)

def create_error_packet(error_code, error_msg):
    """Crea un paquete de error."""
    return struct.pack(f'!HH{len(error_msg) + 1}s', OPCODE_ERROR, error_code, error_msg.encode())

def send_file(filename, server_address):
    """Función para escribir (subir) un archivo al servidor TFTP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)  # Tiempo de espera de 1 segundo

        # Crear y enviar WRQ (Write Request)
        wrq_packet = create_request_packet(OPCODE_WRQ, filename)
        sock.sendto(wrq_packet, server_address)
        
        with open(filename, 'rb') as file:
            block_num = 1
            while True:
                # Leer datos en bloques de 512 bytes
                data = file.read(BLOCK_SIZE)
                data_packet = create_data_packet(block_num, data)
                sock.sendto(data_packet, server_address)

                # Esperar el ACK
                ack_packet, _ = sock.recvfrom(4)
                _, ack_block = struct.unpack('!HH', ack_packet)
                
                if ack_block != block_num:
                    print(f"Error: ACK no coincide para el bloque {block_num}.")
                    return

                block_num += 1
                if len(data) < BLOCK_SIZE:
                    print("Archivo enviado exitosamente.")
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def receive_file(filename, server_address):
    """Función para leer (descargar) un archivo desde el servidor TFTP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)  # Tiempo de espera de 1 segundo

        # Crear y enviar RRQ (Read Request)
        rrq_packet = create_request_packet(OPCODE_RRQ, filename)
        sock.sendto(rrq_packet, server_address)
        
        with open(filename, 'wb') as file:
            block_num = 1
            while True:
                # Recibir paquete de datos
                data_packet, _ = sock.recvfrom(BLOCK_SIZE + 4)
                opcode, received_block, data = struct.unpack(f'!HH{len(data_packet) - 4}s', data_packet)

                if opcode != OPCODE_DATA or received_block != block_num:
                    print(f"Error: Paquete de datos no coincide para el bloque {block_num}.")
                    return
                
                # Escribir datos en el archivo
                file.write(data)

                # Enviar ACK
                ack_packet = create_ack_packet(block_num)
                sock.sendto(ack_packet, server_address)
                
                block_num += 1
                if len(data) < BLOCK_SIZE:
                    print("Archivo recibido exitosamente.")
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(description="Cliente TFTP para leer/escribir archivos.")
    parser.add_argument('operation', choices=['read', 'write'], help="Operación a realizar: 'read' o 'write'")
    parser.add_argument('filename', help="Nombre del archivo")
    parser.add_argument('--server', default='127.0.0.1', help="Dirección del servidor TFTP (por defecto: localhost)")
    parser.add_argument('--port', type=int, default=6969, help="Puerto del servidor TFTP (por defecto: 6969)")
    args = parser.parse_args()

    server_address = (args.server, args.port)

    if args.operation == 'read':
        receive_file(args.filename, server_address)
    elif args.operation == 'write':
        send_file(args.filename, server_address)

if __name__ == "__main__":
    main()

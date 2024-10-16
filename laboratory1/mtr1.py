import socket
import struct
import os
import sys
import time

def resolve_target(target):
    """Resolves a domain or IP address into an IP address."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Unable to resolve domain: {target}")
        sys.exit(1)


def checksum(source_string):
    """Calculates the checksum for the ICMP packet."""
    sum = 0
    max_count = (len(source_string) // 2) * 2
    count = 0
    while count < max_count:
        val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + val
        sum = sum & 0xffffffff  # Keep sum within 32 bits
        count += 2

    if max_count < len(source_string):
        # Add the last byte if the total length is odd
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    # Fold the sum to 16 bits and invert it to get the checksum
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def create_icmp_packet(identifier, sequence_number):
    """Creates an ICMP Echo Request packet (Type 8, Code 0)"""
    icmp_type = 8  # Echo request type
    icmp_code = 0  # Echo request code
    icmp_checksum = 0  # Placeholder for checksum
    header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, identifier, sequence_number)
    data = struct.pack("d", time.time())  # Add a timestamp to the packet data
    # Calculate the checksum for the ICMP header and data
    icmp_checksum = checksum(header + data)
    # Repack the header with the correct checksum
    header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, identifier, sequence_number)
    return header + data  # Return the full ICMP packet (header + data)


def create_socket():
    """Creates a raw socket for sending ICMP packets."""
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        return icmp_socket
    except PermissionError as e:
        print(f"Error: {e}. You need administrator/root privileges to create a raw socket.")
        sys.exit(1)


def send_icmp_packet(icmp_socket, target_ip, packet, ttl):
    """Sends the ICMP packet with the specified TTL (Time-to-Live)."""
    icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)  # Set the TTL for the packet
    icmp_socket.sendto(packet, (target_ip, 1))  # Send the packet to the target IP


def main():
    """Main function that sends ICMP packets to trace the route to the target."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <domain_or_IP>")
        sys.exit(1)

    target = sys.argv[1]
    target_ip = resolve_target(target)

    print(f"Resolving {target}: {target_ip}")

    # Create a raw socket for sending ICMP packets
    icmp_socket = create_socket()

    identifier = os.getpid() & 0xFFFF  # Use the process ID as the ICMP identifier
    sequence_number = 1  # Initial ICMP sequence number

    # Loop to send ICMP packets with increasing TTL values from 1 to 20
    for ttl in range(1, 21):
        icmp_packet = create_icmp_packet(identifier, sequence_number)
        send_icmp_packet(icmp_socket, target_ip, icmp_packet, ttl)
        print(f"ICMP packet sent with TTL={ttl} to {target_ip}")
        sequence_number += 1  # Increment sequence number for each packet
        time.sleep(1)  # Wait 1 second before sending the next packet

if __name__ == "__main__":
    main()

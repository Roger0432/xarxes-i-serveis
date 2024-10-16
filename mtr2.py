import socket
import struct
import time
import os
import sys

# Resolve the target domain name to an IP address
def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Error resolving target: {target}")
        sys.exit(1)

# Compute checksum for the ICMP packet
def checksum(source_string):
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff  # Keep it within 32 bits
        count += 2

    if count_to < len(source_string):
        sum = sum + source_string[-1]
        sum = sum & 0xffffffff  # Keep it within 32 bits

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    return ~sum & 0xffff


# Create ICMP Echo Request packet
def create_icmp_packet(identifier, sequence_number):
    header = struct.pack('bbHHh', 8, 0, 0, identifier, sequence_number)
    data = struct.pack('d', time.time())
    my_checksum = checksum(header + data)
    
    # Repack header with correct checksum
    header = struct.pack('bbHHh', 8, 0, my_checksum, identifier, sequence_number)
    return header + data

# Create raw socket for ICMP communication
def create_socket():
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.settimeout(2)
        return icmp_socket
    except PermissionError:
        print("Error: You need to run this script as root/administrator to create a raw socket.")
        sys.exit(1)
    except socket.error as e:
        print(f"Socket error: {e}")
        sys.exit(1)

# Send ICMP Echo Request with specified TTL
def send_icmp_packet(icmp_socket, target_ip, packet, ttl):
    icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    icmp_socket.sendto(packet, (target_ip, 1))

# Resolve IP to hostname if possible
def resolve_ip_to_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = ip
    return hostname

# Receive ICMP Echo Reply or Time Exceeded message
def receive_icmp_reply(icmp_socket, target_ip, ttl, send_time):
    try:
        addr = icmp_socket.recvfrom(1024)
        recv_time = time.time()
        rtt = (recv_time - send_time) * 1000  # RTT in milliseconds

        if addr[0] == target_ip:
            return rtt, addr[0], True  # Success
        else:
            return rtt, addr[0], False  # ICMP response from an intermediate hop
    except socket.timeout:
        return None, None, None  # Timeout

# Main function to send ICMP packets and display trace results
def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target>")
        sys.exit(1)

    target = sys.argv[1]
    
    # Validate the target
    if not target:
        print("Error: Target cannot be empty.")
        sys.exit(1)

    target_ip = resolve_target(target)
    print(f"Target {target} resolved to {target_ip}")

    icmp_socket = create_socket()
    identifier = os.getpid() & 0xFFFF
    max_hops = 30
    sequence_number = 1

    for ttl in range(1, max_hops + 1):
        packet = create_icmp_packet(identifier, sequence_number)
        send_time = time.time()
        send_icmp_packet(icmp_socket, target_ip, packet, ttl)

        rtt, hop_ip, reached = receive_icmp_reply(icmp_socket, target_ip, ttl, send_time)
        if rtt is not None:
            hop_hostname = resolve_ip_to_hostname(hop_ip)
            print(f"{ttl}\t{hop_hostname} ({hop_ip})\t{rtt:.2f} ms")
            if reached:
                print("Reached destination")
                break
        else:
            print(f"{ttl}\tRequest timed out.")

        sequence_number += 1

if __name__ == "__main__":
    main()

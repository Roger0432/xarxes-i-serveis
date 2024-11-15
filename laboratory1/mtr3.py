import socket
import struct
import time
import os
import sys
import statistics

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

    # Repack header with the correct checksum
    header = struct.pack('bbHHh', 8, 0, my_checksum, identifier, sequence_number)
    return header + data

# Create raw socket for ICMP communication
def create_socket():
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.settimeout(2)
        return icmp_socket
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

# Receive ICMP Echo Reply or Time Exceeded message and calculate statistics
def receive_icmp_reply(icmp_socket, target_ip, ttl, send_time, timings_per_host):
    try:
        packet, addr = icmp_socket.recvfrom(1024)
        recv_time = time.time()
        rtt = (recv_time - send_time) * 1000  # RTT in milliseconds

        if addr[0] not in timings_per_host:
            timings_per_host[addr[0]] = []
        timings_per_host[addr[0]].append(rtt)

        if addr[0] == target_ip:
            return rtt, addr[0], True  # Success
        else:
            return rtt, addr[0], False  # ICMP response from an intermediate hop
    except socket.timeout:
        return None, None, None  # Timeout

# Calculate statistics for RTTs
def calculate_statistics(rtts):
    if rtts:
        return min(rtts), max(rtts), sum(rtts) / len(rtts), statistics.stdev(rtts) if len(rtts) > 1 else 0
    else:
        return None, None, None, None

# Print the table header
def print_table_header():
    print(f"{'TTL':<4}{'Host':<50}{'Last (ms)':<12}{'Min (ms)':<12}{'Avg (ms)':<12}{'Max (ms)':<12}{'StDev (ms)':<12}")
    print('-' * 110)

# Main function to send ICMP packets, calculate stats, and display results
def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target>")
        sys.exit(1)

    target = sys.argv[1]
    target_ip = resolve_target(target)

    icmp_socket = create_socket()
    identifier = os.getpid() & 0xFFFF
    max_hops = 30
    sequence_number = 1
    timings_per_host = {}  # Dictionary to store RTTs per hop
    row_count = 0  # To track the number of rows for reprinting the header

    print_table_header()

    for ttl in range(1, max_hops + 1):
        packet = create_icmp_packet(identifier, sequence_number)
        send_time = time.time()
        send_icmp_packet(icmp_socket, target_ip, packet, ttl)

        rtt, hop_ip, reached = receive_icmp_reply(icmp_socket, target_ip, ttl, send_time, timings_per_host)

        if rtt is not None:
            hop_hostname = resolve_ip_to_hostname(hop_ip)
            hop_hostname = hop_hostname[:47] + '...' if len(hop_hostname) > 47 else hop_hostname  # Truncate long hostnames
            min_rtt, max_rtt, avg_rtt, stddev_rtt = calculate_statistics(timings_per_host[hop_ip])

            print(f"{ttl:<4}{hop_hostname:<50}{rtt:<12.2f}{min_rtt:<12.2f}{avg_rtt:<12.2f}{max_rtt:<12.2f}{stddev_rtt:<12.2f}")

            row_count += 1
            if row_count == 15:
                print('-' * 110)
                print_table_header()
                row_count = 0

            if reached:
                print("Reached destination")
                break
        else:
            print(f"{ttl:<4}{'Request timed out.':<50}")
        sequence_number += 1

if __name__ == "__main__":
    main()

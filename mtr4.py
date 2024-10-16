import socket
import struct
import time
import os
import sys
import signal
import statistics
import curses

ICMP_ECHO_REQUEST = 8
ICMP_CODE = socket.getprotobyname('icmp')

# Function to resolve the target domain to an IP address
def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        print("Error: Unknown host.")
        sys.exit(1)

# Function to calculate checksum for ICMP packets
def checksum(source_string):
    csum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        csum += this_val
        csum &= 0xffffffff
        count += 2

    if count_to < len(source_string):
        csum += source_string[len(source_string) - 1]
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum += (csum >> 16)
    answer = ~csum
    answer &= 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# Create an ICMP packet with identifier and sequence number
def create_icmp_packet(identifier, sequence_number):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, identifier, sequence_number)
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), identifier, sequence_number)
    return header + data

# Create a raw socket for ICMP
def create_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
        return sock
    except PermissionError:
        print("Error: You need root privileges to use raw sockets.")
        sys.exit(1)

# Send ICMP packet with TTL
def send_icmp_packet(icmp_socket, target_ip, packet, ttl):
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
    icmp_socket.sendto(packet, (target_ip, 1))

# Resolve IP to hostname
def resolve_ip_to_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return ip

# Receive ICMP reply and process timings and packet loss
def receive_icmp_reply(icmp_socket, target_ip, ttl, send_time, timings_per_host, loss_per_ttl):
    try:
        icmp_socket.settimeout(2)
        recv_packet, addr = icmp_socket.recvfrom(1024)
        receive_time = time.time()

        icmp_header = recv_packet[20:28]

        type = struct.unpack("bbHHh", icmp_header)

        if type == 11 or type == 0:
            ip = addr[0]
            hostname = resolve_ip_to_hostname(ip)
            round_trip_time = (receive_time - send_time) * 1000  # Convert to ms
            timings_per_host[ttl].append(round_trip_time)
            loss_per_ttl[ttl]['received'] += 1
            return ttl, hostname, round_trip_time
    except socket.timeout:
        loss_per_ttl[ttl]['loss'] += 1
        return ttl, None, None

# Format numerical values for display
def format_value(value):
    if value is None:
        return "*"
    return f"{value:.2f} ms"

# Main function to manage curses interface and run the traceroute
def main(stdscr):
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target>")
        sys.exit(1)

    target = sys.argv[1]
    target_ip = resolve_target(target)
    max_hops = 100
    packet_count = 3
    timings_per_host = {ttl: [] for ttl in range(1, max_hops + 1)}
    loss_per_ttl = {ttl: {'sent': packet_count, 'received': 0, 'loss': 0} for ttl in range(1, max_hops + 1)}

    icmp_socket = create_socket()
    stdscr.clear()

    # Display header row of the table
    stdscr.addstr(0, 0, f"{'TTL':<5}{'Host':<50}{'Last(ms)':<15}{'Min(ms)':<15}{'Avg(ms)':<15}{'Max(ms)':<15}{'StDev(ms)':<15}{'Loss %':<15}")
    stdscr.addstr(1, 0, "-"*135)
    
    # Start traceroute process
    for ttl in range(1, max_hops + 1):
        for sequence in range(packet_count):
            packet = create_icmp_packet(os.getpid() & 0xFFFF, sequence)
            send_time = time.time()
            send_icmp_packet(icmp_socket, target_ip, packet, ttl)
            stdscr.refresh()
            ttl, hostname, round_trip_time = receive_icmp_reply(icmp_socket, target_ip, ttl, send_time, timings_per_host, loss_per_ttl)

        if timings_per_host[ttl]:
            avg_rtt = statistics.mean(timings_per_host[ttl])
            stddev_rtt = statistics.stdev(timings_per_host[ttl]) if len(timings_per_host[ttl]) > 1 else 0
            loss_pct = (loss_per_ttl[ttl]['loss'] / packet_count) * 100
            
            stdscr.addstr(ttl + 1, 0, f"{ttl:<5}{hostname or '*':<50}{format_value(timings_per_host[ttl][-1]):<15}"
                                      f"{format_value(min(timings_per_host[ttl])):<15}{format_value(avg_rtt):<15}"
                                      f"{format_value(max(timings_per_host[ttl])):<15}{stddev_rtt:<15.2f}{loss_pct:<15.2f}")
        else:
            stdscr.addstr(ttl + 1, 0, f"{ttl:<5}{'*':<50}{'*':<15}{'*':<15}{'*':<15}{'*':<15}{'*':<15}{'100.00':<15}")

        stdscr.refresh()
        time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(main)

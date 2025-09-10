#!/usr/bin/env python3
"""
Advanced Port Scanner
Author: Your Name
GitHub: https://github.com/yourusername
Description: A multi-threaded port scanner with banner grabbing and logging.
"""

import socket
import argparse
import threading
from datetime import datetime
from queue import Queue

queue = Queue()

print_lock = threading.Lock()

def get_banner(sock):
    """Attempt to grab a service banner from the port."""
    try:
        sock.send(b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        return sock.recv(1024).decode().strip()
    except:
        return "No banner available"

def scan_port(target, port, verbose=False):
    """Scan a single port."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((target, port))
        if result == 0:
            banner = get_banner(s)
            with print_lock:
                print(f"[+] Port {port} is OPEN - {banner}")
                if verbose:
                    print(f"    Service info: {banner}")
            log_result(target, port, banner)
        s.close()
    except Exception as e:
        with print_lock:
            print(f"[-] Error scanning port {port}: {str(e)}")

def worker(target, verbose):
    """Thread worker function to scan ports from the queue."""
    while not queue.empty():
        port = queue.get()
        scan_port(target, port, verbose)
        queue.task_done()

def log_result(target, port, banner):
    """Log open ports and their banners to a file."""
    with open("scan_results.txt", "a") as f:
        f.write(f"{datetime.now()} - {target}:{port} - {banner}\n")

def main():
    parser = argparse.ArgumentParser(description="Advanced Python Port Scanner")
    parser.add_argument("target", help="Target hostname or IP address to scan")
    parser.add_argument("-p", "--ports", help="Port range (e.g., 1-1024)", default="1-1024")
    parser.add_argument("-t", "--threads", help="Number of threads", type=int, default=50)
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    args = parser.parse_args()

    try:
        port_start, port_end = map(int, args.ports.split("-"))
    except:
        print("Invalid port range format. Example: 1-1024")
        return

    target_ip = socket.gethostbyname(args.target)
    print(f"\n[+] Scanning Target: {args.target} ({target_ip})")
    print(f"[+] Port Range: {port_start}-{port_end}")
    print(f"[+] Threads: {args.threads}")
    print("[+] Starting Scan...\n")
    start_time = datetime.now()

    for port in range(port_start, port_end + 1):
        queue.put(port)

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(target_ip, args.verbose))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"\n[+] Scan Completed in {total_time}")

if __name__ == "__main__":
    main()

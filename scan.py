import socket
import sys
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

target = sys.argv[1]
start_port = int(sys.argv[2])
end_port = int(sys.argv[3])

TIMEOUT = 0.02
MAX_THREADS = 300
port_count = 0

def TCP_scan_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        if sock.connect_ex((target, port)) == 0:
            return port
    return None

start_time = datetime.now()
open_ports = []

print(f"TCP Scanning {target} from port {start_port} to {end_port}...\n")
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(TCP_scan_port, p) for p in range(start_port, end_port+1)]
    for fut in as_completed(futures):
        result = fut.result()
        port_count += 1
        print(f"PROGRESS {port_count}", flush=True)
        if result is not None:
            print(f"Port {result} is OPEN")
            open_ports.append(result)
end_time = datetime.now()
try:
    host = socket.gethostbyaddr(target)
    print("\nReverse DNS:", host[0])
except socket.herror:
    print("No reverse DNS entry")

api_url = f"http://ip-api.com/json/{target}"
res = requests.get(api_url).json()
if res.get("status") == "success":
    print(f"Country: {res.get('country')}")
    print(f"City: {res.get('city')}")
    print(f"ISP: {res.get('isp')}")
    print(f"Latitude: {res.get('lat')}")
    print(f"Longitude: {res.get('lon')}")
else:
    print(f"Lookup failed: {res.get('message')}")

print(f"\nScan completed in: {end_time - start_time}")
import os

def check_ip_alive(ip):
    return True if os.system(f'ping -c 1 {ip}') == 0 else False
print(check_ip_alive("1227.0.0.1"))
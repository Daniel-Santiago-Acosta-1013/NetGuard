import os
import sys
from interface.cli import CLIInterface
from infrastructure.network_scanner import NetworkScanner
from infrastructure.device_manager import DeviceManager

def check_root():
    if os.geteuid() != 0:
        print("Este programa debe ejecutarse como root/sudo")
        sys.exit(1)

def main():
    check_root()
    cli = CLIInterface()
    scanner = NetworkScanner()
    manager = DeviceManager()
    
    while True:
        devices = scanner.scan()
        cli.show_menu()
        cli.display_devices(devices)
        
        action = cli.get_action()
        
        if action == "exit":
            break
            
        if action in ["block", "unblock", "throttle"]:
            ip = cli.select_device(devices)
            device = next(d for d in devices if d.ip == ip)
            
            if action == "block":
                manager.block_device(device.mac)
                cli.show_message(f"Dispositivo {ip} bloqueado")
            elif action == "unblock":
                manager.unblock_device(device.mac)
                cli.show_message(f"Dispositivo {ip} desbloqueado")
            elif action == "throttle":
                limit = cli.get_bandwidth_limit()
                manager.throttle_device(ip, limit)
                cli.show_message(f"Ancho de banda limitado a {limit} para {ip}")

if __name__ == "__main__":
    main()
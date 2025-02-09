import os
import sys
from interface.cli import CLIInterface
from infrastructure.network_scanner import NetworkScanner
from infrastructure.device_manager import DeviceManager
from rich.prompt import Prompt

def check_root():
    if os.geteuid() != 0:
        print("Este programa debe ejecutarse como root/sudo")
        sys.exit(1)

def main():
    check_root()
    cli = CLIInterface()
    scanner = NetworkScanner()
    manager = DeviceManager()
    
    # Realizar el primer escaneo de la red
    devices = scanner.scan()
    
    while True:
        option = cli.show_main_menu()
        
        if option == "1":
            # Ver dispositivos conectados
            cli.display_devices(devices)
            Prompt.ask("\nPresione Enter para continuar", default="")
            
        elif option == "2":
            # Bloquear dispositivo
            ip = cli.select_device(devices)
            if ip is None:
                continue
            device = next((d for d in devices if d.ip == ip), None)
            if device:
                manager.block_device(device.mac)
                device.is_blocked = True
                cli.show_message(f"Dispositivo {ip} bloqueado")
            else:
                cli.show_message("Dispositivo no encontrado")
            Prompt.ask("\nPresione Enter para continuar", default="")
            
        elif option == "3":
            # Bajar calidad de conexión (throttle)
            ip = cli.select_device(devices)
            if ip is None:
                continue
            device = next((d for d in devices if d.ip == ip), None)
            if device:
                limit = cli.get_bandwidth_limit()  # Ejemplo: "100kbit"
                try:
                    if limit.lower().endswith("kbit"):
                        numeric_limit = int(limit[:-4])
                    else:
                        numeric_limit = int(limit)
                        limit = f"{numeric_limit}kbit"
                except ValueError:
                    numeric_limit = 100
                    limit = "100kbit"
                manager.throttle_device(ip, limit)
                device.bandwidth_limit = numeric_limit
                cli.show_message(f"Ancho de banda limitado a {limit} para {ip}")
            else:
                cli.show_message("Dispositivo no encontrado")
            Prompt.ask("\nPresione Enter para continuar", default="")
            
        elif option == "4":
            # Reconectar dispositivo bloqueado (desbloquear)
            ip = cli.select_device(devices)
            if ip is None:
                continue
            device = next((d for d in devices if d.ip == ip), None)
            if device:
                manager.unblock_device(device.mac)
                device.is_blocked = False
                cli.show_message(f"Dispositivo {ip} reconectado")
            else:
                cli.show_message("Dispositivo no encontrado")
            Prompt.ask("\nPresione Enter para continuar", default="")
            
        elif option == "5":
            # Escanear red nuevamente
            devices = scanner.scan()
            cli.show_message("Escaneo completado!")
            Prompt.ask("\nPresione Enter para continuar", default="")
            
        elif option == "6":
            break

if __name__ == "__main__":
    main()

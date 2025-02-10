from scapy.all import ARP, Ether, srp
from rich.progress import Progress
from core.entities import Device
from core.use_cases import NetworkUseCases
import netifaces
import ipaddress
import platform
import subprocess
import os
import re

class NetworkScanner:
    def __init__(self, interface=None):
        if interface is None:
            # Buscar una interfaz inalámbrica (excluyendo loopback) con dirección IPv4
            wireless_iface = None
            for iface in netifaces.interfaces():
                if iface == "lo":
                    continue
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    # Si existe el directorio "wireless", se asume que es inalámbrica
                    if os.path.exists(f"/sys/class/net/{iface}/wireless"):
                        wireless_iface = iface
                        break
            if wireless_iface:
                interface = wireless_iface
            else:
                # Si no se encuentra una interfaz inalámbrica, se utiliza la interfaz por defecto a partir de la gateway
                gateways = netifaces.gateways()
                default_iface = gateways.get('default', {}).get(netifaces.AF_INET, [None, None])[1]
                if default_iface is None:
                    # Fallback: buscar una interfaz no loopback con dirección IPv4
                    for iface in netifaces.interfaces():
                        if iface == "lo":
                            continue
                        addrs = netifaces.ifaddresses(iface)
                        if netifaces.AF_INET in addrs:
                            default_iface = iface
                            break
                    if default_iface is None:
                        default_iface = "eth0"
                interface = default_iface
        self.interface = interface
        self.devices = []

    def scan(self, timeout=2):
        # Reiniciar la lista de dispositivos en cada escaneo
        self.devices = []
        with Progress() as progress:
            task = progress.add_task("[cyan]Escaneando red...", total=100)
            
            # Obtener rango de IP automáticamente
            ip_range = self._get_ip_range()
            
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            
            ans, _ = srp(packet, timeout=timeout, iface=self.interface, verbose=0)
            
            for i, (sent, received) in enumerate(ans):
                device_ip = received.psrc
                # Si la IP es privada, no se puede determinar una IP pública individual
                if ipaddress.ip_address(device_ip).is_private:
                    public_ip = "N/A"
                else:
                    public_ip = device_ip
                device = Device(
                    ip=device_ip,
                    mac=received.hwsrc,
                    vendor=NetworkUseCases.get_vendor(received.hwsrc),
                    os=NetworkUseCases.detect_os(device_ip),
                    public_ip=public_ip
                )
                self.devices.append(device)
                progress.update(task, advance=100 / len(ans) if len(ans) else 100)
        
        # Actualizar las direcciones MAC consultando la tabla ARP del sistema
        self.update_mac_addresses()
        return self.devices

    def update_mac_addresses(self):
        try:
            arp_output = subprocess.check_output(["arp", "-a"], text=True)
            # Expresión regular para capturar IP y MAC (compatible con Linux y macOS)
            pattern = re.compile(r'\(?(\d+\.\d+\.\d+\.\d+)\)?\s+at\s+([0-9a-fA-F:]{17})')
            ip_to_mac = {}
            for line in arp_output.splitlines():
                match = pattern.search(line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).lower()
                    ip_to_mac[ip] = mac
            for device in self.devices:
                if device.ip in ip_to_mac:
                    device.mac = ip_to_mac[device.ip]
        except Exception as e:
            print("Error al actualizar las MAC addresses:", e)

    def _get_ip_range(self):
        addresses = netifaces.ifaddresses(self.interface).get(netifaces.AF_INET)
        if addresses:
            ip = addresses[0]['addr']
            netmask = addresses[0]['netmask']
            network = ipaddress.IPv4Interface(f"{ip}/{netmask}").network
            return str(network)
        else:
            raise Exception("No se pudo determinar la IP de la interfaz")

    def get_external_ip(self):
        """
        Obtiene la IP pública externa utilizando un servicio en línea.
        (No se utiliza en la asignación de IP pública por dispositivo, ya que cada dispositivo
         debe mostrar su propia IP pública si está asignada, o 'N/A' si está tras NAT.)
        """
        try:
            import urllib.request
            with urllib.request.urlopen("https://api.ipify.org") as response:
                return response.read().decode().strip()
        except Exception:
            return "N/A"

    def get_network_name(self):
        """
        Obtiene el nombre (SSID) de la red a la que está conectada la interfaz.
        En Linux se utiliza 'iwgetid' si es inalámbrica; en macOS se usa el comando 'airport'.
        Si no es inalámbrica se retorna el nombre de la interfaz con una indicación.
        """
        system = platform.system()
        if system == "Linux":
            wireless_path = f"/sys/class/net/{self.interface}/wireless"
            if os.path.exists(wireless_path):
                try:
                    ssid = subprocess.check_output(
                        ["iwgetid", self.interface, "--raw"],
                        text=True
                    ).strip()
                    if ssid:
                        return ssid
                except Exception:
                    pass
            return f"{self.interface} (cableado)"
        elif system == "Darwin":
            try:
                airport_output = subprocess.check_output(
                    ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                    text=True
                )
                for line in airport_output.splitlines():
                    if "SSID:" in line:
                        return line.split("SSID:")[1].strip()
            except Exception:
                pass
            return f"{self.interface} (no wifi)"
        else:
            return self.interface

from scapy.all import ARP, Ether, srp
from rich.progress import Progress
from core.entities import Device
from core.use_cases import NetworkUseCases
import netifaces

class NetworkScanner:
    def __init__(self, interface=None):
        # Si no se especifica interfaz, se detecta la interfaz por defecto a partir de la gateway
        if interface is None:
            gateways = netifaces.gateways()
            default_iface = gateways.get('default', {}).get(netifaces.AF_INET, [None, None])[1]
            if default_iface is None:
                # Fallback: buscar una interfaz no loopback que tenga dirección IPv4
                for iface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs:
                        ip = addrs[netifaces.AF_INET][0]['addr']
                        if not ip.startswith("127."):
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
                device = Device(
                    ip=received.psrc,
                    mac=received.hwsrc,
                    vendor=NetworkUseCases.get_vendor(received.hwsrc),
                    os=NetworkUseCases.detect_os(received.psrc)
                )
                self.devices.append(device)
                # Actualizar progreso en función de la cantidad de respuestas
                progress.update(task, advance=100 / len(ans) if len(ans) else 100)
        
        return self.devices

    def _get_ip_range(self):
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
        if default_gateway:
            gw_ip = default_gateway[0]
        else:
            # Fallback: usar la dirección IP asignada a la interfaz especificada
            addresses = netifaces.ifaddresses(self.interface)
            ip_info = addresses.get(netifaces.AF_INET)
            if ip_info:
                gw_ip = ip_info[0]['addr']
            else:
                raise Exception("No se pudo determinar la IP de la interfaz")
        subnet = gw_ip.rsplit('.', 1)[0] + '.0/24'
        return subnet

from scapy.all import ARP, Ether, srp
from rich.progress import Progress
from core.entities import Device
from core.use_cases import NetworkUseCases

class NetworkScanner:
    def __init__(self, interface="wlan0"):
        self.interface = interface
        self.devices = []

    def scan(self, timeout=2):
        with Progress() as progress:
            task = progress.add_task("[cyan]Escaneando red...", total=100)
            
            # Obtener rango de IP automáticamente
            ip_range = self._get_ip_range()
            
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            ans, _ = srp(packet, timeout=timeout, iface=self.interface, verbose=0)
            
            for i, (sent, received) in enumerate(ans):
                device = Device(
                    ip=received.psrc,
                    mac=received.hwsrc,
                    vendor=NetworkUseCases.get_vendor(received.hwsrc),
                    os=NetworkUseCases.detect_os(received.psrc)
                )
                self.devices.append(device)
                progress.update(task, advance=100/len(ans))
        
        return self.devices

    def _get_ip_range(self):
        import netifaces
        gw_ip = netifaces.gateways()['default'][netifaces.AF_INET][0]
        subnet = gw_ip.rsplit('.', 1)[0] + '.0/24'
        return subnet
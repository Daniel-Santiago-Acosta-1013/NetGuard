import subprocess
from python_iptables import Iptables

class DeviceManager:
    def __init__(self):
        self.iptables = Iptables()
        
    def block_device(self, mac):
        self.iptables.append('FORWARD', '-m', 'mac', '--mac-source', mac, '-j', 'DROP')
        self.iptables.commit()
        
    def unblock_device(self, mac):
        self.iptables.delete('FORWARD', '-m', 'mac', '--mac-source', mac, '-j', 'DROP')
        self.iptables.commit()
        
    def throttle_device(self, ip, limit='100kbit'):
        # Configurar control de ancho de banda con tc
        subprocess.run([
            'tc', 'qdisc', 'add', 'dev', 'wlan0', 'root', 
            'handle', '1:', 'htb', 'default', '12'
        ])
        subprocess.run([
            'tc', 'class', 'add', 'dev', 'wlan0', 'parent', '1:', 
            'classid', '1:1', 'htb', 'rate', limit
        ])
        subprocess.run([
            'tc', 'filter', 'add', 'dev', 'wlan0', 'protocol', 'ip', 
            'parent', '1:', 'prio', '1', 'u32', 'match', 'ip', 'dst', 
            ip, 'flowid', '1:1'
        ])
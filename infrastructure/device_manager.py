import subprocess
import shutil
import platform
from infrastructure.iptables_wrapper import Iptables

class DeviceManager:
    def __init__(self):
        self.iptables = Iptables()
        self.system = platform.system()
        if self.system == "Darwin":
            self.setup_pf()

    def setup_pf(self):
        pf_conf = (
            "table <netguard> persist\n"
            "block drop in quick from <netguard>\n"
            "block drop out quick to <netguard>\n"
        )
        conf_file = "/tmp/netguard_pf.conf"
        try:
            with open(conf_file, "w") as f:
                f.write(pf_conf)
            subprocess.run(["sudo", "pfctl", "-f", conf_file],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            subprocess.run(["sudo", "pfctl", "-E"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            print("Error configurando PF en macOS:", e)
        except Exception as e:
            print("Error general en setup_pf:", e)

    def block_device(self, mac, ip=None):
        try:
            if self.system == "Linux":
                # Agregar regla iptables para bloquear por MAC
                subprocess.run(
                    ['iptables', '-A', 'FORWARD', '-m', 'mac', '--mac-source', mac, '-j', 'DROP'],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Intentar desconectar usando iw si está disponible
                if shutil.which('iw'):
                    try:
                        subprocess.run(
                            ['iw', 'dev', 'wlan0', 'station', 'del', mac],
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except subprocess.CalledProcessError as e:
                        print(f"Error desconectando dispositivo {mac} con iw:", e.stderr)
                else:
                    print(f"Advertencia: 'iw' no encontrado. No se pudo desconectar {mac}")

            elif self.system == "Darwin" and ip:
                subprocess.run(
                    ['sudo', 'pfctl', '-t', 'netguard', '-T', 'add', ip],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

        except subprocess.CalledProcessError as e:
            print(f"Error bloqueando dispositivo {mac}:", e.stderr)
        except Exception as e:
            print(f"Error inesperado en block_device:", e)

    def unblock_device(self, mac, ip=None):
        try:
            if self.system == "Linux":
                # Eliminar regla iptables
                subprocess.run(
                    ['iptables', '-D', 'FORWARD', '-m', 'mac', '--mac-source', mac, '-j', 'DROP'],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            elif self.system == "Darwin" and ip:
                subprocess.run(
                    ['sudo', 'pfctl', '-t', 'netguard', '-T', 'delete', ip],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

        except subprocess.CalledProcessError as e:
            print(f"Error desbloqueando dispositivo {mac}:", e.stderr)
        except Exception as e:
            print(f"Error inesperado en unblock_device:", e)

    def throttle_device(self, ip, limit='100kbit'):
        try:
            subprocess.run(['tc', 'qdisc', 'del', 'dev', 'wlan0', 'root'],
                        stderr=subprocess.DEVNULL)
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', 'wlan0', 'root', 
                'handle', '1:', 'htb', 'default', '12'
            ], check=True)
            subprocess.run([
                'tc', 'class', 'add', 'dev', 'wlan0', 'parent', '1:', 
                'classid', '1:1', 'htb', 'rate', limit
            ], check=True)
            subprocess.run([
                'tc', 'filter', 'add', 'dev', 'wlan0', 'protocol', 'ip', 
                'parent', '1:', 'prio', '1', 'u32', 'match', 'ip', 'dst', 
                ip, 'flowid', '1:1'
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error aplicando throttling a {ip}:", e.stderr)
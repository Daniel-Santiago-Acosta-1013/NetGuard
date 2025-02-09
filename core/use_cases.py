import subprocess
import re

class NetworkUseCases:
    @staticmethod
    def get_vendor(mac: str) -> str:
        from mac_vendor_lookup import MacLookup  # type: ignore
        try:
            return MacLookup().lookup(mac)
        except Exception:
            return "Unknown"

    @staticmethod
    def detect_os(ip: str) -> str:
        try:
            # Ejecutar escaneo nmap con guess OS
            result = subprocess.run(
                ['nmap', '-O', '--osscan-guess', ip],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Buscar patrones de sistema operativo en la salida
            os_pattern = r"(Aggressive OS guesses:|OS details:)\s*(.*)"
            matches = re.findall(os_pattern, result.stdout)
            
            if matches:
                # Tomar la primera coincidencia y limpiar el texto
                os_info = matches[0][1].split(',')[0].strip()
                return os_info.replace('OS details: ', '').split(' (')[0]
                
        except (subprocess.TimeoutExpired, FileNotFoundError, IndexError):
            pass
            
        return "Unknown"

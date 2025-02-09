from typing import List
from .entities import Device

class NetworkUseCases:
    @staticmethod
    def get_vendor(mac: str) -> str:
        from mac_vendor_lookup import MacLookup
        try:
            return MacLookup().lookup(mac)
        except:
            return "Unknown"

    @staticmethod
    def detect_os(ip: str) -> str:
        # Implementación básica - mejorar con nmap en producción
        return "Unknown"
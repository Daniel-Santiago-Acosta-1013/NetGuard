import os
import sys
from PyQt5.QtWidgets import QApplication
from interface.gui import GUIInterface
from infrastructure.network_scanner import NetworkScanner
from infrastructure.device_manager import DeviceManager

def check_root():
    if os.geteuid() != 0:
        print("Este programa debe ejecutarse como root/sudo")
        sys.exit(1)

def main():
    check_root()
    app = QApplication(sys.argv)
    scanner = NetworkScanner()
    manager = DeviceManager()
    # Realizar el primer escaneo de la red
    devices = scanner.scan()
    # Obtener el nombre de la red conectada (válido para Linux y macOS)
    network_name = scanner.get_network_name()
    gui = GUIInterface(devices, scanner, manager, network_name)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QMessageBox, QInputDialog, QScrollArea, QFrame, QLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

# --- FlowLayout (para distribución responsive de las tarjetas) ---
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []
        self.setSpacing(spacing)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

# --- Tarjeta para cada dispositivo ---
class DeviceCard(QFrame):
    def __init__(self, device, manager, parent=None):
        super().__init__(parent)
        self.device = device
        self.manager = manager
        self.initUI()
    
    def initUI(self):
        # Configuración del marco (tarjeta) con borde de color según estado
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet(self.cardStyle())
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Etiqueta con la información del dispositivo (usando HTML para formato)
        self.info_label = QLabel(self.device_info_text())
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Botones internos para acciones específicas del dispositivo
        btn_layout = QHBoxLayout()
        self.btn_block = QPushButton("Bloquear")
        self.btn_throttle = QPushButton("Throttle")
        self.btn_reconnect = QPushButton("Reconectar")
        btn_layout.addWidget(self.btn_block)
        btn_layout.addWidget(self.btn_throttle)
        btn_layout.addWidget(self.btn_reconnect)
        layout.addLayout(btn_layout)
        
        # Conexión de señales
        self.btn_block.clicked.connect(self.block_device)
        self.btn_throttle.clicked.connect(self.throttle_device)
        self.btn_reconnect.clicked.connect(self.reconnect_device)
    
    def device_info_text(self):
        # Construye el HTML con la información del dispositivo
        estado = "Bloqueado" if self.device.is_blocked else "Activo"
        ancho = f"{self.device.bandwidth_limit}kbit" if self.device.bandwidth_limit else "Ilimitado"
        text = (
            f"<b>IP:</b> {self.device.ip}<br>"
            f"<b>IP Pública:</b> {self.device.public_ip}<br>"
            f"<b>MAC:</b> {self.device.mac}<br>"
            f"<b>Fabricante:</b> {self.device.vendor}<br>"
            f"<b>OS:</b> {self.device.os}<br>"
            f"<b>Estado:</b> {estado}<br>"
            f"<b>Ancho de Banda:</b> {ancho}"
        )
        return text
    
    def cardStyle(self):
        # Define el estilo: solo se colorea el borde según el estado
        if self.device.is_blocked:
            border_color = "red"
        else:
            border_color = "green"
        style = f"""
            QFrame {{
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 10px;
            }}
        """
        return style
    
    def update_card(self):
        # Actualiza la información y el estilo de la tarjeta
        self.info_label.setText(self.device_info_text())
        self.setStyleSheet(self.cardStyle())
    
    def block_device(self):
        self.manager.block_device(self.device.mac)
        self.device.is_blocked = True
        QMessageBox.information(self, "Información", f"Dispositivo {self.device.ip} bloqueado")
        self.update_card()
    
    def throttle_device(self):
        limit, ok = QInputDialog.getText(
            self, "Límite de ancho de banda",
            "Ingrese el límite de ancho de banda (ej: 100kbit):"
        )
        if not ok or not limit:
            return
        try:
            if limit.lower().endswith("kbit"):
                numeric_limit = int(limit[:-4])
            else:
                numeric_limit = int(limit)
                limit = f"{numeric_limit}kbit"
        except ValueError:
            numeric_limit = 100
            limit = "100kbit"
        self.manager.throttle_device(self.device.ip, limit)
        self.device.bandwidth_limit = numeric_limit
        QMessageBox.information(self, "Información", f"Ancho de banda limitado a {limit} para {self.device.ip}")
        self.update_card()
    
    def reconnect_device(self):
        self.manager.unblock_device(self.device.mac)
        self.device.is_blocked = False
        QMessageBox.information(self, "Información", f"Dispositivo {self.device.ip} reconectado")
        self.update_card()

# --- Interfaz Gráfica Principal ---
class GUIInterface(QMainWindow):
    def __init__(self, devices, scanner, manager, network_name):
        super().__init__()
        self.devices = devices
        self.scanner = scanner
        self.manager = manager
        self.network_name = network_name
        self.setWindowTitle("NetGuard - Administrador de Red")
        self.resize(800, 600)
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Mostrar el nombre de la red conectada
        label = QLabel(f"Conectado a la red: {self.network_name}")
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)
        
        # Área de desplazamiento para las tarjetas de dispositivos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)
        
        self.cards_container = QWidget()
        self.flow_layout = FlowLayout(self.cards_container, margin=10, spacing=10)
        self.cards_container.setLayout(self.flow_layout)
        self.scroll_area.setWidget(self.cards_container)
        
        self.update_cards()
        
        # Botones generales (rescan y salir) en la parte inferior izquierda
        btn_layout = QHBoxLayout()
        self.btn_rescan = QPushButton("Escanear red nuevamente")
        self.btn_exit = QPushButton("Salir")
        btn_layout.addWidget(self.btn_rescan)
        btn_layout.addWidget(self.btn_exit)
        btn_layout.addStretch()  # Alinea los botones a la izquierda
        main_layout.addLayout(btn_layout)
        
        self.btn_rescan.clicked.connect(self.rescan_network)
        self.btn_exit.clicked.connect(self.close)
    
    def update_cards(self):
        # Limpia el layout del FlowLayout y agrega una tarjeta por cada dispositivo
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
        for device in self.devices:
            card = DeviceCard(device, self.manager)
            self.flow_layout.addWidget(card)
    
    def rescan_network(self):
        self.devices = self.scanner.scan()
        QMessageBox.information(self, "Información", "Escaneo completado!")
        self.update_cards()

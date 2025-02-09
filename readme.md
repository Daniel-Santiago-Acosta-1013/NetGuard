# NetGuard - Guía de Uso Rápido

NetGuard es una herramienta CLI para administrar dispositivos en tu red Wi-Fi. Permite escanear, bloquear, desbloquear y limitar el ancho de banda de dispositivos conectados.

---

## Requisitos Previos

- **Sistema Operativo**: Linux (preferiblemente distribuciones basadas en Debian/Ubuntu).
- **Permisos**: Necesitas ejecutar el programa como root o con `sudo`.
- **Python**: Versión 3.8 o superior.

---

## Configuración del Entorno Virtual

1. **Crear el entorno virtual**:
   ```bash
   python3 -m venv netguard-env
   ```

2. **Activar el entorno virtual**:
   ```bash
   source netguard-env/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Ejecución del Programa

1. **Iniciar NetGuard**:
   ```bash
   sudo python main.py
   ```

2. **Interfaz Principal**:
   - Al iniciar, se escaneará automáticamente la red y se mostrará una lista de dispositivos conectados.
   - Cada dispositivo se muestra con su IP, MAC, fabricante, sistema operativo, estado y ancho de banda.

3. **Opciones Disponibles**:
   - **block**: Bloquear un dispositivo por su IP.
   - **unblock**: Desbloquear un dispositivo previamente bloqueado.
   - **throttle**: Limitar el ancho de banda de un dispositivo.
   - **refresh**: Volver a escanear la red.
   - **exit**: Salir del programa.

---

## Ejemplos de Uso

1. **Bloquear un dispositivo**:
   - Selecciona `block` y luego ingresa la IP del dispositivo que deseas bloquear.

2. **Limitar el ancho de banda**:
   - Selecciona `throttle`, ingresa la IP y especifica el límite (ej: `100kbit`).

3. **Actualizar la lista de dispositivos**:
   - Selecciona `refresh` para volver a escanear la red.

---

## Notas Adicionales

- **Detección de SO**: La detección del sistema operativo es básica. Para mejorarla, instala `nmap` y configura la integración.
- **Permisos de Red**: Asegúrate de tener permisos suficientes para modificar reglas de iptables y configurar tc.
- **Interfaz de Red**: Si tu interfaz no es `wlan0`, modifica el valor en `network_scanner.py`.

---

## Soporte y Contribuciones

Si encuentras algún problema o tienes sugerencias, abre un issue en el repositorio oficial. ¡Las contribuciones son bienvenidas!

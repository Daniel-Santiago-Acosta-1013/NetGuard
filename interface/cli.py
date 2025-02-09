import sys

try:
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
    from rich.prompt import Prompt  # type: ignore
    from rich.panel import Panel  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write(
        "El módulo 'rich' es necesario. Por favor, instale 'rich' ejecutando:\n"
        "python3 -m pip install rich\n"
    )
    sys.exit(1)

from core.entities import Device

class CLIInterface:
    def __init__(self):
        self.console = Console()
        
    def show_menu(self):
        self.console.clear()
        self.console.print(Panel.fit("[bold green]NetGuard - Administrador de Red[/bold green]"))
        
    def display_devices(self, devices: list[Device]):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("IP", style="cyan")
        table.add_column("MAC", style="magenta")
        table.add_column("Fabricante")
        table.add_column("OS")
        table.add_column("Estado")
        table.add_column("Ancho de Banda")
        
        for device in devices:
            status = "[red]Bloqueado" if device.is_blocked else "[green]Activo"
            bandwidth = f"{device.bandwidth_limit}kbit" if device.bandwidth_limit else "Ilimitado"
            table.add_row(
                device.ip,
                device.mac,
                device.vendor,
                device.os,
                status,
                bandwidth
            )
            
        self.console.print(table)
        
    def select_device(self, devices: list[Device]):
        """
        Muestra una tabla enumerada de dispositivos y permite seleccionar uno por su número.
        Se puede ingresar "0" para volver al menú principal.
        """
        if not devices:
            self.console.print("[red]No hay dispositivos disponibles.[/red]")
            return None
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Número", style="cyan")
        table.add_column("IP", style="cyan")
        table.add_column("MAC", style="magenta")
        table.add_column("Fabricante")
        table.add_column("OS")
        table.add_column("Estado")
        table.add_column("Ancho de Banda")
        
        for idx, device in enumerate(devices, start=1):
            status = "[red]Bloqueado" if device.is_blocked else "[green]Activo"
            bandwidth = f"{device.bandwidth_limit}kbit" if device.bandwidth_limit else "Ilimitado"
            table.add_row(
                str(idx),
                device.ip,
                device.mac,
                device.vendor,
                device.os,
                status,
                bandwidth
            )
        self.console.print(table)
        
        valid_choices = [str(i) for i in range(1, len(devices) + 1)]
        valid_choices.append("0")
        selection = Prompt.ask("Seleccione el número del dispositivo (0 para volver)", choices=valid_choices)
        if selection == "0":
            return None
        index = int(selection) - 1
        return devices[index].ip
    
    def get_bandwidth_limit(self):
        return Prompt.ask("Ingrese el límite de ancho de banda (ej: 100kbit)")
    
    def show_message(self, message):
        self.console.print(Panel.fit(f"[yellow]{message}[/yellow]"))
        
    def show_main_menu(self):
        self.console.clear()
        menu_text = (
            "[bold green]Escaneo completado![/bold green]\n\n"
            "[bold]Menú Principal[/bold]\n"
            "1. Ver dispositivos conectados\n"
            "2. Bloquear dispositivo\n"
            "3. Bajar calidad de conexión de un dispositivo\n"
            "4. Reconectar dispositivo bloqueado\n"
            "5. Escanear red nuevamente\n"
            "6. Salir\n"
        )
        self.console.print(Panel.fit(menu_text, title="NetGuard"))
        return Prompt.ask("Selecciona una opción", choices=["1", "2", "3", "4", "5", "6"])

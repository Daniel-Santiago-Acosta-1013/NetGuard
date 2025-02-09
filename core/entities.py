from dataclasses import dataclass

@dataclass
class Device:
    ip: str
    mac: str
    vendor: str
    os: str = "Unknown"
    is_blocked: bool = False
    bandwidth_limit: int = 0
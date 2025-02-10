from dataclasses import dataclass

@dataclass
class VersionResponse:
    firmware_version: int
    hardware_version: int
    protocol_version: int

@dataclass
class VersionStringResponse:
    version: str
    name: str
    board: str
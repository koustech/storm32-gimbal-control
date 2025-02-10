from dataclasses import dataclass
from enum import Enum

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

class PanMode(Enum):
    OFF = 0
    HOLD_HOLD_PAN = 1
    HOLD_HOLD_HOLD = 2
    PAN_PAN_PAN = 3
    PAN_HOLD_HOLD = 4
    PAN_HOLD_PAN = 5
    HOLD_PAN_PAN = 6

from dataclasses import dataclass
from enum import Enum, Flag, auto

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

class StandBySwitch(Enum):
    OFF = 0
    ON = 1
    
class DoCameraMode(Enum):
    OFF = 0
    IRSHUTTER = 1
    IRSHUTTERDELAYED = 2
    IRVIDEOON = 3
    IRVIDEOOFF = 4
    
class ScriptControlMode(Enum):
    OFF = 0
    CASE_DEFAULT = 1
    CASE_1 = 2
    CASE_2 = 3
    CASE_3 = 4
    
class PanModeSetting(Enum):
    DEFAULT_SETTING = 0x00
    SETTING_1 = 0x01
    SETTING_2 = 0x02
    SETTING_3 = 0x03

class SetAngleFlags(Flag):
    PITCH_LIMITED = 0x01
    ROLL_LIMITED = 0x02
    YAW_LIMITED = 0x04

    @classmethod
    def from_axes(cls, pitch: bool, roll: bool, yaw: bool):
        """Create a flag value based on which axes should be limited."""
        flag = cls(0)
        if pitch:
            flag |= cls.PITCH_LIMITED
        if roll:
            flag |= cls.ROLL_LIMITED
        if yaw:
            flag |= cls.YAW_LIMITED
        return flag

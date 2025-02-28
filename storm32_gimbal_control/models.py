from dataclasses import dataclass
from enum import Enum, Flag, IntFlag
import struct

@dataclass
class VersionResponse:
    """Response to the GETVERSION command."""
    firmware_version: int
    setup_layout_version: int
    board_capabilities: int

@dataclass
class VersionStringResponse:
    """Response to the GETVERSIONSTR command."""
    version: str
    name: str
    board: str

@dataclass
class DataStreamResponse:
    """Response to the GETDATA command."""
    state: int
    status: int
    status2: int
    i2c_errors: int
    lipo_voltage: int
    timestamp: int
    cycle_time: int
    imu1_gyro: tuple
    imu1_acc: tuple
    imu1_rotation: tuple
    imu1_pitch: float
    imu1_roll: float
    imu1_yaw: float
    pid_pitch: float
    pid_roll: float
    pid_yaw: float
    input_pitch: int
    input_roll: int
    input_yaw: int
    imu2_pitch: float
    imu2_roll: float
    imu2_yaw: float
    mag_yaw: float
    mag_pitch: float
    imu_acc_confidence: float
    extra_function_input: int

    @classmethod
    def from_data_stream(cls, data_stream):
        """Parses a 74-byte data stream and returns a DataStreamResponse object."""
        if len(data_stream) != 64:
            raise ValueError(f"Invalid data length: expected 74 bytes, got {len(data_stream)}")

        values = struct.unpack("<32h", bytes(data_stream[:64]))

        return cls(
            state=values[0],
            status=values[1],
            status2=values[2],
            i2c_errors=values[3],
            lipo_voltage=values[4],
            timestamp=values[5],
            cycle_time=values[6],
            imu1_gyro=values[7:10],  # (gx, gy, gz)
            imu1_acc=values[10:13],  # (ax, ay, az)
            imu1_rotation=values[13:16],  # (Rx, Ry, Rz)
            imu1_pitch=values[16] / 100.0,
            imu1_roll=values[17] / 100.0,
            imu1_yaw=values[18] / 100.0,
            pid_pitch=values[19] / 100.0,
            pid_roll=values[20] / 100.0,
            pid_yaw=values[21] / 100.0,
            input_pitch=values[22],
            input_roll=values[23],
            input_yaw=values[24],
            imu2_pitch=values[25] / 100.0,
            imu2_roll=values[26] / 100.0,
            imu2_yaw=values[27] / 100.0,
            mag_yaw=values[28] / 100.0,
            mag_pitch=values[29] / 100.0,
            imu_acc_confidence=values[30] / 10000.0,
            extra_function_input=values[31],
        )

class PanMode(Enum):
    """Pan mode settings."""
    OFF = 0
    HOLD_HOLD_PAN = 1
    HOLD_HOLD_HOLD = 2
    PAN_PAN_PAN = 3
    PAN_HOLD_HOLD = 4
    PAN_HOLD_PAN = 5
    HOLD_PAN_PAN = 6

class StandBySwitch(Enum):
    """Standby switch settings."""
    OFF = 0
    ON = 1
    
class DoCameraMode(Enum):
    """Camera mode settings."""
    OFF = 0
    IRSHUTTER = 1
    IRSHUTTERDELAYED = 2
    IRVIDEOON = 3
    IRVIDEOOFF = 4
    
class ScriptControlMode(Enum):
    """Script control mode settings."""
    OFF = 0
    CASE_DEFAULT = 1
    CASE_1 = 2
    CASE_2 = 3
    CASE_3 = 4
    
class PanModeSetting(Enum):
    """Pan mode settings."""
    DEFAULT_SETTING = 0x00
    SETTING_1 = 0x01
    SETTING_2 = 0x02
    SETTING_3 = 0x03

class SetAngleFlags(Flag):
    """Flags for setting angles."""
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

class LiveDataFields(IntFlag):
    """Data fields that can be requested in the GETDATAFIELDS command."""
    STATUS = 0x0001
    TIMES = 0x0001  # Same value as STATUS, needs clarification
    IMU1_GYRO = 0x0004
    IMU1_ACC = 0x0008
    IMU1_R = 0x0010
    IMU1_ANGLES = 0x0020
    PID_CONTROL = 0x0040
    INPUTS = 0x0080
    IMU2_ANGLES = 0x0100
    MAG_ANGLES = 0x0200
    STORM32_LINK = 0x0400
    IMU_ACC_CONFIDENCE = 0x0800

import serial
from storm32_gimbal_control import utils
from storm32_gimbal_control import constants
from storm32_gimbal_control import models
import logging
import struct

logging.basicConfig(level=logging.INFO)

def get_version(serial_port: serial.Serial) -> models.VersionResponse:
    """
    Retrieves the firmware version of the Storm32 gimbal controller.
    
    :param serial_port: Open serial port connection
    :return: VersionResponse object containing firmware version details
    """
    utils.send_command(serial_port, constants.CMD_GETVERSION, [])
    return utils.read_from_serial(serial_port, 11)
    
def get_version_str(serial_port: serial.Serial) -> models.VersionStringResponse:
    """
    Retrieves the firmware version as a string.
    
    :param serial_port: Open serial port connection
    :return: VersionStringResponse object containing firmware version string
    """
    utils.send_command(serial_port, constants.CMD_GETVERSIONSTR, [])
    return utils.read_from_serial(serial_port, 5+16*3)
    
def get_parameter(serial_port: serial.Serial, param_id: int) -> int:
    """
    Retrieves the value of a specific parameter from the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param param_id: ID of the parameter to retrieve (0-65535)
    :return: Parameter value as an integer
    """
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")

    data = [param_id & 0xFF, (param_id >> 8) & 0xFF]
    utils.send_command(serial_port, constants.CMD_GETPARAMETER, data)
    
    return utils.read_from_serial(serial_port, 9)

def set_parameter(serial_port: serial.Serial, param_id: int, param_value: int):
    """
    Sets a specific parameter value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param param_id: ID of the parameter to set (0-65535)
    :param param_value: Value to set for the parameter
    """
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")

    data = [
        param_id & 0xFF, (param_id >> 8) & 0xFF,
        param_value & 0xFF, (param_value >> 8) & 0xFF
    ]

    utils.send_command(serial_port, constants.CMD_SETPARAMETER, data)
    
    return utils.read_from_serial(serial_port, 6)

def get_data(serial_port: serial.Serial, type_byte: int):
    """
    Retrieves live data from the gimbal.
    
    :param serial_port: Open serial port connection
    :param type_byte: Type of data to request (Currently only type 0 is supported)
    :return: DataStreamResponse object containing live data
    """
    if type_byte != 0:
        raise ValueError("Invalid type_byte! Currently, only type 0 is supported.")

    data = [type_byte]

    utils.send_command(serial_port, constants.CMD_GETDATA, data)
    
    return utils.read_from_serial(serial_port, 74)

def get_data_fields(serial_port: serial.Serial, bitmask: models.LiveDataFields) -> tuple:
    """
    Retrieves live data fields from the gimbal.
    
    :param serial_port: Open serial port connection
    :param bitmask: Bitmask of fields to request (LiveDataFields enum values)
    :return: Tuple containing the bitmask and data fields
    """
    if not isinstance(bitmask, models.LiveDataFields):
        raise ValueError("Invalid bitmask. Use LiveDataFields enum values.")
    
    data = [bitmask & 0xFF, (bitmask >> 8) & 0xFF]

    utils.send_command(serial_port, constants.CMD_GETDATAFIELDS, data)
    
    return utils.read_from_serial(serial_port, 6)

def set_axis(serial_port: serial.Serial, command: int, value: int):
    """
    Sets a specific axis value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param command: Command ID for the axis to set
    :param value: Value to set for the axis
    """
    if not (700 <= value <= 2300) and not value == 0:
        raise ValueError("Invalid axis value. Must be 0 to recenter or between 700 and 2300.")
    
    data = [value & 0xFF, (value >> 8) & 0xFF]

    utils.send_command(serial_port, command, data)
    
    return utils.read_from_serial(serial_port, 6)

def set_pitch(serial_port: serial.Serial, value : int):
    """
    Sets the pitch value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param value: Value to set for the pitch axis
    """
    if not 700 <= value <= 2300 and not value == 0:
        raise ValueError("Invalid pitch value. Must be 0 to recenter or between 700 and 2300.")
    
    return set_axis(serial_port, constants.CMD_SETPITCH, value)

def set_roll(serial_port: serial.Serial, value: int):
    """
    Sets the roll value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param value: Value to set for the roll axis
    """
    if not 700 <= value <= 2300 and not value == 0:
        raise ValueError("Invalid pitch value. Must be 0 to recenter or between 700 and 2300.")
    
    return set_axis(serial_port, constants.CMD_SETROLL, value)

def set_yaw(serial_port: serial.Serial, value: int):
    """
    Sets the yaw value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param value: Value to set for the yaw axis
    """
    if not 700 <= value <= 2300 and not value == 0:
        raise ValueError("Invalid pitch value. Must be 0 to recenter or between 700 and 2300.")
    
    return set_axis(serial_port, constants.CMD_SETYAW, value)

def set_pan_mode(serial_port: serial.Serial, pan_mode: models.PanMode):
    """
    Sets the pan mode on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param pan_mode: PanMode enum value
    """
    if not isinstance(pan_mode, models.PanMode):
        raise ValueError("Invalid pan mode. Use PanMode enum values.")

    utils.send_command(serial_port, constants.CMD_SETPANMODE, [pan_mode.value])
    
    return utils.read_from_serial(serial_port, 6)

def set_standby(serial_port: serial.Serial, standby_switch: models.StandBySwitch):
    """
    Sets the standby mode on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param standby_switch: StandBySwitch enum value
    """
    if not isinstance(standby_switch, models.StandBySwitch):
        raise ValueError("Invalid standby switch. Use StandBySwitch enum values.")
    
    utils.send_command(serial_port, constants.CMD_SETSTANDBY, [standby_switch.value])
    
    return utils.read_from_serial(serial_port, 6)
    
def do_camera(serial_port: serial.Serial, camera_mode: models.DoCameraMode):
    """
    Sets the camera mode on the gimbal controller.

    :param serial_port: Open serial port connection
    :param camera_mode: DoCameraMode enum value
    """
    if not isinstance(camera_mode, models.DoCameraMode):
        raise ValueError("Invalid camera mode. Use DoCameraMode enum values.")
    
    utils.send_command(serial_port, constants.CMD_DOCAMERA, [0x00, camera_mode.value, 0x00, 0x00, 0x00, 0x00])
    
    return utils.read_from_serial(serial_port, 6)
    
def set_script_control(serial_port: serial.Serial, script_control_mode: models.ScriptControlMode):
    """
    Sets the script control mode on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param script_control_mode: ScriptControlMode enum value
    """
    if not isinstance(script_control_mode, models.ScriptControlMode):
        raise ValueError("Invalid camera mode. Use DoCameraMode enum values.")
    
    utils.send_command(serial_port, constants.CMD_SETSCRIPTCONTROL, [0x00, script_control_mode.value, 0x00, 0x00, 0x00, 0x00])
    
    return utils.read_from_serial(serial_port, 6)
    
def set_angle(serial_port: serial.Serial, pitch_degree: float, roll_degree: float, yaw_degree: float, flags: models.SetAngleFlags):
    """
    Sets the pitch, roll, and yaw angles on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param pitch_degree: Pitch angle in degrees
    :param roll_degree: Roll angle in degrees
    :param yaw_degree: Yaw angle in degrees
    :param flags: SetAngleFlags enum value
    """
    if not isinstance(flags, models.SetAngleFlags):
        raise ValueError("Invalid flags. Use SetAngleFlags enum values.")
    
    pitch_bytes = list(struct.pack('<f', pitch_degree))
    roll_bytes = list(struct.pack('<f', roll_degree))
    yaw_bytes = list(struct.pack('<f', yaw_degree))
    
    utils.send_command(serial_port, constants.CMD_SETANGLE, pitch_bytes + roll_bytes + yaw_bytes + [flags.value, 0x00])
    
    return utils.read_from_serial(serial_port, 6)
    
def set_pitch_roll_yaw(serial_port: serial.Serial, pitch: int, roll: int, yaw: int):
    """
    Sets the pitch, roll, and yaw values on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param pitch: Pitch value (0-2300)
    :param roll: Roll value (0-2300)
    :param yaw: Yaw value (0-2300)
    """
    if (pitch != 0) and not (700 <= pitch <= 2300):
        raise ValueError("Pitch value must be between 0 and 2300.")
    if (pitch != 0) and not (700 <= roll <= 2300):
        raise ValueError("Roll value must be between 0 and 2300.")
    if (pitch != 0) and not (700 <= yaw <= 2300):
        raise ValueError("Yaw value must be between 0 and 2300.")
    
    pitch_data = [pitch & 0xFF, (pitch >> 8) & 0xFF]
    roll_data = [roll & 0xFF, (roll >> 8) & 0xFF]
    yaw_data = [yaw & 0xFF, (yaw >> 8) & 0xFF]

    data = pitch_data + roll_data + yaw_data

    utils.send_command(serial_port, constants.CMD_SETPITCHROLLYAW, data)
    
    return utils.read_from_serial(serial_port, 6)
    
def set_pwm_out(serial_port: serial.Serial, input: int):
    """
    Sets the PWM output value on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param input: PWM output value (700-2300)
    """
    
    if (input != 0) and not (700 <= input <= 2300):
        raise ValueError("Input value must be between 0 and 2300.")
    
    data = [input & 0xFF, (input >> 8) & 0xFF]
    
    utils.send_command(serial_port, constants.CMD_SETPWMOUT, data)
    
    return utils.read_from_serial(serial_port, 6)
    
def restore_parameter(serial_port: serial.Serial, param: int):
    """
    Restores a specific parameter to its default value.
    
    :param serial_port: Open serial port connection
    :param param: ID of the parameter to restore (0-65535)
    """
    if not (0 <= param <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")
    
    data = [param & 0xFF, (param >> 8) & 0xFF]
    
    utils.send_command(serial_port, constants.CMD_RESTOREPARAMETER, data)
    
    return utils.read_from_serial(serial_port, 6)
    
def restore_all_parameters(serial_port: serial.Serial):
    """
    Restores all parameters to their default values.
    
    :param serial_port: Open serial port connection
    """
    utils.send_command(serial_port, constants.CMD_RESTOREALLPARAMETER, [])
    
    return utils.read_from_serial(serial_port, 6)
    
def active_pan_mode_setting(serial_port: serial.Serial, pan_mode_setting: models.PanModeSetting):
    """
    Sets the active pan mode setting on the gimbal controller.
    
    :param serial_port: Open serial port connection
    :param pan_mode_setting: PanModeSetting enum value
    """
    if not isinstance(pan_mode_setting, models.PanModeSetting):
        raise ValueError("Invalid pan mode setting. Use PanModeSetting enum values.")
    
    data = [pan_mode_setting.value & 0xFF, (pan_mode_setting.value >> 8) & 0xFF]
    
    utils.send_command(serial_port, constants.CMD_ACTIVEPANMODESETTING, data)
    
    return utils.read_from_serial(serial_port, 6)

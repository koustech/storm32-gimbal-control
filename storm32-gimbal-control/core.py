import serial
import utils
import constants
import models
import logging
import struct

logging.basicConfig(level=logging.INFO)

def get_version(serial_port: serial.Serial) -> models.VersionResponse:
    response = utils.send_command(serial_port, constants.CMD_GETVERSION, [], 11)
    if response is None:
        raise ValueError("Failed to retrieve version!")

    data1 = response[0] | (response[1] << 8)
    data2 = response[2] | (response[3] << 8)
    data3 = response[4] | (response[5] << 8)

    return models.VersionResponse(firmware_version=data1, hardware_version=data2, protocol_version=data3)

def get_version_str(serial_port: serial.Serial) -> models.VersionStringResponse:
    response = utils.send_command(serial_port, constants.CMD_GETVERSIONSTR, [], 53)
    if response is None:
        raise ValueError("Failed to retrieve version string!")

    version = response[:16].decode('utf-8').rstrip('\x00')
    name = response[16:32].decode('utf-8').rstrip('\x00')
    board = response[32:48].decode('utf-8').rstrip('\x00')

    return models.VersionStringResponse(version, name, board)

def get_parameter(serial_port: serial.Serial, param_id: int) -> int:
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")

    data = [param_id & 0xFF, (param_id >> 8) & 0xFF]
    response = utils.send_command(serial_port, constants.CMD_GETPARAMETER, data, 9)
    
    if response is None:
        raise ValueError("Failed to retrieve parameter!")

    received_param_id = response[0] | (response[1] << 8)
    param_value = response[2] | (response[3] << 8)

    if received_param_id != param_id:
        raise ValueError(f"Unexpected parameter ID received: {received_param_id}")

    return param_value

def set_parameter(serial_port: serial.Serial, param_id: int, param_value: int):
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")

    data = [
        param_id & 0xFF, (param_id >> 8) & 0xFF,
        param_value & 0xFF, (param_value >> 8) & 0xFF
    ]

    response = utils.send_command(serial_port, constants.CMD_SETPARAMETER, data, 3)
    if response is None:
        raise RuntimeError("No acknowledgment received for setting parameter.")

def get_data(serial_port: serial.Serial, type_byte: int):
    if type_byte != 0:
        raise ValueError("Invalid type_byte! Currently, only type 0 is supported.")
        
    header = [constants.STARTSIGNS.INCOMING, 0x01]
    command = [constants.CMD_GETDATA]
    data = [type_byte]
    
    packet = header + command + data
    
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF
    
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])
    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(9)

    if len(response) != 8:
        raise ValueError("Incomplete response received!")

    start_sign = response[0]
    packet_length = response[1]
    command = response[2]

    if start_sign != constants.STARTSIGNS.OUTGOING or packet_length != 1 or command != constants.CMD_GETDATA:
        raise ValueError("Invalid response format!")

    data_stream = response[3] | response[4] << 8 | response[5] << 8
    received_crc = response[-2] | (response[-1] << 8)

    calculated_crc = utils.calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        raise ValueError("CRC mismatch! Data may be corrupted.")

    return data_stream

def get_data_fields(serial_port: serial.Serial, bitmask: int) -> tuple:
    if not (0 <= bitmask <= 0xFFFF):
        raise ValueError("Bitmask must be a 16-bit integer (0x0000 - 0xFFFF).")

    header = [constants.STARTSIGNS.INCOMING, 0x02]
    command = [constants.CMD_GETDATAFIELDS]
    data = [bitmask & 0xFF, (bitmask >> 8) & 0xFF]

    packet = header + command + data

    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF

    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])

    serial_port.write(final_packet)

    # ------ READ ------
    header = serial_port.read(3)
    if len(header) != 3:
        raise ValueError("Incomplete header received!")

    start_sign, packet_length, command = header

    if start_sign != constants.STARTSIGNS.OUTGOING or command != constants.CMD_GETDATAFIELDS:
        raise ValueError("Invalid response format!")

    response = serial_port.read(packet_length + 2)

    if len(response) != packet_length + 2:
        raise ValueError("Incomplete response received!")

    received_bitmask = response[3] | (response[4] << 8)
    data_stream = response[5:-2]
    received_crc = response[-2] | (response[-1] << 8)

    calculated_crc = utils.calculate_crc(header + response[:-2])
    if received_crc != calculated_crc:
        raise ValueError("CRC mismatch! Data may be corrupted.")
    
    if received_bitmask != bitmask:
        raise ValueError(f"Bitmask mismatch! Expected {hex(bitmask)}, but got {hex(received_bitmask)}")

    return bitmask, data_stream

def set_axis(serial_port: serial.Serial, command: int, value: int):
    data = [value & 0xFF, (value >> 8) & 0xFF]

    response = utils.send_command(serial_port, command, data, 3)
    if response is None:
        raise RuntimeError(f"No acknowledgment received for {command} command.")

    print(f"{command} command acknowledged.")

def set_pitch(serial_port: serial.Serial, degree: int):
    set_axis(serial_port, constants.CMD_SETPITCH, degree)

def set_roll(serial_port: serial.Serial, degree: int):
    set_axis(serial_port, constants.CMD_SETROLL, degree)

def set_yaw(serial_port: serial.Serial, degree: int):
    set_axis(serial_port, constants.CMD_SETYAW, degree)
    
def set_pitch_degree(serial_port: serial.Serial, degree: int):
    value = utils.degrees_to_value(degree)
    set_axis(serial_port, constants.CMD_SETPITCH, value)

def set_roll_degree(serial_port: serial.Serial, degree: int):
    value = utils.degrees_to_value(degree)
    set_axis(serial_port, constants.CMD_SETROLL, value)

def set_yaw_degree(serial_port: serial.Serial, degree: int):
    value = utils.degrees_to_value(degree)
    set_axis(serial_port, constants.CMD_SETYAW, value)

def set_pan_mode(serial_port: serial.Serial, pan_mode: models.PanMode):
    if not isinstance(pan_mode, models.PanMode):
        raise ValueError("Invalid pan mode. Use PanMode enum values.")

    response = utils.send_command(serial_port, constants.CMD_SETPANMODE, [pan_mode.value], 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for SETPANMODE command!")

    logging.info(f"Pan mode set to {pan_mode.name} successfully.")

def set_standby(serial_port: serial.Serial, standby_switch: models.StandBySwitch):
    response = utils.send_command(serial_port, constants.CMD_SETSTANDBY, [standby_switch.value], 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for SETSTANDBY command!")

    logging.info(f"Pan mode set to {standby_switch.name} successfully.")
    
def do_camera(serial_port: serial.Serial, camera_mode: models.DoCameraMode):
    if not isinstance(camera_mode, models.DoCameraMode):
        raise ValueError("Invalid camera mode. Use DoCameraMode enum values.")
    
    response = utils.send_command(serial_port, constants.CMD_DOCAMERA, [0x00, camera_mode, 0x00, 0x00, 0x00, 0x00], 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for DOCAMERA command!")
    
    logging.info(f"Camera set to {do_camera.name} successfully.")
    
def set_script_control(serial_port: serial.Serial, script_control_mode: models.ScriptControlMode):
    if not isinstance(script_control_mode, models.ScriptControlMode):
        raise ValueError("Invalid camera mode. Use DoCameraMode enum values.")
    
    response = utils.send_command(serial_port, constants.CMD_SETSCRIPTCONTROL, [0x00, script_control_mode, 0x00, 0x00, 0x00, 0x00], 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for SETSCRIPTCONTROL command!")
    
    logging.info(f"Script Control set to {do_camera.name} successfully.")
    
def set_angle(serial_port: serial.Serial, pitch_degree: float, roll_degree: float, yaw_degree: float, flags: int):
    if not (0x00 <= flags <= 0xFF):
        raise ValueError("Flags must be a single byte (0x00 - 0xFF).")
    
    pitch_bytes = struct.pack('<f', pitch_degree)
    roll_bytes = struct.pack('<f', roll_degree)
    yaw_bytes = struct.pack('<f', yaw_degree)
    
    response = utils.send_command(serial_port, constants.CMD_SETANGLE, [pitch_bytes, roll_bytes, yaw_bytes, flags, 0x00], 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for SETANGLE command!")
    
    logging.info(f"Set angle command with pitch: {pitch_degree}, roll: {roll_degree}, yaw: {yaw_degree} was successfully.")
    
def set_pitch_roll_yaw(serial_port: serial.Serial, pitch: int, roll: int, yaw: int):
    if (pitch != 0) and not (700 <= pitch <= 2300):
        raise ValueError("Pitch value must be between 0 and 2300.")
    if (pitch != 0) and not (700 <= roll <= 2300):
        raise ValueError("Roll value must be between 0 and 2300.")
    if (pitch != 0) and not (700 <= yaw <= 2300):
        raise ValueError("Yaw value must be between 0 and 2300.")
    
    pitch_data = [pitch & 0xFF, (pitch >> 8) & 0xFF]
    roll_data = [roll & 0xFF, (roll >> 8) & 0xFF]
    yaw_data = [yaw & 0xFF, (yaw >> 8) & 0xFF]

    data = [pitch_data + roll_data + yaw_data]

    response = utils.send_command(serial_port, constants.CMD_SETPITCHROLLYAW, data, 3)
    if response is None:
        raise RuntimeError("Failed to receive acknowledgment for SETPITCHROLLYAW command!")
    
    logging.info(f"Set pitch-roll-yaw command with pitch: {pitch_data}, roll: {roll_data}, yaw: {yaw_data} was successfully.")

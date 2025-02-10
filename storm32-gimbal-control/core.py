import serial
import utils
import constants
import models

def get_version(serial_port: serial.Serial) -> models.VersionResponse:
    header = [constants.STARTSIGNS.INCOMING, 0x00]
    command = [constants.CMD_GETVERSION]
    
    packet = header + command
    
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF
    
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])
    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(11)
    
    if len(response) != 11:
        raise ValueError("Incomplete response received!")
    
    start_sign = response[0]
    packet_length = response[1]
    command = response[2]

    if start_sign != constants.STARTSIGNS.OUTGOING or packet_length != 6 or command != constants.CMD_GETVERSION:
        raise ValueError("Invalid response format!")

    data1 = response[3] | (response[4] << 8)
    data2 = response[5] | (response[6] << 8)
    data3 = response[7] | (response[8] << 8)

    received_crc = response[9] | (response[10] << 8)
    calculated_crc = utils.calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        raise ValueError("CRC mismatch! Data may be corrupted.")

    return models.VersionResponse(firmware_version=data1, hardware_version=data2, protocol_version=data3)

def get_version_str(serial_port: serial.Serial):
    header = [constants.STARTSIGNS.INCOMING, 0x00]
    command = [constants.CMD_GETVERSIONSTR]
    
    packet = header + command
    
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF
    
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])
    serial_port.write(final_packet)
    
    # ------ READ ------
    # (expected length: 3 header bytes + 48 data bytes + 2 CRC bytes = 53)
    response = serial_port.read(53)
    
    if len(response) != 53:
        raise ValueError("Incomplete response received!")
    
    start_sign = response[0]
    packet_length = response[1]
    command = response[2]

    if start_sign != constants.STARTSIGNS.OUTGOING or packet_length != 48 or command != constants.CMD_GETVERSIONSTR:
        raise ValueError("Invalid response format!")

    version_bytes = response[3:19]
    name_bytes = response[19:35]
    board_bytes = response[35:51]
    
    version = version_bytes.decode('utf-8').rstrip('\x00')
    name = name_bytes.decode('utf-8').rstrip('\x00')
    board = board_bytes.decode('utf-8').rstrip('\x00')
    
    received_crc = response[51] | (response[52] << 8)
    calculated_crc = utils.calculate_crc(response[:-2])
    
    if received_crc != calculated_crc:
        raise ValueError("CRC mismatch! Data may be corrupted.")

    return models.VersionStringResponse(version, name, board)

def get_parameter(serial_port: serial.Serial, param_id: int) -> int:
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")
    
    header = [constants.STARTSIGNS.INCOMING, 0x02]
    command = [constants.CMD_GETPARAMETER]
    
    param_low_byte = param_id & 0xFF
    param_high_byte = (param_id >> 8) & 0xFF
    data = [param_low_byte, param_high_byte]
    
    packet = header + command + data
    
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF
    
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])
    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(9)

    if len(response) != 9:
        raise ValueError("Incomplete response received!")

    start_sign = response[0]
    packet_length = response[1]
    command = response[2]

    if start_sign != constants.STARTSIGNS.OUTGOING or packet_length != 4 or command != constants.CMD_GETPARAMETER:
        raise ValueError("Invalid response format!")

    received_param_id = response[3] | (response[4] << 8)  # data1
    param_value = response[5] | (response[6] << 8)  # data2

    if received_param_id != param_id:
        raise ValueError(f"Unexpected parameter ID received: {received_param_id}")

    received_crc = response[7] | (response[8] << 8)
    calculated_crc = utils.calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        raise ValueError("CRC mismatch! Data may be corrupted.")

    return param_value

def set_parameter(serial_port: serial.Serial, param_id: int, param_value: int):
    if not (0 <= param_id <= 65535):
        raise ValueError("Parameter ID must be between 0 and 65535.")
    
    header = [constants.STARTSIGNS.INCOMING, 0x04]
    command = [constants.CMD_SETPARAMETER]
    
    param_low_byte = param_id & 0xFF
    param_high_byte = (param_id >> 8) & 0xFF
    
    param_value_low_byte = param_value & 0xFF
    param_value_high_byte = (param_value >> 8) & 0xFF
    
    data = [param_low_byte, param_high_byte, param_value_low_byte, param_value_high_byte]
    
    packet = header + command + data
    
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF
    
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])
    serial_port.write(final_packet)
    
    response = serial_port.read(3)
    if response[0] == constants.STARTSIGNS.OUTGOING and response[2] == constants.CMD_ACK:
        print("Pitch command acknowledged.")
    else:
        raise ValueError("No acknowledgment received!")
    
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

def set_pitch(serial_port: serial.Serial, degree: int):
    header = [constants.STARTSIGNS.INCOMING, 0x02]
    command = [constants.CMD_SETPITCH]
    
    pitch_value = utils.degrees_to_value(degree)
    data = [pitch_value & 0xFF, (pitch_value >> 8) & 0xFF]

    packet = header + command + data

    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF

    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])

    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(3)
    if response[0] == constants.STARTSIGNS.OUTGOING and response[2] == constants.CMD_ACK:
        print("Pitch command acknowledged.")
    else:
        raise ValueError("No acknowledgment received!")
    

def set_roll(serial_port: serial.Serial, degree: int):
    header = [constants.STARTSIGNS.INCOMING, 0x02]
    command = [constants.CMD_SETROLL]
    
    roll_value = utils.degrees_to_value(degree)
    data = [roll_value & 0xFF, (roll_value >> 8) & 0xFF]

    packet = header + command + data

    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF

    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])

    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(3)
    if response[0] == constants.STARTSIGNS.OUTGOING and response[2] == constants.CMD_ACK:
        print("Pitch command acknowledged.")
    else:
        raise ValueError("No acknowledgment received!")
    
def set_yaw(serial_port: serial.Serial, degree: int):
    header = [constants.STARTSIGNS.INCOMING, 0x02]
    command = [constants.CMD_SETYAW]
    
    yaw_value = utils.degrees_to_value(degree)
    data = [yaw_value & 0xFF, (yaw_value >> 8) & 0xFF]

    packet = header + command + data

    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF

    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])

    serial_port.write(final_packet)
    
    # ------ READ ------
    response = serial_port.read(3)
    if response[0] == constants.STARTSIGNS.OUTGOING and response[2] == constants.CMD_ACK:
        print("Pitch command acknowledged.")
    else:
        raise ValueError("No acknowledgment received!")

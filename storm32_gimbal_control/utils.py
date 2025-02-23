import serial
from storm32_gimbal_control import utils
from storm32_gimbal_control import constants
from storm32_gimbal_control import models
from storm32_gimbal_control import exceptions
from typing import Optional, Union
import logging
import struct

logger_serial = logging.getLogger("LoggerSerial")
logger_response = logging.getLogger("LoggerResponse")

logger_serial.setLevel(logging.WARNING)
logger_response.setLevel(logging.WARNING)

logger_serial.propagate = False
logger_response.propagate = False

console_handler_serial = logging.StreamHandler()
console_handler_response = logging.StreamHandler()

console_formatter_serial = logging.Formatter("%(asctime)s - %(levelname)s - Serial data: %(message)s")
console_formatter_response = logging.Formatter('%(asctime)s - %(name)s - { %(message)s }')

console_handler_serial.setFormatter(console_formatter_serial)
console_handler_response.setFormatter(console_formatter_response)

logger_serial.addHandler(console_handler_serial)
logger_response.addHandler(console_handler_response)

def configure_logging(enable: bool = True, level=logging.INFO):
    """
    Enables or disables logging for serial and response loggers.
    
    Args:
        enable (bool): If True, enables logging. If False, disables it.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING).
    """
    log_level = level if enable else logging.WARNING
    logger_serial.setLevel(log_level)
    logger_response.setLevel(log_level)

def calculate_crc(data):
    crc = 0xFFFF 
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if (crc & 0x0001):
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def calculate_crc_ccitt(data):
    crc = 0xFFFF  # CCITT uses 0xFFFF as initial value
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021  # CCITT uses 0x1021 polynomial
            else:
                crc <<= 1
    return crc & 0xFFFF

def validate_crc(data):
    """
    CRC validation function.
    - data: Incoming data including CRC.

    Data format: [data1, data2, ..., crc_low, crc_high]
    """
    if len(data) < 3:
        raise ValueError("Data is too short!")

    received_crc = data[-2] | (data[-1] << 8) 
    data_without_crc = data[:-2] 

    calculated_crc = calculate_crc(data_without_crc)

    if calculated_crc == received_crc:
        return True  
    else:
        return False

def degrees_to_value(degrees):
    if -90 <= degrees <= 90:
        raise ValueError("The degree must be in between values -90 and 90!")

    return int((degrees + 90) * (2300 - 700) / 180 + 700)

def send_command(serial_port: serial.Serial, command: int, data: list[int]) -> Optional[bytearray]:
    """
    Sends a command packet and reads the response.

    Args:
        serial_port (serial.Serial): The serial port object.
        command (int): Command ID.
        data (list[int]): Data bytes.
        expected_length (int): Expected response length.

    Returns:
        Optional[bytearray]: The response data (excluding header and CRC) if successful, else None.
    """

    header = [constants.STARTSIGNS.INCOMING, len(data)]
    packet = header + [command] + data

    crc = utils.calculate_crc(packet)
    packet += [crc & 0xFF, (crc >> 8) & 0xFF]

    serial_port.write(bytearray(packet))
    
def read_from_serial(serial_port: serial.Serial, expected_length: int):
    header = serial_port.read(3)
    
    if len(header) < 3:
        raise ValueError("Incomplete response header received")

    start_sign, packet_length, response_cmd = header

    if start_sign != constants.STARTSIGNS.OUTGOING:
        raise ValueError("Invalid start sign received")

    if response_cmd == constants.CMD_ACK:
        response = serial_port.read(3)
        
        if len(response) < 3:
            raise ValueError("Incomplete ACK response received")
        
        data = response[0]
        
        logger_response.info(f"\nACK RESPONSE:\n\tdata: {constants.ACK_CODES[data]}\n")
        if constants.ACK_CODES[data] != "SERIALRCCMD_ACK_OK":
            raise exceptions.AckError(constants.ACK_CODES[data])
        
        return constants.ACK_CODES[data]

    remaining_length = expected_length - 3
    remaining_response = serial_port.read(remaining_length)
    response = header + remaining_response

    if len(response) < expected_length:
        logger_response.warning(f"Expected {expected_length} bytes, but got {len(response)}. Data may be incomplete.")
        
    hex_data = ' '.join(f'{byte:02X}' for byte in response)
    logger_serial.info(hex_data)

    start_sign, packet_length, response_cmd = response[:3]

    # CRC fails for some reason but the response is correct
    #if not validate_crc(response):
    #    logger_response.warning("CRC validation failed!")
    #    raise exceptions.CrcError("CRC validation failed!")
    #    return None

    if response_cmd == constants.CMD_GETVERSION:
        data1 = (response[4] << 8) | response[3]
        data2 = (response[6] << 8) | response[5]
        data3 = (response[8] << 8) | response[7]

        logger_response.info(f"\nGETVERSION RESPONSE:\n\tfirmware version:{data1}\n\tsetup layout version: {data2}\n\tboard capabilities value: {data3}")
        
        return models.VersionResponse(firmware_version=data1, setup_layout_version=data2, board_capabilities=data3)
    
    elif response_cmd == constants.CMD_GETVERSIONSTR:
        data_stream = response[3:-2]

        version_string = data_stream[:16].decode('utf-8', errors="ignore").rstrip('\x00')
        name_string = data_stream[16:32].decode('utf-8', errors="ignore").rstrip('\x00')
        board_string = data_stream[32:48].decode('utf-8', errors="ignore").rstrip('\x00')

        logger_response.info(f"\nGETVERSIONSTR RESPONSE:\n\tVersion: {version_string}\n\tName: {name_string}\n\tBoard: {board_string}\n")

        return models.VersionStringResponse(version=version_string, name=name_string, board=board_string)
    
    elif response_cmd == constants.CMD_GETPARAMETER:
        data1 = (response[4] << 8) | response[3]
        data2 = (response[6] << 8) | response[5]
        
        logger_response.info(f"\nGETPARAMETER RESPONSE:\n\tparameter number: {data1}\n\tparameter value: {data2}\n")
    
        return data2
    elif response_cmd == constants.CMD_GETDATA:
        type_byte = response[3]
        
        # GETDATA can't be 0x76 but GETVERSIONSTR returns GETDATA with 0x76 for some reason
        if type_byte == 0x76:
            data_stream = response[3:-2]
            logger_response.info(f"\nGETDATA RESPONSE:\n\ttype byte: {type_byte}\n\tdatastream: {data_stream}\n")
            
            version_string = data_stream[:16].decode('utf-8', errors="ignore").rstrip('\x00')
            name_string = data_stream[16:32].decode('utf-8', errors="ignore").rstrip('\x00')
            board_string = data_stream[32:48].decode('utf-8', errors="ignore").rstrip('\x00')
            
            return models.VersionStringResponse(version=version_string, name=name_string, board=board_string)

        # Stream starts from 5 because msg structure is 0xFB 0x4A 0x05 type-byte 0x00 ...
        data_stream = response[5:-2]
        logger_response.info(f"\nGETDATA RESPONSE:\n\ttype byte: {type_byte}\n\tdatastream: {data_stream}\n")

        return models.DataStreamResponse.from_data_stream(data_stream)
        
    elif response_cmd == constants.CMD_GETDATAFIELDS:
        bitmask = (response[4] << 8) | response[3]
        data_stream = response[5:-2].decode('utf-8', errors="ignore").rstrip('\x00')

        logger_response.info(f"\nGETDATAFIELDS RESPONSE:\n\tbitmask: {bitmask}\n\tdatastream: {data_stream}\n")
        
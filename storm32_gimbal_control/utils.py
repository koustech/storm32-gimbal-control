import serial
from storm32_gimbal_control import utils
from storm32_gimbal_control import constants
from storm32_gimbal_control import models
import logging
from typing import Optional, Union

logger_serial = logging.getLogger("LoggerSerial")
logger_serial.setLevel(logging.INFO)
logger_serial.propagate = False

console_handler_serial = logging.StreamHandler()
console_formatter_serial = logging.Formatter("%(asctime)s - %(levelname)s - Serial data: %(message)s")
console_handler_serial.setFormatter(console_formatter_serial)

logger_serial.addHandler(console_handler_serial)

logger_response = logging.getLogger("LoggerResponse")
logger_response.setLevel(logging.INFO)
logger_response.propagate = False

console_handler_response = logging.StreamHandler()
console_formatter_response = logging.Formatter('%(asctime)s - %(name)s - { %(message)s }')
console_handler_response.setFormatter(console_formatter_response)

logger_response.addHandler(console_handler_response)

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

def degrees_to_value(degrees):
    if -90 <= degrees <= 90:
        raise ValueError("The degree must be in between values -90 and 90!")

    return int((degrees + 90) * (2300 - 700) / 180 + 700)

def send_command(serial_port: serial.Serial, command: int, data: list[int], expected_length: int) -> Optional[bytearray]:
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
    """
    if response_cmd == constants.CMD_ACK:
        ack_code = response[3]
        ack_message = constants.ACK_CODES.get(ack_code, f"Unknown ACK Code {ack_code}")

        if ack_code == 0:
            logging.info(f"ACK Received: {ack_message}")
            return response[3:-2]  # Return response without header & CRC
        else:
            logging.error(f"ACK Error: {ack_message}")
            return None

    received_crc = response[-2] | (response[-1] << 8)
    calculated_crc = utils.calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        logging.error("CRC mismatch! Data may be corrupted.")
        return None

    return response[3:-2]
    """
    
def read_from_serial(serial_port: serial.Serial):
    while True:
        response = serial_port.readline()
        
        if response:
            hex_data = ' '.join(f'{byte:02X}' for byte in response)
            logger_serial.info(hex_data)

            start_sign, packet_length, response_cmd = response[:3]

            if start_sign == constants.STARTSIGNS.OUTGOING:
                if response_cmd == constants.CMD_GETVERSION:
                    data1 = (response[4] << 8) | response[3]
                    data2 = (response[6] << 8) | response[5]
                    data3 = (response[8] << 8) | response[7]

                    logger_response.info(f"\nGETVERSION RESPONSE:\n\tfirmware version:{data1}\n\tsetup layout version: {data2}\n\tboard capabilities value: {data3}")
                
                elif response_cmd == constants.CMD_GETVERSIONSTR:
                    data_stream = response[3:-2]

                    version_string = data_stream[:16].decode('utf-8', errors="ignore").rstrip('\x00')
                    name_string = data_stream[16:32].decode('utf-8', errors="ignore").rstrip('\x00')
                    board_string = data_stream[32:48].decode('utf-8', errors="ignore").rstrip('\x00')

                    logger_response.info(f"\nGETVERSIONSTR RESPONSE:\n\tVersion: {version_string}\n\tName: {name_string}\n\tBoard: {board_string}\n")

                elif response_cmd == constants.CMD_GETPARAMETER:
                    data1 = (response[4] << 8) | response[3]
                    data2 = (response[6] << 8) | response[5]
                    
                    logger_response.info(f"\nGETPARAMETER RESPONSE:\n\tparameter number: {data1}\n\tparameter value: {data2}\n")
                
                elif response_cmd == constants.CMD_GETDATA:
                    type_byte = response[3]
                    data_stream = response[5:-2].decode('utf-8', errors="ignore").rstrip('\x00')
                    
                    logger_response.info(f"\nGETDATA RESPONSE:\n\ttype byte: {type_byte}\n\tdatastream: {data_stream}\n")
                    
                elif response_cmd == constants.CMD_GETDATAFIELDS:
                    bitmask = (response[4] << 8) | response[3]
                    data_stream = response[5:-2].decode('utf-8', errors="ignore").rstrip('\x00')

                    logger_response.info(f"\nGETDATAFIELDS RESPONSE:\n\tbitmask: {bitmask}\n\tdatastream: {data_stream}\n")
                
                elif response_cmd == constants.CMD_ACK:
                    data = response[3]
                    
                    logger_response.info(f"\nACK RESPONSE:\n\tdata: {constants.ACK_CODES[data]}\n")
                    
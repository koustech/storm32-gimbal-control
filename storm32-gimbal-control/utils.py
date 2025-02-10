import serial
import utils
import constants
import models
import logging
from typing import Optional, Union

logging.basicConfig(level=logging.INFO)

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

    response = serial_port.read(expected_length)

    if len(response) != expected_length:
        logging.error(f"Incomplete response! Expected {expected_length}, got {len(response)}")
        return None

    start_sign, packet_length, response_cmd = response[:3]
    if start_sign != constants.STARTSIGNS.OUTGOING or response_cmd != command:
        logging.error("Invalid response format!")
        return None

    received_crc = response[-2] | (response[-1] << 8)
    calculated_crc = utils.calculate_crc(response[:-2])

    if received_crc != calculated_crc:
        logging.error("CRC mismatch! Data may be corrupted.")
        return None

    return response[3:-2]
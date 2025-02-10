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

# Genel bir ayar fonksiyonu (Pitch, Roll, Yaw için kullanılabilir)
def set_axis(serial_port, degrees, command_id):
    # Dereceyi uint16_t değere dönüştür
    value = utils.degrees_to_value(degrees)

    # CMD_SET Komut Yapısı
    header = [0xFA, 0x02]  # Header: 0xFA 0x02
    command = [command_id]  # Command ID: CMD_SETPITCH (#10), CMD_SETROLL (#11), CMD_SETYAW (#12)

    # Data (uint16_t, low-byte ve high-byte)
    data_low_byte = value & 0xFF  # En düşük 8 bit
    data_high_byte = (value >> 8) & 0xFF  # En yüksek 8 bit
    data = [data_low_byte, data_high_byte]

    # CRC Hesaplama
    packet = header + command + data
    crc = utils.calculate_crc(packet)
    crc_low_byte = crc & 0xFF
    crc_high_byte = (crc >> 8) & 0xFF

    # Final Paket
    final_packet = bytearray(packet + [crc_low_byte, crc_high_byte])

    # Paket Gönderimi
    serial_port.write(final_packet)  # Seri port üzerinden veriyi gönder
    print(f"Gönderilen Paket (Hex): {final_packet.hex()} - Value: {value}")

# Roll Ayarlama Fonksiyonu
def set_roll(serial_port, degrees):
    set_axis(serial_port, degrees, 0x0B)

# Pitch Ayarlama Fonksiyonu
def set_pitch(serial_port, degrees):
    set_axis(serial_port, degrees, 0x0A)

# Yaw Ayarlama Fonksiyonu
def set_yaw(serial_port, degrees):
    set_axis(serial_port, degrees, 0x0C)

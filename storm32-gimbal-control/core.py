import serial

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

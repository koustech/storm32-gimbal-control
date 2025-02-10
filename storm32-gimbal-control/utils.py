
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

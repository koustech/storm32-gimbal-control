import serial
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core

def scan_area(serial_port, yaw_range, pitch_range, step_yaw, step_pitch, roll_angle=0):
    """
    Gimbal ile kapsamlı bir alan tarama algoritması.
    
    Args:
        serial_port: Seri port bağlantı objesi.
        yaw_range: Yaw ekseni için (-90, 90) aralığında bir tuple (min, max).
        pitch_range: Pitch ekseni için (-90, 90) aralığında bir tuple (min, max).
        step_yaw: Yaw ekseni için adım açısı (derece).
        step_pitch: Pitch ekseni için adım açısı (derece).
        roll_angle: Roll ekseni sabit bir açıda tutulacaksa değeri (derece).
    """
    yaw_min, yaw_max = yaw_range
    pitch_min, pitch_max = pitch_range

    core.set_roll(serial_port, roll_angle)
    time.sleep(0.5)

    for yaw_angle in range(yaw_min, yaw_max + 1, step_yaw):
        for pitch_angle in range(pitch_min, pitch_max + 1, step_pitch):
            core.set_yaw(serial_port, yaw_angle)
            core.set_pitch(serial_port, pitch_angle)
            print(f"Yaw: {yaw_angle}, Pitch: {pitch_angle}, Roll: {roll_angle}")
            time.sleep(0.5)

        pitch_min, pitch_max = pitch_max, pitch_min

    core.set_yaw(serial_port, 0)
    core.set_pitch(serial_port, 0)
    core.set_roll(serial_port, 0)
    print("Tarama tamamlandı, gimbal sıfırlandı.")

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print("Seri port açıldı: /dev/ttyACM0")

    yaw_range = (-90, 90)
    pitch_range = (-45, 45)
    step_yaw = 15
    step_pitch = 15
    roll_angle = 0

    scan_area(ser, yaw_range, pitch_range, step_yaw, step_pitch, roll_angle)
except Exception as e:
    print(f"Hata: {e}")
finally:
    ser.close()

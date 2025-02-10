import serial
from gimbal_control import set_roll, set_pitch, set_yaw
import time

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

    # Roll eksenini sabit bir açıya ayarla
    set_roll(serial_port, roll_angle)
    time.sleep(0.5)

    # Yaw ve pitch ekseninde sistematik tarama
    for yaw_angle in range(yaw_min, yaw_max + 1, step_yaw):  # Yaw ekseni boyunca hareket et
        for pitch_angle in range(pitch_min, pitch_max + 1, step_pitch):  # Pitch ekseni boyunca hareket et
            set_yaw(serial_port, yaw_angle)
            set_pitch(serial_port, pitch_angle)
            print(f"Yaw: {yaw_angle}, Pitch: {pitch_angle}, Roll: {roll_angle}")
            time.sleep(0.5)  # Hareketin tamamlanması için kısa bir bekleme
        # Her Yaw adımında Pitch'in yönünü tersine çevir (zigzag tarama için)
        pitch_min, pitch_max = pitch_max, pitch_min

    # Gimbalı başlangıç pozisyonuna döndür
    set_yaw(serial_port, 0)
    set_pitch(serial_port, 0)
    set_roll(serial_port, 0)
    print("Tarama tamamlandı, gimbal sıfırlandı.")

# Seri Port Bağlantısı ve Tarama
try:
    ser = serial.Serial('COM3', 115200, timeout=1)  # COM3 portu üzerinden bağlantı
    print("Seri port açıldı: COM3")

    # Alan tarama parametreleri
    yaw_range = (-90, 90)  # Yaw ekseni tarama aralığı
    pitch_range = (-45, 45)  # Pitch ekseni tarama aralığı
    step_yaw = 15  # Yaw ekseni için adım açısı
    step_pitch = 15  # Pitch ekseni için adım açısı
    roll_angle = 0  # Roll ekseni sabit (0 derece)

    # Alan taramasını başlat
    scan_area(ser, yaw_range, pitch_range, step_yaw, step_pitch, roll_angle)
except Exception as e:
    print(f"Hata: {e}")
finally:
    ser.close()  # Seri portu kapat

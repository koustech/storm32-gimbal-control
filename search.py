import serial
from gimbal_control import set_roll, set_pitch, set_yaw

# Seri Port Bağlantısı
try:
    ser = serial.Serial('COM3', 115200, timeout=1)  # COM3 portu üzerinden bağlantı
    print("Seri port açıldı: COM3")

    # Derece cinsinden roll, pitch ve yaw değerleri
    roll_degrees = 0  # Roll için derece değeri
    pitch_degrees = 0 # Pitch için derece değeri
    yaw_degrees = 0 # Yaw için derece değeri

    # Roll, Pitch ve Yaw ayarla
    set_roll(ser, roll_degrees)    # Roll ayarla
    set_pitch(ser, pitch_degrees)  # Pitch ayarla
    set_yaw(ser, yaw_degrees)      # Yaw ayarla
except Exception as e:
    print(f"Hata: {e}")
finally:
    ser.close()  # Seri portu kapat

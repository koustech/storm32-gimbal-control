import os
import sys
import serial
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import utils

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=0.02)

utils.configure_logging(True)

start_time = time.time()

while True:
    elapsed_time = time.time() - start_time
    data = core.get_data(serial_port, 0)
    
    print(f"\nTime Elapsed: {elapsed_time:.2f} seconds")
    print(data)
    print(f"IMU2 Yaw: {data.imu2_yaw}")
    print(f"IMU2 Roll: {data.imu2_roll}")
    print(f"IMU2 Pitch: {data.imu2_pitch}")


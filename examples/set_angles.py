import os
import sys
import serial
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import models
from storm32_gimbal_control import utils

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

utils.configure_logging(True)

print(core.set_yaw(serial_port, 0))
print(core.set_pitch(serial_port, 0))
print(core.set_roll(serial_port, 0))

flags = models.SetAngleFlags.from_axes(pitch=True, roll=True, yaw=True)
#print(core.set_angle(serial_port, -60, -45, -90, flags))
#print(core.set_angle(serial_port, 60, 45, 90, flags))
print(core.set_angle(serial_port, 0, 0, 0, flags))

#core.set_pitch_roll_yaw(serial_port, 0, 0, 0)

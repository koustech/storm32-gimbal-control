import os
import sys
import serial
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import utils

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

print(core.get_version(serial_port))
print(core.get_version_str(serial_port))

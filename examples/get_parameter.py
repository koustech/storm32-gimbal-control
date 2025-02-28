import os
import sys
import serial
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import utils

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

core.get_parameter(serial_port, 1)
core.get_parameter(serial_port, 2)
core.get_parameter(serial_port, 3)

core.set_parameter(serial_port, 1, 1500)
core.get_parameter(serial_port, 1)
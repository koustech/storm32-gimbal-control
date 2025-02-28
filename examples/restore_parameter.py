import os
import sys
import serial

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import models

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

core.restore_parameter(serial_port, 1)

core.restore_all_parameters(serial_port)

import os
import sys
import serial
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import utils
from storm32_gimbal_control import models

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

utils.configure_logging(True)
print(core.get_data_fields(serial_port, models.LiveDataFields.STATUS))

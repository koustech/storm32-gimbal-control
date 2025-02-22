import os
import sys
import serial
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import utils
from storm32_gimbal_control import constants

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

thread = threading.Thread(target=utils.read_from_serial, args=(serial_port,))
thread.start()

core.get_data_fields(serial_port, constants.BITMASKS.LIVEDATA_STATUS)

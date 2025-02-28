import os
import sys
import serial

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from storm32_gimbal_control import core
from storm32_gimbal_control import models

serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

core.active_pan_mode_setting(serial_port, models.PanModeSetting.SETTING_1)

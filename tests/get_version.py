import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your actual module
from storm32_gimbal_control import core

class TestGetData(unittest.TestCase):
    @patch("storm32_gimbal_control.utils.serial.Serial")
    def test_get_data(self, mock_serial_class):
        """Test get_data function with mocked serial response"""

        # Create a mock serial instance
        mock_serial_instance = MagicMock()
        mock_serial_class.return_value = mock_serial_instance

        # Mock side_effect to return chunks of data as if read from serial
        mock_serial_instance.read.side_effect = [
            bytes([0xFB, 0x42, 0x05]),  # First part (header)
            bytes([0x00, 0x00, 0x06, 0x00]),  # State, status
            bytes([0x70, 0x98, 0x00, 0x80]),  # status2
            bytes([0x00, 0x00, 0x00, 0x00]),  # i2c_errors, lipo_voltage
            bytes([0xB3, 0x1E, 0xDC, 0x05]),  # timestamp, cycle_time
            bytes([0x61, 0x00, 0x0A, 0x00]),  # imu1_gyro
            bytes([0xF8, 0xFF, 0x41, 0x0C]),  # imu1_acc
            bytes([0x3F, 0xFD, 0x48, 0x1A]),  # imu1_acc
            bytes([0xEF, 0x10, 0x42, 0xFC]),  # imu1_rotation
            bytes([0xFB, 0x22, 0xE7, 0xF5]),  # imu1_pitch, roll, yaw
            bytes([0xDF, 0xFD, 0xC2, 0xFF]),  # pid values
            bytes([0x19, 0x0A, 0x21, 0x02]),  # pid_pitch, roll
            bytes([0x3E, 0x00, 0x00, 0x00]),  # pid_yaw, input_pitch
            bytes([0x00, 0x00, 0x00, 0x00]),  # input_roll, yaw
            bytes([0x48, 0x04, 0xBF, 0xFC]),  # imu2_pitch, roll
            bytes([0x6E, 0xFF, 0x00, 0x00]),  # imu2_yaw, mag_yaw
            bytes([0x3E, 0x03, 0xD3, 0x35]),  # mag_pitch, imu_acc_confidence
            bytes([0x00, 0x00, 0x7C, 0x50]),  # extra_function_input, checksum
        ]

        # Call function
        data = core.get_data(mock_serial_instance)

        # Assertions
        self.assertEqual(data.state, 6)
        self.assertEqual(data.status, -26512)
        self.assertEqual(data.status2, -32768)
        self.assertEqual(data.i2c_errors, 0)
        self.assertEqual(data.lipo_voltage, 0)
        self.assertEqual(data.timestamp, 7859)  # Corrected
        self.assertEqual(data.cycle_time, 1500)
        self.assertEqual(data.imu1_gyro, (97, 10, -8))
        self.assertEqual(data.imu1_acc, (3137, -705, 6728))
        self.assertEqual(data.imu1_rotation, (4335, -958, 8955))
        self.assertEqual(data.imu1_pitch, -25.85)
        self.assertEqual(data.imu1_roll, -5.45)
        self.assertEqual(data.imu1_yaw, -0.62)
        self.assertEqual(data.pid_pitch, 25.85)
        self.assertEqual(data.pid_roll, 5.45)
        self.assertEqual(data.pid_yaw, 0.62)
        self.assertEqual(data.input_pitch, 0)
        self.assertEqual(data.input_roll, 0)
        self.assertEqual(data.input_yaw, 0)
        self.assertEqual(data.imu2_pitch, 10.96)
        self.assertEqual(data.imu2_roll, -8.33)
        self.assertEqual(data.imu2_yaw, -1.46)
        self.assertEqual(data.mag_yaw, 0.0)
        self.assertEqual(data.mag_pitch, 8.3)
        self.assertAlmostEqual(data.imu_acc_confidence, 1.3779, places=4)
        self.assertEqual(data.extra_function_input, 0)

if __name__ == "__main__":
    unittest.main()

"""Unit tests for esp32_light_control module."""

import argparse
import pytest
from unittest.mock import MagicMock, patch, call
import esp32_light_control as elc


class TestRangedInt:
    """Tests for ranged_int validation function."""

    def test_valid_value(self):
        """Test valid integer within range."""
        assert elc.ranged_int("50", 0, 100, "test") == 50

    def test_boundary_min(self):
        """Test minimum boundary value."""
        assert elc.ranged_int("0", 0, 100, "test") == 0

    def test_boundary_max(self):
        """Test maximum boundary value."""
        assert elc.ranged_int("100", 0, 100, "test") == 100

    def test_below_minimum(self):
        """Test value below minimum raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            elc.ranged_int("-1", 0, 100, "test")

    def test_above_maximum(self):
        """Test value above maximum raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            elc.ranged_int("101", 0, 100, "test")

    def test_non_integer(self):
        """Test non-integer value raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            elc.ranged_int("abc", 0, 100, "test")


class TestRGBValue:
    """Tests for RGB value validation."""

    def test_valid_rgb(self):
        """Test valid RGB values."""
        assert elc.rgb_value("0") == 0
        assert elc.rgb_value("128") == 128
        assert elc.rgb_value("255") == 255

    def test_invalid_rgb(self):
        """Test invalid RGB values."""
        with pytest.raises(argparse.ArgumentTypeError):
            elc.rgb_value("256")


class TestBuzzerFrequency:
    """Tests for buzzer frequency validation."""

    def test_valid_frequency(self):
        """Test valid buzzer frequencies."""
        assert elc.buzzer_frequency("20") == 20
        assert elc.buzzer_frequency("2000") == 2000
        assert elc.buzzer_frequency("20000") == 20000

    def test_invalid_frequency(self):
        """Test invalid buzzer frequencies."""
        with pytest.raises(argparse.ArgumentTypeError):
            elc.buzzer_frequency("10")


class TestCommandText:
    """Tests for command text generation."""

    def test_simple_command(self):
        """Test simple command generation."""
        args = argparse.Namespace(command="off")
        assert elc.command_text(args) == "off"

    def test_solid_command(self):
        """Test solid RGB command generation."""
        args = argparse.Namespace(command="solid", r=255, g=128, b=0)
        assert elc.command_text(args) == "solid 255 128 0"

    def test_beep_command(self):
        """Test beep command generation."""
        args = argparse.Namespace(command="beep", frequency_hz=2000, duration_ms=200)
        assert elc.command_text(args) == "beep 2000 200"

    def test_tone_command_with_duty(self):
        """Test tone command with duty cycle."""
        args = argparse.Namespace(command="tone", frequency_hz=1000, duty_percent=50)
        assert elc.command_text(args) == "tone 1000 50"

    def test_tone_command_without_duty(self):
        """Test tone command without duty cycle."""
        args = argparse.Namespace(command="tone", frequency_hz=1000, duty_percent=None)
        assert elc.command_text(args) == "tone 1000"

    def test_vibrate_command(self):
        """Test vibrate command generation."""
        args = argparse.Namespace(command="vibrate", duration_ms=500)
        assert elc.command_text(args) == "vibrate 500"

    def test_raw_command(self):
        """Test raw command generation."""
        args = argparse.Namespace(command="raw", text=["custom", "command"])
        assert elc.command_text(args) == "custom command"


class TestPortScoring:
    """Tests for serial port scoring."""

    def test_score_esp32_port(self):
        """Test scoring of ESP32-like port."""
        port = MagicMock()
        port.device = "/dev/cu.usbserial-0001"
        port.description = "USB Serial Device"
        port.manufacturer = "Silicon Labs"
        port.hwid = "USB VID:PID=10C4:EA60"
        score = elc.score_serial_port(port)
        assert score > 0

    def test_ignore_bluetooth_port(self):
        """Test that Bluetooth ports are ignored."""
        port = MagicMock()
        port.device = "/dev/cu.Bluetooth-Incoming-Port"
        port.description = "Bluetooth"
        port.manufacturer = ""
        port.hwid = ""
        assert elc.port_is_ignored(port)

    def test_ignore_debug_console(self):
        """Test that debug console ports are ignored."""
        port = MagicMock()
        port.device = "/dev/cu.debug-console"
        port.description = "Debug Console"
        port.manufacturer = ""
        port.hwid = ""
        assert elc.port_is_ignored(port)


class TestSerialConnection:
    """Tests for serial connection operations."""

    def test_send_command_with_response(self, mock_pyserial_available, mock_serial_connection):
        """Test sending command and reading response."""
        mock_serial_connection.in_waiting = 14
        mock_serial_connection.read = MagicMock(return_value=b"ESP32_LIGHT_OK")

        elc.send_command(mock_serial_connection, "off", read_response=True, quiet=True)

        mock_serial_connection.write.assert_called_once_with(b"off\n")
        mock_serial_connection.flush.assert_called_once()
        mock_serial_connection.read.assert_called_once()

    def test_send_command_without_response(self, mock_pyserial_available, mock_serial_connection):
        """Test sending command without reading response."""
        elc.send_command(mock_serial_connection, "off", read_response=False, quiet=True)

        mock_serial_connection.write.assert_called_once_with(b"off\n")
        mock_serial_connection.flush.assert_called_once()
        mock_serial_connection.read.assert_not_called()

    def test_send_empty_command(self, mock_pyserial_available, mock_serial_connection):
        """Test that empty commands are not sent."""
        elc.send_command(mock_serial_connection, "   ", read_response=False, quiet=True)

        mock_serial_connection.write.assert_not_called()

    def test_send_command_strips_whitespace(self, mock_pyserial_available, mock_serial_connection):
        """Test that command text is stripped of whitespace."""
        elc.send_command(mock_serial_connection, "  off  \n", read_response=False, quiet=True)

        mock_serial_connection.write.assert_called_once_with(b"off\n")


class TestCacheOperations:
    """Tests for port caching operations."""

    def test_cache_path(self):
        """Test cache path generation."""
        path = elc.cache_path()
        assert "light_port" in path
        assert path.endswith("light_port")

    @patch("builtins.open", create=True)
    @patch("os.path.exists")
    def test_read_cached_port_exists(self, mock_exists, mock_open):
        """Test reading cached port when file exists."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "/dev/cu.usbserial-0001\n"

        port = elc.read_cached_port()

        assert port == "/dev/cu.usbserial-0001"

    @patch("builtins.open", side_effect=OSError)
    def test_read_cached_port_not_found(self, mock_open):
        """Test reading cached port when file doesn't exist."""
        port = elc.read_cached_port()
        assert port is None

    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    def test_write_cached_port(self, mock_makedirs, mock_open):
        """Test writing cached port."""
        elc.write_cached_port("/dev/cu.usbserial-0001")

        mock_open.assert_called_once()
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with("/dev/cu.usbserial-0001\n")


class TestArgumentParser:
    """Tests for argument parser."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = elc.build_parser()
        assert parser is not None

    def test_parse_solid_command(self):
        """Test parsing solid RGB command."""
        parser = elc.build_parser()
        args = parser.parse_args(["solid", "255", "128", "0"])
        assert args.command == "solid"
        assert args.r == 255
        assert args.g == 128
        assert args.b == 0

    def test_parse_beep_command(self):
        """Test parsing beep command."""
        parser = elc.build_parser()
        args = parser.parse_args(["beep", "2000", "300"])
        assert args.command == "beep"
        assert args.frequency_hz == 2000
        assert args.duration_ms == 300

    def test_parse_with_port(self):
        """Test parsing with port argument."""
        parser = elc.build_parser()
        args = parser.parse_args(["-p", "/dev/cu.usbserial-0001", "off"])
        assert args.port == "/dev/cu.usbserial-0001"
        assert args.command == "off"

    def test_parse_with_baud(self):
        """Test parsing with baud rate."""
        parser = elc.build_parser()
        args = parser.parse_args(["-b", "9600", "off"])
        assert args.baud == 9600


class TestListPorts:
    """Tests for list ports functionality."""

    @patch("esp32_light_control.serial")
    @patch("esp32_light_control.list_ports")
    @patch("builtins.print")
    def test_list_serial_ports(self, mock_print, mock_list_ports_module, mock_serial):
        """Test listing serial ports."""
        mock_serial.Serial = MagicMock()
        mock_port = MagicMock()
        mock_port.device = "/dev/cu.usbserial-0001"
        mock_port.description = "USB Serial Device"
        mock_list_ports_module.comports.return_value = [mock_port]

        elc.list_serial_ports()

        mock_print.assert_called()

    @patch("esp32_light_control.serial")
    @patch("esp32_light_control.list_ports")
    @patch("builtins.print")
    def test_list_ports_empty(self, mock_print, mock_list_ports_module, mock_serial):
        """Test listing when no ports available."""
        mock_serial.Serial = MagicMock()
        mock_list_ports_module.comports.return_value = []

        elc.list_serial_ports()

        mock_print.assert_called_with("No serial ports found.")

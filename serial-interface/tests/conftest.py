"""Pytest fixtures and mocks for serial-interface tests."""

from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_serial_connection():
    """Create a mock serial connection."""
    mock_conn = MagicMock()
    mock_conn.write = MagicMock(return_value=10)
    mock_conn.read = MagicMock(return_value=b"ESP32_LIGHT_OK\n")
    mock_conn.flush = MagicMock()
    mock_conn.reset_input_buffer = MagicMock()
    mock_conn.in_waiting = 0
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    return mock_conn


@pytest.fixture
def mock_serial_module(mock_serial_connection):
    """Mock the serial module."""
    with patch("esp32_light_control.serial") as mock_serial:
        mock_serial.Serial = MagicMock(return_value=mock_serial_connection)
        mock_serial.SerialException = Exception
        yield mock_serial


@pytest.fixture
def mock_list_ports():
    """Mock the list_ports module."""
    with patch("esp32_light_control.list_ports") as mock_ports:
        mock_port = MagicMock()
        mock_port.device = "/dev/cu.usbserial-0001"
        mock_port.description = "USB Serial Device"
        mock_port.manufacturer = "Silicon Labs"
        mock_port.hwid = "USB VID:PID=10C4:EA60"
        mock_ports.comports = MagicMock(return_value=[mock_port])
        yield mock_ports


@pytest.fixture
def mock_pyserial_available(mock_serial_module, mock_list_ports):
    """Fixture to ensure pyserial is available."""
    yield

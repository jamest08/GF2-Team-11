"""Test the parse module."""
import pytest
import sys
import os

from scanner import Scanner
from scanner import Symbol
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from parse import Parser


@pytest.fixture
def parser():
    """Return an instance of a scanner using."""
    print("\nNow opening file...")

    #  Print the path provided and try to open the file for reading
    cwd = os.getcwd()

    file_list = ["example1.txt", "example1_with_syntax_errors.txt",
                 "error2.txt", "error1.txt", "example4.txt", "example4_with_syntax_errors.txt"]
    parser_list = []
    for item in file_list:
        if '/' in cwd:
            path = cwd + '/' + item
        else:
            path = cwd + '\\' + item

        names = Names()
        scanner = Scanner(path, names)
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        parse = Parser(names, devices, network, monitors, scanner)
        parse.parse_network()
        parser_list.append(parse)

    return parser_list


def test_get_error_amount(parser):
    """Test if parser detects expected number of errors."""

    assert parser[0].scanner.error_count == 0
    assert parser[1].scanner.error_count == 2
    assert parser[2].scanner.error_count > 0
    assert parser[4].scanner.error_count == 0


def test_error_type(parser):
    "Test parser is returning correct errors messages."
    assert parser[0].scanner.error_message_list == []
    assert parser[1].scanner.error_message_list == ["Invalid symbol for start of line.",
                                                    "The following inputs are floating: ['G1.I1']"]
    assert ("Expected 0 or 1 for switch state" and
            "Number of inputs must be integer in range(1, 17)" and
            "Unexpected dot. Can only specify port for DTYPE."
            in parser[3].scanner.error_message_list)
    assert 'Invalid name, may be keyword' in parser[3].scanner.error_message_list
    assert "Expected 0 or 1 or keyword 'waveform'" in parser[5].scanner.error_message_list


def test_devices(parser):
    """Test parser has created expected devices."""

    names = parser[0].names
    devices = parser[0].devices
    device_ids = parser[0].devices.find_devices()

    expected_dev = ["NAND", "NAND", "SWITCH", "SWITCH"]
    dev = []
    for device_id in device_ids:
        dev.append(names.get_name_string(devices.get_device(device_id).device_kind))
    assert dev == expected_dev

    names = parser[1].names
    devices = parser[1].devices
    device_ids = parser[1].devices.find_devices()

    dev = []
    for device_id in device_ids:
        dev.append(names.get_name_string(devices.get_device(device_id).device_kind))
    assert dev == expected_dev

    names = parser[4].names
    devices = parser[4].devices
    device_ids = parser[4].devices.find_devices()

    dev = []
    for device_id in device_ids:
        dev.append(names.get_name_string(devices.get_device(device_id).device_kind))
    assert "SIGGEN" in dev


def test_connections(parser):
    """Test parser has made the correct connections."""

    names = parser[0].names
    network = parser[0].network

    [SW1_ID, SW2_ID, G1_ID, G2_ID, I1, I2] = names.lookup(["SW1", "SW2", "G1",
                                                           "G2", "I1", "I2"])

    assert network.get_connected_output(G1_ID, I1) == (SW1_ID, None)
    assert network.get_connected_output(G2_ID, I2) == (SW2_ID, None)


def test_monitor_list(parser):
    """Test parser has created the correct monitors."""
    [G1_ID, G2_ID] = parser[0].names.lookup(["G1", "G2"])
    assert len(parser[0].monitors.monitors_dictionary) == 2
    assert (G1_ID, None) in parser[0].monitors.monitors_dictionary
    assert (G2_ID, None) in parser[0].monitors.monitors_dictionary

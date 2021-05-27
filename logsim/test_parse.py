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

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    #example = "example1.txt"

    file_list=["example1.txt", "example1_with_syntax_errors.txt"]
    parser_list = []
    for item in file_list:
        path = cwd + '\\' + item
        print(path)
        names = Names()
        scanner= Scanner(path, names)
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)
        parse = Parser(names, devices, network, monitors, scanner)
        parse.parse_network()
        parser_list.append(parse)

    return parser_list
"""
@pytest.mark.parametrize("example, num_errors", [
    ("example1.txt",0),
    ("example1_with_syntax_errors.txt",2),
    ("example2_with_syntax_errors.txt",16),
    ("example3.txt",0),
    ("example4.txt",0)
])
"""
def test_get_error_amount(parser):
    """Test if parser detects expected number of errors."""

    assert parser[0].scanner.error_count == 0
    assert parser[1].scanner.error_count == 2








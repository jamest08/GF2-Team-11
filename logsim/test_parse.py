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


@pytest.mark.parametrize("example", [
    ("example1.txt"),
    ("example1_with_syntax_errors.txt"),
    ("example2_with_syntax_errors.txt"),
    ("example3.txt"),
    ("example4.txt")
])

@pytest.fixture
def parser(example):
    """Return an instance of a scanner using ."""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    #example = "Example.txt"
    for file in example:
        path = cwd + '//' + example
    print(path)
    
    names = Names()
    scanner= Scanner(path, names)
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner)
    return parser1,







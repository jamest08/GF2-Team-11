"""Test the names module."""
import pytest
import wx
from wx.core import BoxSizer
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

import sys
import os

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from gui import Gui
from gui import MyGLCanvas

@pytest.fixture
def gui():


    cwd = os.getcwd()
    path = cwd + '\\' + 'example1.txt'

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    parser = Parser(names, devices, network, monitors, scanner)
    parser.parse_network()
    app = wx.App()
    g = Gui("Logic Simulator", path, names, devices, network,
                      monitors)
    g.Show(False)
    
    return g

def test_run_button(gui):
    gui.spin_value = 9
    gui.on_run_button(True)

    for device_id, output_id in gui.monitors.monitors_dictionary:
                signal_list = gui.monitors.monitors_dictionary[(device_id, output_id)]

    assert gui.cycles_completed == 9
    assert len(signal_list) == 9

def test_continue_button(gui):
    gui.spin_value = 10
    gui.on_run_button(True)
    gui.spin_value = 3
    gui.on_continue_button(True)

    for device_id, output_id in gui.monitors.monitors_dictionary:
                signal_list = gui.monitors.monitors_dictionary[(device_id, output_id)]

    assert gui.cycles_completed == 13
    assert len(signal_list) == 13


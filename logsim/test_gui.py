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
from devices import Device
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from gui import Gui
from gui import MyGLCanvas


@pytest.fixture
def gui():

    cwd = os.getcwd()

    if '/' in cwd:
        path = cwd + '/' + 'example1.txt'
    else:
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
    "Check the correct number of cycles is being run."
    gui.spin_value = 9
    gui.on_run_button(True)

    for device_id, output_id in gui.monitors.monitors_dictionary:
        signal_list = gui.monitors.monitors_dictionary[(device_id, output_id)]

    assert gui.cycles_completed == 9
    assert len(signal_list) == 9


def test_continue_button(gui):
    "Check the continue button runs the correct number of cycles."
    gui.spin_value = 10
    gui.on_run_button(True)
    gui.spin_value = 3
    gui.on_continue_button(True)

    for device_id, output_id in gui.monitors.monitors_dictionary:
        signal_list = gui.monitors.monitors_dictionary[(device_id, output_id)]

    assert gui.cycles_completed == 13
    assert len(signal_list) == 13


def test_switches(gui):
    "Check the switch button sets the correct switch to the correct value."
    gui.switches.SetSelection(0)
    switch_id = gui.switches_id_list[0]
    gui.switch_setting.SetSelection(1)
    gui.on_switch_button(True)
    gui.spin_value = 10
    gui.on_run_button(True)
    lev = gui.network.get_output_signal(switch_id, None)

    assert lev == 1

    gui.switches.SetSelection(1)
    switch_id = gui.switches_id_list[1]
    gui.switch_setting.SetSelection(0)
    gui.on_switch_button(True)
    gui.spin_value = 10
    gui.on_run_button(True)
    lev = gui.network.get_output_signal(switch_id, None)

    assert lev == 0


def test_monitor_changes(gui):
    "Test the monitors are added and zapped correctly."
    gui.monitored.SetSelection(0)
    gui.on_zap_button(True)
    assert len(gui.monitors.monitors_dictionary) == 1

    gui.not_monitored.SetSelection(1)
    gui.on_add_button(True)
    assert len(gui.monitors.monitors_dictionary) == 2

    switch_id = gui.switches_id_list[0]
    assert (switch_id, None) in gui.monitors.monitors_dictionary


def test_quit(gui):
    "Test the quit button functions as expected."
    with pytest.raises(SystemExit):
            gui.on_quit_button(True)


"""
Manual Tests

The window resizing and visual printing aspects of the gui
have been visually testes by all members of the group."""
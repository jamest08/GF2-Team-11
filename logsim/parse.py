"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from names import Names
from scanner import Scanner
from devices import Devices
from network import Network
from monitors import Monitors
import sys
import os


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.current_symbol = ""

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        while True:
            # these are all possibilities for start of line
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id == self.names.query('END'):
                break

            elif self.current_symbol.id == self.names.query('define'):
                name_ids = []
                self.current_symbol = self.scanner.get_symbol()
                if not self.name():  # check valid name
                    continue
                name_ids.append(self.current_symbol.id)
                # call to devices, check name not already in use
                self.current_symbol = self.scanner.get_symbol()
                need_continue = False
                while self.current_symbol.id != self.names.query('as'):
                    if not self.name():
                        need_continue = True
                        break
                    else:
                        name_ids.append(self.current_symbol.id)
                        self.current_symbol = self.scanner.get_symbol()
                    # call to devices, check name not already in use
                if need_continue:
                    continue
                self.current_symbol = self.scanner.get_symbol()
                if not self.device(name_ids):
                    continue
                self.current_symbol = self.scanner.get_symbol()

            elif self.current_symbol.id == self.names.query('connect'):
                self.current_symbol = self.scanner.get_symbol()
                [output_id, output_port_id] = self.output()
                if output_id is None:
                    continue
                if self.current_symbol.id != self.names.query('to'):
                    self.scanner.display_error("Expected keyword 'to'")
                    continue
                self.current_symbol = self.scanner.get_symbol()
                [input_id, input_port_id] = self.input()
                if input_id is None:
                    continue
                # check semantic errors
                if self.scanner.error_count == 0:
                    error_type = self.network.make_connection(output_id, output_port_id,
                                                              input_id, input_port_id)
                    if error_type == self.network.INPUT_CONNECTED:
                        self.scanner.display_error("Input is already in a connection")
                        continue
                self.current_symbol = self.scanner.get_symbol()

            elif self.current_symbol.id == self.names.query('monitor'):
                self.current_symbol = self.scanner.get_symbol()
                need_continue = False
                while self.current_symbol.id != self.names.query(';'):
                    [output_id, output_port_id] = self.output()
                    if output_id is None:
                        need_continue = True
                        break
                    if self.scanner.error_count == 0:
                        error_type = self.monitors.make_monitor(output_id, output_port_id)
                        if error_type == self.monitors.MONITOR_PRESENT:
                            self.scanner.display_error("A monitor has already been placed at this output port.")
                            need_continue = True
                            break
                if need_continue:
                    continue

            elif self.current_symbol.type == self.scanner.EOF:
                self.scanner.display_error('Expected END at end of file', False)
                break

            else:  # unexpected symbol
                self.scanner.display_error('Invalid symbol for start of line.')
                continue

            # do this at end of all lines
            if self.current_symbol.id != self.names.query(';'):
                self.scanner.display_error('Expected semicolon')

        # check all inputs connected
        floating_inputs = self.network.check_network()
        if len(floating_inputs) != 0:
            floating_inputs_list = []
            for floating_input in floating_inputs:
                floating_inputs_list.append(self.names.get_name_string(floating_input[0])
                                            + '.' + self.names.get_name_string(floating_input[1]))
            self.scanner.display_error("The following inputs are floating: " + str(floating_inputs_list), False)

        # check at least one monitor
        if len(self.monitors.monitors_dictionary) == 0:
            print("Warning: No monitors specified.")

        # may not pick up all semantic errors as stops calling network
        print('Number of errors found: ' + str(self.scanner.error_count))
        if self.scanner.error_count == 0:
            return True
        else:
            return False

    def name(self):
        if self.current_symbol.type != self.scanner.NAME:
            self.scanner.display_error('Invalid name, may be keyword')
            return False
        else:
            return True

    def device(self, name_ids):
        if self.current_symbol.id == self.names.query('SWITCH'):
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id == self.names.query('0'):
                switch_state = self.devices.LOW
            elif self.current_symbol.id == self.names.query('1'):
                switch_state = self.devices.HIGH
            else:
                self.scanner.display_error("Expected 0 or 1 for switch state")
                return False
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('state'):
                self.scanner.display_error("Expected keyword 'state'")
                return False
            if self.scanner.error_count == 0:
                for name_id in name_ids:
                    self.devices.make_device(name_id, self.devices.SWITCH, switch_state)
                    # errors all covered by syntax

        elif self.current_symbol.id in [self.names.query('NAND'), self.names.query('AND'),
                                        self.names.query('OR'), self.names.query('NOR')]:
            gate_id = self.current_symbol.id
            self.current_symbol = self.scanner.get_symbol()
            num_inputs = int(self.names.get_name_string(self.current_symbol.id))
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('inputs'):
                self.scanner.display_error("Expected keyword 'inputs'")
                return False
            if self.scanner.error_count == 0:
                for name_id in name_ids:
                    error_type = self.devices.make_device(name_id, gate_id, num_inputs)
                    if error_type == self.devices.INVALID_QUALIFIER:
                        self.scanner.display_error("Number of inputs must be integer in range(1, 17)")
                        return False

        elif self.current_symbol.id == self.names.query('CLOCK'):
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('period'):
                self.scanner.display_error("Expected keyword 'period'")
                return False
            self.current_symbol = self.scanner.get_symbol()
            try:
                # zeros at start will be truncated
                clock_period = int(self.names.get_name_string(self.current_symbol.id))
            except ValueError:
                self.scanner.display_error("Expected integer period.")
                return False
            if self.scanner.error_count == 0:
                for name_id in name_ids:
                    error_type = self.devices.make_device(name_id, self.devices.CLOCK, clock_period//2)
                    if error_type == self.devices.INVALID_QUALIFIER:
                        self.scanner.display_error("Expected half period >= 1 simulation cycle")
                        return False

        elif self.current_symbol.id == self.names.query('DTYPE'):
            if self.scanner.error_count == 0:
                for name_id in name_ids:
                    self.devices.make_device(name_id, self.devices.D_TYPE)

        elif self.current_symbol.id == self.names.query('XOR'):
            if self.scanner.error_count == 0:
                for name_id in name_ids:
                    self.devices.make_device(name_id, self.devices.XOR)

        else:
            self.scanner.display_error('Expected device type')
            return False

        return True

    def output(self):
        name_id = self.current_symbol.id
        if self.devices.get_device(name_id) is None:  # check actually a device
            self.scanner.display_error('Output device does not exist.')
            return [None, None]
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id == self.names.query('.'):
            if self.devices.get_device(name_id).device_kind != self.devices.D_TYPE:
                self.scanner.display_error("Unexpected dot. Can only specify port for DTYPE.")
                return [None, None]
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id not in [self.names.query('Q'), self.names.query('QBAR')]:
                self.scanner.display_error('Expected Q or QBAR to follow after dot.')
                return [None, None]
            else:
                port_id = self.current_symbol.id
            self.current_symbol = self.scanner.get_symbol()
        else:
            if self.devices.get_device(name_id).device_kind == self.devices.D_TYPE:
                self.scanner.display_error("Output port must be specified for DTYPE")
                return [None, None]
            port_id = None
        return [name_id, port_id]
        # current symbol is symbol after output

    def input(self):
        name_id = self.current_symbol.id
        if self.devices.get_device(name_id) is None:  # check actually a device
            self.scanner.display_error('Input device does not exist.')
            return [None, None]
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id != self.names.query('.'):
            self.scanner.display_error("Expected '.' before input port")
            return [None, None]
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id in [self.names.query('DATA'), self.names.query('SET'),
                                      self.names.query('CLK'), self.names.query('CLEAR')]:
            if self.devices.get_device(name_id).device_kind != self.devices.D_TYPE:
                self.scanner.display_error("DTYPE port specified for non-DTYPE device.")
                return [None, None]
            port_id = self.current_symbol.id
        elif self.current_symbol.id in self.names.lookup(['I1', 'I2', 'I3', 'I4', 'I5', 'I6',
                                                          'I7', 'I8', 'I9', 'I10', 'I11', 'I12',
                                                          'I13', 'I14', 'I15', 'I16']):
            if self.devices.get_device(name_id).device_kind not in [self.devices.AND, self.devices.NAND,
                                                                    self.devices.OR, self.devices.NOR, self.devices.XOR]:
                self.scanner.display_error("Invalid input port type for "
                                            + self.names.get_name_string(self.devices.get_device(name_id).device_kind))
                return [None, None]
            if self.current_symbol.id not in self.devices.get_device(name_id).inputs:
                self.scanner.display_error("Specified input port out of range")
                return [None, None]
            port_id = self.current_symbol.id
        else:
            self.scanner.display_error('Expected port')
            return [None, None]
        return [name_id, port_id]
        # current symbol is last symbol of input (different from output function)

"""
#quick tests
names = Names()
cwd=(os.getcwd())

example = "example2.txt"
path = cwd + '/' + example
#path = cwd + '\\' +example

scanner= Scanner(path, names)
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)
parser = Parser(names, devices, network, monitors, scanner)
parser.parse_network()

device_ids = devices.find_devices()
for device_id in device_ids:
    print(names.get_name_string(devices.get_device(device_id).device_kind), names.get_name_string(device_id))
    for input_id in devices.get_device(device_id).inputs:
        output = network.get_connected_output(device_id, input_id)
        if output != None:
                print('Input ' + names.get_name_string(input_id) + ' connected to', names.get_name_string(output[0]))
                if output[1] != None:
                    print('Output port ' + names.get_name_string(output[1]))
"""

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

    #check all listed semantic errors included
    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        while True:
            #these are all possibilities for start of line (ie. just after semicolon)
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id == self.names.query('END'):
                break

            elif self.current_symbol.id == self.names.query('define'):
                self.current_symbol = self.scanner.get_symbol()
                if not self.name():
                    continue
                #call to devices, check name not already in use
                self.current_symbol = self.scanner.get_symbol()
                need_continue = False
                while self.current_symbol.id != self.names.query('as'):
                    if not self.name():
                        need_continue = True
                        break
                    else:
                        self.current_symbol = self.scanner.get_symbol()
                    #call to devices, check name not already in use
                if need_continue:
                    continue
                self.current_symbol = self.scanner.get_symbol()
                if not self.device():
                    continue
                self.current_symbol = self.scanner.get_symbol()

            elif self.current_symbol.id == self.names.query('connect'):
                self.current_symbol = self.scanner.get_symbol()
                if not self.output():
                    continue
                if self.current_symbol.id != self.names.query('to'):
                    self.scanner.display_error("Expected keyword 'to'")
                    continue
                self.current_symbol = self.scanner.get_symbol()
                if not self.input():
                    continue
                self.current_symbol = self.scanner.get_symbol()

            elif self.current_symbol.id == self.names.query('monitor'):
                self.current_symbol = self.scanner.get_symbol()
                need_continue = False
                while self.current_symbol.id != self.names.query(';'):
                    if not self.output():
                        need_continue = True
                        break
                if need_continue:
                    continue
                    #call monitors class

            elif self.current_symbol.type == self.scanner.EOF:
                self.scanner.display_error('Expected END at EOF')
                break

            else: #unexpected symbol
                self.scanner.display_error('Invalid symbol')
                continue

            if self.current_symbol.id != self.names.query(';'): #do this at end of all lines - may need to move this depending on where scanner.error() leave pointer
                self.scanner.display_error('Expected semicolon')

        print('Number of syntax errors found: ' + str(scanner.error_count))
        return True

    def name(self):
        if self.current_symbol.type != self.scanner.NAME:
            self.scanner.display_error('Invalid name, may be keyword')
            return False
        else:
            return True

    def device(self):
        if self.current_symbol.id == self.names.query('SWITCH'):
            self.current_symbol = self.scanner.get_symbol()
            switch_state_id = self.current_symbol.id
            if switch_state_id not in [self.names.query('0'), self.names.query('1')]:
                self.scanner.display_error("Expected 0 or 1 for switch state")
                return False
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('state'):
                self.scanner.display_error("Expected keyword 'state'")
                return False
        elif self.current_symbol.id in [self.names.query('NAND'), self.names.query('AND'), self.names.query('OR'), self.names.query('NOR')]:
            gate_id = self.current_symbol.id
            self.current_symbol = self.scanner.get_symbol()
            num_inputs_id = self.current_symbol.id
            #check semantic error: invalid qualifier
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('inputs'):
                self.scanner.display_error("Expected keyword 'inputs'")
                return False
        elif self.current_symbol.id == self.names.query('CLOCK'):
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('period'):
                self.scanner.display_error("Expected keyword 'period'")
                return False
            self.current_symbol = self.scanner.get_symbol()
            clock_period_id = self.current_symbol.id
            #check semantic error: clock period is number, doesn't start with zero
        elif self.current_symbol.id == self.names.query('DTYPE'):
            #call to devices
            pass
        elif self.current_symbol.id == self.names.query('XOR'):
            #call to devices
            pass
        else:
            self.scanner.display_error('Expected device type')
            return False
        return True

    def output(self):
        name_id = self.current_symbol.id
        if not self.name(): #check actually a name
            return False
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id == self.names.query('.'):
            #check name corresponds to DTYPE
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id not in [self.names.query('Q'), self.names.query('QBAR')]:
                raise SyntaxError('Expected Q or QBAR to follow .')
            self.current_symbol = self.scanner.get_symbol()
        return True
        #return output name/port to be called by network/monitor. current symbol is symbol after output


    def input(self):
        name_id = self.current_symbol.id
        if not self.name(): #check actually a name
            return False
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id != self.names.query('.'):
            raise SyntaxError("Expected '.' before input port")
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id in [self.names.query('DATA'), self.names.query('SET'), self.names.query('CLK'), self.names.query('CLEAR')]:
            #check name corresponds to DTYPE/port_absent error
            pass
        elif self.current_symbol.id in self.names.lookup(['I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15', 'I16']):
            pass
            #check received valid input number. check for port_absent
        else:
            raise SyntaxError('Expected port')
        return True
        #return input name/port to be called by network. current symbol is last symbol of input (different from input function)


#pad out functions etc. then include calls to Devices and Network with semantic error detection

#quick tests
names = Names()
cwd=(os.getcwd())
       
example = "example1_with_syntax_errors.txt"
path = cwd + '/' + example
#path = cwd + '\\' +example

scanner= Scanner(path, names)
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)
parser = Parser(names, devices, network, monitors, scanner)
parser.parse_network()
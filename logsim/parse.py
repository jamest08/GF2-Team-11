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
            if self.current_symbol.id ==  self.names.query('END'):
                break
            elif self.current_symbol.id == self.names.query('define'):
                self.current_symbol = self.scanner.get_symbol()
                self.name()
                #call to devices, check name not already in use
                while True:
                    self.current_symbol = self.scanner.get_symbol()
                    if self.current_symbol.id == self.names.query('as'): #may need changing
                        break
                    self.name()
                    #call to devices, check name not already in use
                self.current_symbol = self.scanner.get_symbol()
                self.device()
                self.current_symbol = self.scanner.get_symbol()
            elif self.current_symbol.id == self.names.query('connect'):
                self.current_symbol = self.scanner.get_symbol()
                self.output()
                if self.current_symbol.id != self.names.query('to'):
                    raise SyntaxError("Expected keyword 'to'")
                self.current_symbol = self.scanner.get_symbol()
                self.input()
                self.current_symbol = self.scanner.get_symbol()
            elif self.current_symbol.id == self.names.query('monitor'):
                self.current_symbol = self.scanner.get_symbol()
                while self.current_symbol.id != self.names.query(';'):
                    self.output()
                    #call monitors class
            elif self.current_symbol.id == self.names.query(""):
                raise SyntaxError('Expected END at EOF') #replace this with a call to syntax error method of scanner class
                break
            else: #unexpected symbol
                raise SyntaxError('Invalid symbol') #replace this with a call to syntax error method of scanner class, move to semicolon

            if self.current_symbol.id != self.names.query(';'): #do this at end of all lines - may need to move this depending on where scanner.error() leave pointer
                raise SyntaxError('Expected semicolon') #replace this with a call to syntax error method of scanner class, move to semicolon

        return True

    def name(self):
        if self.current_symbol.type != self.scanner.NAME:
            raise NameError('Invalid name, may be keyword')

    def device(self):
        if self.current_symbol.id == self.names.query('SWITCH'):
            self.current_symbol = self.scanner.get_symbol()
            switch_state_id = self.current_symbol.id
            if switch_state_id not in [self.names.query('0'), self.names.query('1')]:
                raise SyntaxError("Expected 0 or 1 for switch state") #replace this with a call to syntax error method of scanner class, move to semicolon
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('state'):
                raise SyntaxError("Expected keyword 'state'")
        elif self.current_symbol.id in [self.names.query('NAND'), self.names.query('AND'), self.names.query('OR'), self.names.query('NOR')]:
            gate_id = self.current_symbol.id
            self.current_symbol = self.scanner.get_symbol()
            num_inputs_id = self.current_symbol.id
            #check semantic error: invalid qualifier
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('inputs'):
                raise SyntaxError("Expected keyword 'inputs'")
        elif self.current_symbol.id == self.names.query('CLOCK'):
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id != self.names.query('period'):
                raise SyntaxError("Expected keyword 'period'")
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
            raise SyntaxError('expected device type') #replace this with a call to syntax error method of scanner class, move to semicolon

    def output(self):
        name_id = self.current_symbol.id
        self.name() #check actually a name
        self.current_symbol = self.scanner.get_symbol()
        if self.current_symbol.id == self.names.query('.'):
            #check name corresponds to DTYPE
            self.current_symbol = self.scanner.get_symbol()
            if self.current_symbol.id not in [self.names.query('Q'), self.names.query('QBAR')]:
                raise SyntaxError('Expected Q or QBAR to follow .')
            self.current_symbol = self.scanner.get_symbol()
        #return output name/port to be called by network/monitor. current symbol is symbol after output


    def input(self):
        name_id = self.current_symbol.id
        self.name() #check actually a name
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
        #return input name/port to be called by network. current symbol is last symbol of input (different from input function)


#pad out functions etc. then include calls to Devices and Network with semantic error detection

#quick tests
names = Names()
cwd=(os.getcwd())
       
example = "example3.txt"
path = cwd + '/' + example
#path = cwd + '\\' +example
print(path)


scanner= Scanner(path, names)
devices = Devices(names)
network = Network(names, devices)
monitors = Monitors(names, devices, network)
parser = Parser(names, devices, network, monitors, scanner)
parser.parse_network()
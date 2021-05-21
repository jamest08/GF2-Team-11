"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


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
            #these are all possibilities for start of line (ie. just after semicolon)
            self.current_symbol = self.scanner.getsymbol()
            if self.current_symbol.id ==  self.names.query('END'):
                break
            elif self.current_symbol.id == self.names.query('define'):
                self.current_symbol = self.scanner.getsymbol()
                self.name()
                while True:
                    self.current_symbol = self.scanner.getsymbol()
                    if self.current_symbol.id == self.names.query('as'):
                        break
                    self.name()
                self.current_symbol = self.scanner.getsymbol()
                self.device()
                self.current_symbol = self.scanner.getsymbol()
                if self.current_symbol.id != self.names.query(';'):
                    raise SyntaxError('Expected semicolon') #replace this with a call to syntax error method of scanner class, move to semicolon
            elif self.current_symbol.id == self.names.query('connect'):
                self.output()

            elif self.current_symbol.id == self.names.query('monitor'):
                pass
            elif self.current_symbol.id == self.names.query(""):
                raise SyntaxError('Expected END at EOF') #replace this with a call to syntax error method of scanner class
            else: #unexpected symbol
                raise SyntaxError('Invalid symbol') #replace this with a call to syntax error method of scanner class, move to semicolon

        return True

    def name(self):
        if self.current_symbol.type != self.Name:
            raise NameError('Invalid name, may be keyword')

    def device(self):
        if self.current_symbol.id == self.names.query('SWITCH'):
            pass
        elif self.current_symbol.id in [self.names.query('NAND'), self.names.query('AND'), self.names.query('OR')]:
            pass
        elif self.current_symbol.id == self.names.query('CLOCK'):
            pass
        elif self.current_symbol.id == self.names.query('DTYPE'):
            pass
        elif self.current_symbol.id == self.names.query('XOR'):
            pass
        else:
            raise SyntaxError('expected device type') #replace this with a call to syntax error method of scanner class, move to semicolon

    def output(self):
        pass

    def input(self):
        pass


#pad out functions etc. then include calls to Devices and Network with semantic error detection
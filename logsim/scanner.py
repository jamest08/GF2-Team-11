"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    type: symbol type.
    id: id of symbol.
    pos: position of symbol in the file.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self,type,id,pos):
        """Initialise symbol properties."""
        self.type = type
        self.id = id
        self.pos = pos


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    skip_spaces(): Finds the next non whitespace chaarcter in the file.
    get_number():
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.symbol_type_list = [self.FULLSTOP, self.SEMICOLON,
        self.KEYWORD, self.NUMBER, self.NAME, self.INVALID] = range(6)
        self.keywords_list = ["define", "connect", "monitor", 
        "END", "as", "XOR", "DTYPE", "CLOCK", "SWITCH", 
        "state", "NAND", "AND", "OR", "NOR", "inputs", 
        "period", "to", "Q", "QBAR", "DATA", "CLK", "SET", "CLEAR"]
        [self.define_ID, self.connect_ID, self.monitor_ID,
        self.END_ID, self.as_ID, self.XOR_ID, self.DTYPE_ID, 
        self.CLOCK_ID, self.SWITCH_ID, self.state_ID, 
        self.NAND_ID,self.AND_ID, self.OR_ID, self.NOR_ID, 
        self.inputs_ID, self.period_ID, self.to_ID, self.Q_ID, 
        self.QBAR_ID, self.DATA_ID, self.CLK_ID, self.SET_ID, 
        self.CLEAR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""


    def get_symbol(self,path):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces(path) # current character now not whitespace

        if self.current_character.isalpha(): # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # number
            num = self.get_number()
            symbol.id = self.names.lookup([num])
            symbol.type = self.NUMBER

        elif self.current_character == ".": # punctuation
            symbol.type = self.FULLSTOP
            symbol.id = self.names.lookup([.])

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            symbol.id = self.names.lookup([;])

        else: # not a valid character
            symbol.type = self.INVALID

        return symbol
    
    def open_file(path):
        """Open and return the file specified by path."""
        file =open(path, "r")
        return(file)

    def skip_spaces(self,path):
        file= open_file(path)
        z = file.read(1)
        
        while z.isspace()==True:
            z=file.read(1)
             
        return(z)

"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from names import Names
import sys
import os


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

    def __init__(self, type=None, id=None, pos=None, line=None):
        """Initialise symbol properties."""
        self.type = type
        self.id = id
        self.pos = pos
        self.line = line


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
    skip_spaces(self): Finds the next non whitespace character in the file.
    get_number(self): Finds all digits in a number
    open_file(self): Opens the specified definition file
    get_name(self): Finds a whole name in the definition file
    skip_comment(self): Skips comments enclosed in hashes in the definition
                        file
    display_error(self, error_message): Displays the error line and error
                        message
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        if isinstance(names, Names) is True:
            self.names = names
        else:
            raise TypeError("names arguments not an instance of Names class")

        self.symbol_type_list = [self.FULLSTOP, self.SEMICOLON,
                                 self.KEYWORD, self.NUMBER, self.NAME,
                                 self.INVALID, self.EOF] = range(7)
        self.keywords_list = ["define", "connect", "monitor",
                              "END", "as", "XOR", "DTYPE", "CLOCK", "SWITCH",
                              "state", "NAND", "AND", "OR", "NOR", "inputs",
                              "period", "to", "Q", "QBAR", "DATA", "CLK",
                              "SET", "CLEAR"]
        [self.define_ID, self.connect_ID, self.monitor_ID,
            self.END_ID, self.as_ID, self.XOR_ID, self.DTYPE_ID,
            self.CLOCK_ID, self.SWITCH_ID, self.state_ID,
            self.NAND_ID, self.AND_ID, self.OR_ID, self.NOR_ID,
            self.inputs_ID, self.period_ID, self.to_ID, self.Q_ID,
            self.QBAR_ID, self.DATA_ID, self.CLK_ID, self.SET_ID,
            self.CLEAR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""
        self.path = path
        self.file = self.open_file(self.path)
        self.error_count = 0
        self.last_semicolon_pos = 0
        self.last_last_semicolon_pos = 0
        self.last_comment_pos = 0
        self.error_message_list = []

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace
        if self.current_character == "#":  # comments skipped
            self.skip_comment()
            return self.get_symbol()

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])
            symbol.pos = self.file.tell()

        elif self.current_character.isdigit():  # number
            num = self.get_number()
            [symbol.id] = self.names.lookup([num])
            symbol.type = self.NUMBER
            symbol.pos = self.file.tell()

        elif self.current_character == ".":  # punctuation
            symbol.type = self.FULLSTOP
            [symbol.id] = self.names.lookup(["."])
            symbol.pos = self.file.tell()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            [symbol.id] = self.names.lookup([";"])
            symbol.pos = self.file.tell()
            self.last_last_semicolon_pos = self.last_semicolon_pos
            self.last_semicolon_pos = self.file.tell()

        elif self.current_character == "":  # end of file character
            symbol.type = self.EOF
            [symbol.id] = self.names.lookup([""])
            symbol.pos = self.file.tell()

        else:  # not a valid character
            symbol.type = self.INVALID
            [symbol.id] = self.names.lookup([self.current_character])
            symbol.pos = self.file.tell()

        return symbol

    def open_file(self, path):
        """Open and return the file specified by path."""
        if type(path) != str:
            raise TypeError("File path was not a string.")
        else:
            try:
                file = open(self.path, "r")
            except Exception:
                print("File could not be opened.")
                sys.exit()
            else:
                return(file)

    def skip_spaces(self):
        """Skip to next non whitespace character in the file."""
        z = self.file.read(1)

        while z.isspace() is True:
            z = self.file.read(1)

        self.current_character = z

    def get_name(self):
        """Return full name."""
        isname = False

        while isname is False:
            z = self.current_character

            name = []
            if z.isalpha() is True:

                name.append(z)
                prev_char_pos = self.file.tell()
                nextchar = self.file.read(1)

                while nextchar.isalnum() is True:
                    name.append(nextchar)
                    prev_char_pos = self.file.tell()
                    nextchar = self.file.read(1)
                isname = True
                na = ''.join(name)

                self.file.seek(prev_char_pos)
                return(na)

            if z == '':
                return ''

    def get_number(self):
        """Return all digits in a number."""
        z = self.current_character
        number = []

        if z.isdigit() is True:

            number.append(z)
            prev_char_pos = self.file.tell()
            nextnum = self.file.read(1)

            while nextnum.isdigit() is True:
                number.append(nextnum)
                prev_char_pos = self.file.tell()
                nextnum = self.file.read(1)

            n = ''.join(number)
            self.file.seek(prev_char_pos)
            return(n)

    def skip_comment(self):
        """Skips comments enclosed in hashes."""
        z = self.file.read(1)

        end_of_file = False
        while z != "#" and end_of_file is False:
            z = self.file.read(1)
            if z == "":
                end_of_file = True

        self.last_comment_pos = self.file.tell()
        self.current_character = z

    def display_error(self, error_message, caret=True):
        """Display line of error and the error_message."""
        self.error_count += 1
        error_position = self.file.tell()

        self.error_message_list.append(error_message)
        if self.last_semicolon_pos > self.last_comment_pos:
            if self.current_character == ';':
                pos = self.last_last_semicolon_pos
                difference = error_position - self.last_last_semicolon_pos
            else:
                pos = self.last_semicolon_pos
                difference = error_position-self.last_semicolon_pos
        else:
            pos = self.last_comment_pos
            difference = error_position - self.last_comment_pos

        if pos == 0:
            self.file.seek(pos)
        else:
            self.file.seek(pos)
            self.skip_spaces()
            cur_pos = self.file.tell()
            self.file.seek(cur_pos-1, 0)

        if type(error_message) != str:
            raise TypeError("Error message not a string")
        else:
            if caret:  # caret True when need error line to be printed
                print(self.file.readline().strip())
                print(" "*(difference-3), end='')
                print("^")
            print("***ERROR: {}".format(error_message))
            print('\n')

        self.last_semicolon_pos = self.file.tell()

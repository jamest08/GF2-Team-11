"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:
    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.names_list = []
        self.error_code_count = 0  # how many error codes have been declared

    # edited pre-written method to include ValueError
    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        elif num_error_codes <= 0:
            raise ValueError("Expected num_error_codes > 0.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        if isinstance(name_string, str):
            try:
                return self.names_list.index(name_string)
            except ValueError:  # exception thrown if name not in list
                return None
        else:
            raise TypeError("Expected name_string to be string.")

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        if isinstance(name_string_list, list):
            name_id_list = []
            for name_string in name_string_list:
                if isinstance(name_string, str):
                    try:
                        name_id_list.append(self.names_list.index(name_string))
                    except ValueError:  # exception thrown if name not in list
                        self.names_list.append(name_string)
                        name_id_list.append(len(self.names_list) - 1)
                else:
                    raise TypeError("Expected list item to be string.")
            return name_id_list
        else:
            raise TypeError("Expected name_string_list to be list.")

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if isinstance(name_id, int):
            if name_id < len(self.names_list) and name_id >= 0:  # if id exists
                return self.names_list[name_id]
            elif name_id < 0:  # if invalid name_id value
                raise ValueError
            else:  # if name_id not in names list
                return None
        else:
            raise TypeError("Expected name_id to be integer.")

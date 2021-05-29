"""Test the names module."""
import pytest
import sys
import os

from scanner import Scanner
from names import Names


@pytest.fixture
def scanner_one():
    """Return an instance of a scanner using example 1"""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    example = "example1.txt"

    path = "{}/{}".format(cwd, example)
    print(path)
    names = Names()

    scanner = Scanner(path, names)
    return scanner


@pytest.fixture
def scanner_two():
    """Return an instance of a scanner using example 2"""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    example = "example2.txt"

    path = "{}/{}".format(cwd, example)
    print(path)
    names = Names()

    scanner = Scanner(path, names)
    return scanner


@pytest.fixture
def scanner_three():
    """Return an instance of a scanner using example 2 with comments"""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    example = "example2_with_comments.txt"

    path = "{}/{}".format(cwd, example)
    print(path)
    names = Names()

    scanner = Scanner(path, names)
    return scanner


def test_innit_raises_exceptions():
    names = Names()
    with pytest.raises(TypeError):
        scanner = Scanner(12, names)

    cwd = os.getcwd()
    example = "example1.txt"
    new_path = "{}/{}".format(cwd, example)
    print(new_path)

    with pytest.raises(TypeError):
        scanner = Scanner(new_path, "not a names instance")


def test_get_symbol_example_one(scanner_one):
    """Test if get_symbol produces the correct output for example file 1"""
    scanner = scanner_one

    symbol = scanner.get_symbol()  # symbol should be "define"
    assert symbol.type == scanner.KEYWORD
    assert symbol.id == scanner.define_ID

    symbol = scanner.get_symbol()  # symbol should be "G1"
    assert symbol.type == scanner.NAME
    keyword_list_length = len(scanner.keywords_list)
    assert symbol.id == keyword_list_length

    for i in range(6):
        symbol = scanner.get_symbol()  # should end with symbol ";"

    assert symbol.type == scanner.SEMICOLON

    # ensure scanner handles new line appropriately

    symbol = scanner.get_symbol()  # symbol should be "define"
    assert symbol.type == scanner.KEYWORD
    assert symbol.id == scanner.define_ID

    # check if symbols around '.' are handled properly

    for i in range(12):
        symbol = scanner.get_symbol()  # should end with symbol "."

    assert symbol.type == scanner.FULLSTOP
    symbol = scanner.get_symbol()  # should be "I1"
    assert symbol.type == scanner.NAME

    # test "END symbol is identified"

    for i in range(27):
        symbol = scanner.get_symbol()  # should end on "END" symbol

    assert symbol.type == scanner.KEYWORD
    assert symbol.id == scanner.END_ID

    # check get_symbol returns "" if at the end of the file

    symbol = scanner.get_symbol()

    assert symbol.type == scanner.EOF


def test_get_symbol_example_two(scanner_two):
    """Test if get_symbol produces the correct output for example file 2"""
    scanner = scanner_two

    # check if single character name is handled properly

    for i in range(6):
        symbol = scanner.get_symbol()  # symbol should be '1'

    assert symbol.type == scanner.NUMBER

    symbol = scanner.get_symbol()  # symbol should be ';'

    assert symbol.type == scanner.SEMICOLON


def test_get_symbol_example_three(scanner_two, scanner_three):
    """Test if get_symbol produces the correct output for example file 3"""

    # checking if single line comment is ignored

    for i in range(8):
        symbol_two = scanner_two.get_symbol()
        symbol_three = scanner_three.get_symbol()

        print("ex. 2 id: {}, ex. 3 id: {}".format(symbol_two.id, symbol_three.id))

        assert symbol_two.type == symbol_three.type
        assert symbol_two.id == symbol_three.id

    # checking if comment in the middle of a line is ignored

    for i in range(6):
        symbol_two = scanner_two.get_symbol()
        symbol_three = scanner_three.get_symbol()

        print("ex. 2 id: {}, ex. 3 id: {}".format(symbol_two.id, symbol_three.id))

        assert symbol_two.type == symbol_three.type
        assert symbol_two.id == symbol_three.id

    # checking if paragraph comment is ignored

    for i in range(68):
        symbol_two = scanner_two.get_symbol()
        symbol_three = scanner_three.get_symbol()

    for i in range(5):
        symbol_two = scanner_two.get_symbol()
        symbol_three = scanner_three.get_symbol()

        assert symbol_two.type == symbol_three.type
        assert symbol_two.id == symbol_three.id


def test_display_error_raises_exceptions(scanner_one):
    """Check if the display error function is raising exceptions"""

    scanner = scanner_one

    with pytest.raises(TypeError):
        var = scanner_one.display_error(12)


def test_display_error(scanner_one):
    """Check if the display error function is producing the expected output"""

    """ Will check if print statements are appropriate from manual testing,
    since the function does not output any information about the print"""

    # check if next read position is on next line after an error is flagged

    scanner = scanner_one

    for i in range(3):
        symbol = scanner.get_symbol()

    scanner.display_error("error_message")

    symbol = scanner.get_symbol()  # expecting this symbol to be 'define'
    assert symbol.id == scanner.define_ID

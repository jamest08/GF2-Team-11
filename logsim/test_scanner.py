"""Test the names module."""
import pytest
import sys
import os

from scanner import Scanner
from scanner import Symbol
from names import Names

@pytest.fixture
def scanner():
    """Return an instance of a scanner using ."""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    example = "Example.txt"

    path = "{}/{}".format(cwd, example)
    print(path)
    names = Names()

    scanner = Scanner(path, names)
    return scanner


def test_innit_raises_exceptions():
    path = "this is not a path"
    names = Names()
    with pytest.raises(ValueError):
        scanner = Scanner(path, names)
    with pytest.raises(TypeError):
        scanner = Scanner(12, names)
    
    cwd = os.getcwd()
    example = "example.txt"
    new_path = "{}/{}".format(cwd, example)
    print(new_path)

    with pytest.raises(TypeError):
        scanner = Scanner(new_path, "not a names instance")

def test_get_symbol(scanner, symbol):
    """Test if get_symbol produces the correct output."""
    symbol = scanner.get_symbol() # symbol should be "define"
    assert symbol.type == scanner.KEYWORD
    assert symbol.id == scanner.define_ID

    next_symbol = scanner.get_symbol() # symbol should be "G1"
    assert next_symbol.type == scanner.NAME
    keyword_list_length = len(scanner.keywords_list)
    assert next_symbol.id == keyword_list_length

    for i in range(6):
        new_symbol = scanner.get_symbol() # should end with symbol ";"
    
    assert new_symbol.type == scanner.SEMICOLON

    # ensure scanner handles new line appropriately

    symbol = scanner.get_symbol() # symbol should be "define"
    assert symbol.type == scanner.KEYWORD
    assert symbol.id == scanner.define_ID


    





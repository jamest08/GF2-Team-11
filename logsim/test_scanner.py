"""Test the names module."""
import pytest
import sys
import os

from scanner import Scanner
from names import Names

@pytest.fixture
def scanner():
    """Return an instance of a scanner."""
    print("\nNow opening file...")

    # Print the path provided and try to open the file for reading
    cwd = os.getcwd()
    example = "example.rtf"

    path = "{}/{}".format(cwd, example)
    print(path)
    names = Names()

    scanner = Scanner(path, names)


def test_innit_raises_exceptions():
    path = "this is not a path"
    names = Names()
    with pytest.raises(ValueError):
        scanner = Scanner(path, names)
    with pytest.raises(TypeError):
        scanner = Scanner(12, names)
    
    cwd = os.getcwd()
    example = "example.rtf"
    new_path = "{}/{}".format(cwd, example)
    print(new_path)

    with pytest.raises(TypeError):
        scanner = Scanner(new_path, "not a names instance")






# def test_get_symbol_raises_exceptions():
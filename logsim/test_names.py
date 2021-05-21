"""Test the names module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["James", "Anna", "Neelay"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    names = Names()
    names.lookup(name_string_list)
    return names


def test_get_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "James"),
    (1, "Anna"),
    (2, "Neelay"),
    (3, None)
])
def test_get_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


def test_lookup_raises_exceptions(used_names):
    """Test if lookup raises the expected exceptions"""
    with pytest.raises(TypeError):
        used_names.lookup(1.4)
    with pytest.raises(TypeError):
        used_names.lookup("James")


@pytest.mark.parametrize("name_string, expected_id", [
    (["James"], [0]),
    (["Anna", "Neelay"], [1, 2])
])
def test_lookup(used_names, name_string, expected_id):
    """Test if lookup returns the expected id"""
    # Name is present
    assert used_names.lookup(name_string) == expected_id
    # Name gets added
    used_names.lookup(["Andrew"])
    assert used_names.lookup(["Andrew"]) == [3]


def test_unique_error_codes_raises_exceptions(used_names):
    """Test if unique_error_codes raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.unique_error_codes(1.2)
    with pytest.raises(TypeError):
        used_names.unique_error_codes("hello")
    with pytest.raises(ValueError):
        used_names.unique_error_codes(-1)


def test_unique_error_codes(used_names):
    """Test if unique_error_codes provides the expected output"""
    # Confirm 4 codes currently
    assert used_names.unique_error_codes(3) == range(0, 3)
    # Confirm new code is added
    assert used_names.unique_error_codes(3) == range(3, 6)


def test_query_raises_exceptions(used_names):
    """Test if query raises the expected exceptions"""
    with pytest.raises(TypeError):
        used_names.query(1.4)


@pytest.mark.parametrize("name_string, expected_id", [
    ("James", 0),
    ("Anna", 1),
    ("Neelay", 2)
])
def test_query(used_names, name_string, expected_id):
    """Test if lookup returns the expected id"""
    # Name is present
    assert used_names.query(name_string) == expected_id
    # Name gets added
    assert used_names.query("Bob") is None

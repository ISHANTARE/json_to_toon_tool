import pytest
from mini_toon.encoder import encode

def test_primitives():
    assert encode("hello") == "hello"
    assert encode("hello world") == "hello world"
    assert encode(42) == "42"
    assert encode(3.14) == "3.14"
    assert encode(True) == "true"
    assert encode(False) == "false"
    assert encode(None) == "null"

def test_quoted_strings():
    # Empty string
    assert encode("") == '""'
    # Leading/trailing space
    assert encode(" a ") == '" a "'
    # Reserved words
    assert encode("true") == '"true"'
    assert encode("null") == '"null"'
    # Numbers as strings
    assert encode("42") == '"42"'
    assert encode("05") == '"05"'
    # Special chars
    assert encode("a:b") == '"a:b"'
    assert encode("a,b") == '"a,b"' # comma is default delim
    assert encode('- listItem') == '"- listItem"'

def test_simple_object():
    obj = {"id": 1, "name": "Ada", "active": True}
    expected = (
        "id: 1\n"
        "name: Ada\n"
        "active: true"
    )
    assert encode(obj) == expected

def test_nested_object():
    obj = {"user": {"id": 1, "name": "Ada"}}
    expected = (
        "user:\n"
        "  id: 1\n"
        "  name: Ada"
    )
    assert encode(obj) == expected

def test_primitive_array_inline():
    obj = {"tags": ["admin", "ops", "dev"]}
    expected = "tags[3]: admin,ops,dev"
    assert encode(obj) == expected

def test_tabular_array():
    obj = {"items": [{"id": 1, "qty": 5}, {"id": 2, "qty": 3}]}
    expected = (
        "items[2]{id,qty}:\n"
        "  1,5\n"
        "  2,3"
    )
    assert encode(obj) == expected

def test_mixed_array():
    obj = {"items": [1, {"a": 1}, "x"]}
    expected = (
        "items[3]:\n"
        "  - 1\n"
        "  - a: 1\n"
        "  - x"
    )
    assert encode(obj) == expected

def test_root_array():
    obj = ["x", "y", "z"]
    expected = "[3]: x,y,z"
    assert encode(obj) == expected

def test_array_of_arrays():
    obj = {"pairs": [[1, 2], [3, 4]]}
    expected = (
        "pairs[2]:\n"
        "  - [2]: 1,2\n"
        "  - [2]: 3,4"
    )
    assert encode(obj) == expected

def test_empty_containers():
    assert encode({}) == ""
    assert encode({"items": []}) == "items[0]:"

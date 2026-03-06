import pytest
from mini_toon.decoder import decode

def test_primitives():
    assert decode("hello") == "hello"
    assert decode("true") is True
    assert decode("false") is False
    assert decode("null") is None
    assert decode("42") == 42
    assert decode("3.14") == 3.14
    assert decode('"05"') == "05"

def test_quoted_strings():
    assert decode('""') == ""
    assert decode('" hello "') == " hello "
    assert decode('"true"') == "true"
    assert decode('"42"') == "42"
    assert decode('"a:b"') == "a:b"

def test_simple_object():
    toon = (
        "id: 1\n"
        "name: Ada\n"
        "active: true"
    )
    assert decode(toon) == {"id": 1, "name": "Ada", "active": True}

def test_nested_object():
    toon = (
        "user:\n"
        "  id: 1\n"
        "  name: Ada"
    )
    assert decode(toon) == {"user": {"id": 1, "name": "Ada"}}

def test_primitive_array_inline():
    toon = "tags[3]: admin,ops,dev"
    assert decode(toon) == {"tags": ["admin", "ops", "dev"]}

def test_tabular_array():
    toon = (
        "items[2]{id,qty}:\n"
        "  1,5\n"
        "  2,3"
    )
    assert decode(toon) == {"items": [{"id": 1, "qty": 5}, {"id": 2, "qty": 3}]}

def test_mixed_array():
    toon = (
        "items[3]:\n"
        "  - 1\n"
        "  - a: 1\n"
        "  - x"
    )
    assert decode(toon) == {"items": [1, {"a": 1}, "x"]}

def test_root_array():
    toon = "[3]: x,y,z"
    assert decode(toon) == ["x", "y", "z"]

def test_array_of_arrays():
    toon = (
        "pairs[2]:\n"
        "  - [2]: 1,2\n"
        "  - [2]: 3,4"
    )
    assert decode(toon) == {"pairs": [[1, 2], [3, 4]]}

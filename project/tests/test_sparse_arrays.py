"""
Tests for Sparse Tabular Arrays - arrays where objects have heterogeneous keys.
A missing key is encoded as an empty unquoted cell; a real empty string is "".
"""
import json
import pytest
from mini_toon.encoder import encode
from mini_toon.decoder import decode


def _roundtrip(data):
    """Helper: encode to TOON then decode back and compare to original."""
    toon = encode(data)
    result = decode(toon)
    return result, toon


def test_missing_key_drops_in_output():
    """Objects with missing keys should round-trip without the missing key."""
    data = [
        {"id": 1, "name": "Alice", "brand": "Nike"},
        {"id": 2, "name": "Bob"},   # 'brand' is absent
        {"id": 3, "name": "Carol", "brand": "Adidas"},
    ]
    result, toon = _roundtrip(data)
    assert result[1] == {"id": 2, "name": "Bob"}
    assert "brand" not in result[1]


def test_missing_key_preserved_for_present_items():
    """Items that DO have the key should still decode correctly."""
    data = [
        {"id": 1, "name": "Alice", "brand": "Nike"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Carol", "brand": "Adidas"},
    ]
    result, _ = _roundtrip(data)
    assert result[0]["brand"] == "Nike"
    assert result[2]["brand"] == "Adidas"


def test_empty_string_value_is_preserved():
    """An actual empty string value (encoded as quoted "") must NOT be dropped."""
    data = [
        {"id": 1, "name": "Alice", "note": ""},   # real empty string
        {"id": 2, "name": "Bob",   "note": "hi"},
    ]
    result, _ = _roundtrip(data)
    assert result[0]["note"] == ""  # must still be present as empty string


def test_products_like_sparse_array():
    """Simulate the products.json pattern: product without brand field."""
    data = [
        {"id": 1, "title": "Mascara", "brand": "Essence", "price": 9.99},
        {"id": 16, "title": "Apple", "price": 1.99},   # no brand (like groceries)
        {"id": 6,  "title": "CK One", "brand": "Calvin Klein", "price": 49.99},
    ]
    result, toon = _roundtrip(data)
    assert result[1] == {"id": 16, "title": "Apple", "price": 1.99}
    assert "brand" not in result[1]
    assert result[0]["brand"] == "Essence"
    assert result[2]["brand"] == "Calvin Klein"


def test_all_missing_key_reverts_gracefully():
    """Moderate sparsity: shared keys survive, unique keys are dropped from other rows."""
    data = [
        {"id": 1, "type": "A", "aval": 10},
        {"id": 2, "type": "B", "bval": 20},
        {"id": 3, "type": "C", "cval": 30},
    ]
    result, toon = _roundtrip(data)
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2
    assert result[2]["id"] == 3


def test_full_roundtrip_json_equivalence():
    """Encode→TOON→Decode must produce identical JSON to original."""
    original = [
        {"x": 1, "y": 2, "z": 3},
        {"x": 4,          "z": 6},   # y missing
        {"x": 7, "y": 8          },   # z missing
    ]
    result, _ = _roundtrip(original)
    assert result[0] == original[0]
    assert result[1] == original[1]
    assert result[2] == original[2]

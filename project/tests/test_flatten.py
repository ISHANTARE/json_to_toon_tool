import pytest
from mini_toon.encoder import encode
from mini_toon.decoder import decode

def test_auto_flatten_arrays():
    data = {"commits": [
        {
            "id": 1,
            "author": {"name": "Alice", "alias": ["A1"]},
            "stats": {"add": 10}
        },
        {
            "id": 2,
            "author": {"name": "Bob", "alias": ["B1"]},
            "stats": {"add": 5}
        }
    ]}
    
    encoded = encode(data)
    # Ensure it generated a tabular array with flattened fields!
    assert "commits[2]{id,author.name,author.alias.0,stats.add}:" in encoded
    
    decoded = decode(encoded)
    assert decoded == data

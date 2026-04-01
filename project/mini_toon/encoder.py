"""
Encoder for translating JSON data structures into TOON v3.0 text format.
"""

from typing import Any, Dict, List
from .strings import encode_primitive, needs_quoting
from .types import EncodeError


def _is_primitive(value: Any) -> bool:
    """Check if value is a JSON primitive."""
    return value is None or isinstance(value, (str, int, float, bool))


def _flatten_item(data: Any, prefix: str = "") -> dict:
    """Recursively flattens a nested dictionary/list into a flat dict of primitives."""
    items = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{prefix}.{k}" if prefix else str(k)
            items.update(_flatten_item(v, new_key))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_key = f"{prefix}.{i}" if prefix else str(i)
            items.update(_flatten_item(v, new_key))
    else:
        if not _is_primitive(data):
            raise EncodeError(f"Cannot flatten non-primitive value of type {type(data)}")
        items[prefix] = data
    return items


def _check_tabular(items: list) -> tuple[list[str], list[dict]]:
    """
    Check if a list can be a tabular array (using flattening).
    Returns (fields, flattened_items). If it cannot, returns ([], [])
    """
    if not items:
        return [], []

    first_item = items[0]
    if not isinstance(first_item, dict):
        return [], []

    try:
        flat_items = [_flatten_item(item) for item in items]
    except Exception:
        return [], []

    # Gather the union of all keys across all flattened objects
    fields = []
    field_set = set()
    for flat_item in flat_items:
        for k in flat_item.keys():
            if k not in field_set:
                fields.append(k)
                field_set.add(k)

    # Protect against extreme sparsity (e.g. distinct objects creating massive comma bloat)
    total_cells = len(fields) * len(flat_items)
    filled_cells = sum(len(fi) for fi in flat_items)
    if total_cells > 0 and (filled_cells / total_cells) < 0.5:
        return [], []

    return fields, flat_items


def _encode_row(item: dict, fields: list[str], delim: str) -> str:
    """Encode a single object row in tabular format, handling missing keys sparsely."""
    parts = []
    for field in fields:
        if field in item:
            val = item[field]
            parts.append(encode_primitive(val, delim))
        else:
            # Leave cell entirely unquoted empty for missing fields
            parts.append("")
    return delim.join(parts)


def encode(data: Any, delimiter: str = ',') -> str:
    """
    Encode a JSON value (dict, list) to TOON string.
    """
    import json
    
    # Handle toJSON if present
    def _normalize(val: Any) -> Any:
        if hasattr(val, 'toJSON') and callable(val.toJSON):
            return _normalize(val.toJSON())
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in val.items()}
        if isinstance(val, list):
            return [_normalize(x) for x in val]
        return val

    data = _normalize(data)
    
    # Root level encoding
    out = []
    _encode_value(data, out, 0, None, delimiter)
    
    # Join with newlines
    return '\n'.join(out).strip()


def _encode_value(val: Any, out: list[str], depth: int, list_context: bool, delim: str):
    """Recursively encode values, adding lines to out array."""
    pad = ' ' * (depth * 2)
    
    if val is None or isinstance(val, (str, int, float, bool)):
        # Primitives at root level
        if depth == 0 and not list_context:
            out.append(encode_primitive(val, delim))
        else:
            raise EncodeError("Primitive value cannot appear outside object/array")
            
    elif isinstance(val, dict):
        _encode_object(val, out, depth, list_context, delim)
        
    elif isinstance(val, list):
        _encode_array(val, out, depth, list_context, delim)
        
    else:
        raise EncodeError(f"Unsupported type: {type(val)}")


def _encode_object(obj: dict, out: list[str], depth: int, list_context: bool, delim: str):
    """Encode a dictionary."""
    pad = ' ' * (depth * 2)

    # Empty object
    if not obj:
        if depth == 0 and not list_context:
            pass # Root empty object -> empty document
        return

    # Check for the list-item canonical pattern (tabular array as first field)
    # We'll handle this by just encoding normally, since list context is handled above
    
    for i, (k, v) in enumerate(obj.items()):
        
        # Determine if we need to prefix with "- "
        prefix = ''
        if list_context and i == 0:
            prefix = '- '
            # Depth for the first item is implicitly the parent depth + 1, 
            # but we write it on the same line as the hyphen
            key_pad = pad
        elif list_context:
            # Subsequent keys in a list-item object are indented
            prefix = '  '
            key_pad = pad
        else:
            key_pad = pad

        # Encode key
        key_str = k if not needs_quoting(k, delim) else f'"{k}"'
        
        # Object or array requires nesting
        if isinstance(v, (dict, list)):
            if isinstance(v, list):
                # Array headers go next to key
                header = _get_array_header(v, delim)
                out.append(f"{key_pad}{prefix}{key_str}{header}:")
                # Write array contents
                _encode_array_contents(v, out, depth + 1 if not list_context else depth + 1, delim)
            else:
                # Nested object
                if not v:
                    # Empty nested object
                    out.append(f"{key_pad}{prefix}{key_str}:")
                else:
                    out.append(f"{key_pad}{prefix}{key_str}:")
                    _encode_object(v, out, depth + 1, False, delim)
        else:
            # Primitive value
            val_str = encode_primitive(v, delim)
            out.append(f"{key_pad}{prefix}{key_str}: {val_str}")


def _get_array_header(arr: list, delim: str) -> str:
    """Generate the TOON array header [N] or [N]{fields}."""
    length = len(arr)
    # Check if tabular
    fields, _ = _check_tabular(arr)
    
    
    d_str = ''
    if delim == '\t': d_str = '\\t'
    elif delim == '|': d_str = '|'
    
    if fields:
        fields_str = ','.join(fields)
        return f"[{length}{d_str}]{{{fields_str}}}"
    else:
        return f"[{length}{d_str}]"


def _encode_array(arr: list, out: list[str], depth: int, list_context: bool, delim: str):
    """Encode an array at root level or nested inside array (since object handles its own array fields)."""
    pad = ' ' * (depth * 2)
    
    prefix = '- ' if list_context else ''
    
    header = _get_array_header(arr, delim)
    out.append(f"{pad}{prefix}{header}:")
    _encode_array_contents(arr, out, depth + 1, delim)


def _encode_array_contents(arr: list, out: list[str], content_depth: int, delim: str):
    """Write the contents of an array (assumes header was already written)."""
    if not arr:
        return
        
    pad = ' ' * (content_depth * 2)
    
    # 1. Tabular format
    fields, flat_arr = _check_tabular(arr)
    if fields:
        for item in flat_arr:
            row = _encode_row(item, fields, delim)
            out.append(f"{pad}{row}")
        return
        
    # 2. Primitive inline format
    if all(_is_primitive(x) for x in arr):
        parts = [encode_primitive(x, delim) for x in arr]
        out[-1] += f" {delim.join(parts)}"
        return
        
    # 3. List-item format (mixed or non-uniform)
    for item in arr:
        if _is_primitive(item):
            out.append(f"{pad}- {encode_primitive(item, delim)}")
        elif isinstance(item, list):
            # Array of arrays
            _encode_array(item, out, content_depth, True, delim)
        elif isinstance(item, dict):
            # Object list item
            if not item:
                out.append(f"{pad}- ")
            else:
                _encode_object(item, out, content_depth, True, delim)


# Public API alias
def encode_json(data: Any, delimiter: str = ',') -> str:
    return encode(data, delimiter)

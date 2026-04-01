import re
from typing import Any, Tuple, Optional
from .scanner import scan, Line
from .strings import unescape
from .types import DecodeError

_HEADER_RE = re.compile(
    r'^(?:(?P<key>.*?)\s*)?\[(?P<length>\d+)(?P<delim>[,|\t])?\](?:\{(?P<fields>.*?)\})?\s*$'
)

def _unflatten_dict(flat_dict: dict) -> dict:
    """Unflatten a dictionary with dot-notation keys into a nested structure."""
    if not flat_dict:
        return {}
        
    if not any('.' in str(k) for k in flat_dict.keys()):
        return flat_dict
        
    result = {}
    for key, value in flat_dict.items():
        parts = str(key).split('.')
        current = result
        
        for i, part in enumerate(parts[:-1]):
            next_part = parts[i+1]
            next_is_list = next_part.isdigit()
            
            if isinstance(current, list):
                idx = int(part)
                while len(current) <= idx:
                    current.append([] if next_is_list else {})
                current = current[idx]
            else:
                if part not in current:
                    current[part] = [] if next_is_list else {}
                current = current[part]
                
        last_part = parts[-1]
        if isinstance(current, list):
            idx = int(last_part)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[last_part] = value
            
    return result

def split_delimited(text: str, delimiter: str) -> list[str]:
    if '"' not in text and '\\' not in text:
        return [part.strip() for part in text.split(delimiter)]

    out = []
    buf = []
    in_quotes = False
    escape_next = False
    
    for char in text:
        if escape_next:
            buf.append(char)
            escape_next = False
            continue
            
        if char == '\\' and in_quotes:
            buf.append(char)
            escape_next = True
            continue
            
        if char == '"':
            in_quotes = not in_quotes
            buf.append(char)
            continue
            
        if char == delimiter and not in_quotes:
            out.append(''.join(buf).strip())
            buf = []
            continue
            
        buf.append(char)
        
    out.append(''.join(buf).strip())
    return out


def _is_primitive_line(text: str) -> bool:
    in_quotes = False
    escape_next = False
    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == '\\' and in_quotes:
            escape_next = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if char == ':' and not in_quotes:
            return False
    return True

def parse_value(text: str) -> Any:
    text = text.strip()
    if not text:
        return ""
        
    if text.startswith('"'):
        if not text.endswith('"') or len(text) == 1:
            if text == '"': return text
            raise DecodeError("Unclosed string")
        return unescape(text[1:-1])
        
    if text == "true": return True
    if text == "false": return False
    if text == "null": return None
    
    if text.startswith('0') and len(text) > 1 and not text.startswith('0.'):
        return text
    if text.startswith('-0') and len(text) > 2 and not text.startswith('-0.'):
        return text
        
    try:
        if '.' in text or 'e' in text.lower():
            return float(text)
        return int(text)
    except ValueError:
        return text

def parse_key(text: str) -> str:
    text = text.strip()
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        return unescape(text[1:-1])
    return text


def _parse_array_contents_gen(
    lines: list[Line], 
    start: int, 
    depth: int, 
    length: int, 
    fields: Optional[list[str]], 
    delim: str
):
    arr = []
    i = start
    
    if length == 0:
        return arr, i
        
    if fields is not None:
        for _ in range(length):
            if i >= len(lines):
                raise DecodeError(f"Unexpected EOF while parsing tabular array of length {length}")
            line = lines[i]
            if line.depth < depth:
                raise DecodeError(f"Unexpected un-indent in tabular array at line {line.number}")
                
            parts = split_delimited(line.text, delim)
            obj = {}
            for j, field in enumerate(fields):
                val_text = parts[j] if j < len(parts) else ""
                # Empty unquoted cell = missing key (sparse tabular array)
                # Quoted empty string "" is preserved as an actual empty string value
                if val_text == "":
                    continue  # skip - key was absent in original object
                obj[parse_key(field)] = parse_value(val_text)
                
            arr.append(_unflatten_dict(obj))
            i += 1
            
        return arr, i
        
    if i >= len(lines) or lines[i].depth < depth:
        raise DecodeError(f"Expected array contents for {length} items")
        
    first_line = lines[i]
    is_list_format = first_line.text.startswith('- ') or first_line.text == '-'
    
    if not is_list_format:
        parts = split_delimited(first_line.text, delim)
        for part in parts:
            arr.append(parse_value(part))
        return arr, i + 1
        
    count = 0
    while i < len(lines) and count < length:
        line = lines[i]
        if line.depth < depth:
            break
            
        if not (line.text.startswith('- ') or line.text == '-'):
            i += 1
            continue
            
        content = line.text[1:].strip() 
        
        # Simulate an anonymous line to parse it cleanly using parse_block logic
        dummy_line = Line(content, depth + 1, line.number)
        temp_lines = [dummy_line]
        
        k = i + 1
        while k < len(lines) and lines[k].depth > depth:
            temp_lines.append(lines[k])
            k += 1
            
        # Try to parse the block or primitive
        if content == '':
            if len(temp_lines) > 1:
                val, _ = yield (_parse_block_gen, temp_lines, 1, depth + 1)
                arr.append(val)
            else:
                arr.append(None)
        elif ':' in content:
            val, _ = yield (_parse_block_gen, temp_lines, 0, depth + 1)
            # Edge case if val is an array but it's anonymous
            if type(val) is dict and len(val) == 1 and '' in val:
                val = val['']
            arr.append(val)
        else:
            arr.append(parse_value(content))
            
        count += 1
        i = k
        
    return arr, i


def _parse_block_gen(lines: list[Line], start: int, depth: int):
    obj = {}
    i = start
    is_object = False
    
    while i < len(lines):
        line = lines[i]
        
        if line.depth < depth:
            break
            
        if line.depth > depth:
            raise DecodeError(f"Invalid indent at line {line.number}: expected {depth}, got {line.depth}")
            
        text = line.text
        
        if ':' not in text:
            # Check if anonymous array header
            m = _HEADER_RE.match(text) if '[' in text else None
            if m and not m.group('key'):
                length = int(m.group('length'))
                delim = m.group('delim') or ','
                fields_str = m.group('fields')
                fields = split_delimited(fields_str.strip(), delim) if fields_str else None
                arr, next_i = yield (_parse_array_contents_gen, lines, i + 1, depth + 1, length, fields, delim)
                
                # We return it bound to empty string for the list-item hack, or just return array
                # If we are parsing an anonymous block (from list item), we can just return the array
                if is_object:
                    obj[''] = arr
                    i = next_i
                    continue
                return arr, next_i
            else:
                raise DecodeError(f"Missing ':' at line {line.number}")
            
        is_object = True
        key_raw, rest = text.split(':', 1)
        key_raw = key_raw.strip()
        rest = rest.strip()
        
        m = _HEADER_RE.match(key_raw) if '[' in key_raw else None
        if m:
            key_str = m.group('key')
            key = parse_key(key_str) if key_str else ''
            length = int(m.group('length'))
            delim = m.group('delim') or ','
            fields_str = m.group('fields')
            fields = split_delimited(fields_str.strip(), delim) if fields_str else None
            
            if rest:
                parts = split_delimited(rest, delim)
                arr = [parse_value(p) for p in parts] if rest else []
                obj[key] = arr
                i += 1
                continue
                
            arr, i = yield (_parse_array_contents_gen, lines, i + 1, depth + 1, length, fields, delim)
            
            if key:
                obj[key] = arr
            else:
                return arr, i
            continue
            
        key = parse_key(key_raw)
        
        if not rest:
            val, i = yield (_parse_block_gen, lines, i + 1, depth + 1)
            obj[key] = val
        else:
            obj[key] = parse_value(rest)
            i += 1
            
    return obj, i

def trampoline(generator_func, *args):
    """Executes generator-based recursion on a heap stack to prevent RecursionError."""
    stack = [generator_func(*args)]
    return_value = None
    
    while stack:
        try:
            # Send the return value of the last child generator to the current one
            call = stack[-1].send(return_value)
            return_value = None
            
            # If the generator yielded a tuple of (func, *args), we push the new generator
            if isinstance(call, tuple) and call and callable(call[0]):
                stack.append(call[0](*call[1:]))
            else:
                raise DecodeError("Expected a generator function tuple to be yielded")
        except StopIteration as e:
            # Generator finished, capture its return value
            stack.pop()
            return_value = e.value
            
    return return_value

def parse_block(lines: list[Line], start: int, depth: int) -> Tuple[Any, int]:
    return trampoline(_parse_block_gen, lines, start, depth)

def _parse_array_contents(lines, start, depth, length, fields, delim):
    return trampoline(_parse_array_contents_gen, lines, start, depth, length, fields, delim)

def decode(text: str) -> Any:
    lines = scan(text)
    
    if not lines:
        return {}
        
    if len(lines) == 1:
        text_line = lines[0].text
        if _is_primitive_line(text_line) and not _HEADER_RE.match(text_line):
            return parse_value(text_line)
            
    first_line = lines[0].text
    if ':' in first_line:
        key_raw, rest = first_line.split(':', 1)
        m = _HEADER_RE.match(key_raw.strip()) if '[' in key_raw else None
    else:
        m = _HEADER_RE.match(first_line.strip()) if '[' in first_line else None
        rest = ""

    if m and not m.group('key'):
        length = int(m.group('length'))
        delim = m.group('delim') or ','
        fields_str = m.group('fields')
        fields = split_delimited(fields_str.strip(), delim) if fields_str else None
        
        if rest.strip():
            parts = split_delimited(rest.strip(), delim)
            return [parse_value(p) for p in parts]
            
        arr, pos = trampoline(_parse_array_contents_gen, lines, 1, 0, length, fields, delim)
        return arr

    result, pos = trampoline(_parse_block_gen, lines, 0, 0)
    
    if pos < len(lines):
        raise DecodeError(f"Extra content after root at line {lines[pos].number}")
        
    return result

def decode_toon(text: str) -> Any:
    return decode(text)

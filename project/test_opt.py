import json
import tiktoken
import sys
sys.path.append('project')
import mini_toon.encoder as encoder

# Monkey patch encoder for 1 space indentation
def _encode_value(val, out, depth, list_context, delim):
    pad = ' ' * depth
    if val is None or isinstance(val, (str, int, float, bool)):
        if depth == 0 and not list_context:
            out.append(encoder.encode_primitive(val, delim))
        else:
            raise encoder.EncodeError("Primitive value cannot appear outside object/array")
    elif isinstance(val, dict):
        encoder._encode_object(val, out, depth, list_context, delim)
    elif isinstance(val, list):
        encoder._encode_array(val, out, depth, list_context, delim)
    else:
        raise encoder.EncodeError(f"Unsupported type: {type(val)}")

def _encode_object(obj, out, depth, list_context, delim):
    pad = ' ' * depth
    if not obj:
        if depth == 0 and not list_context:
            pass
        return
    for i, (k, v) in enumerate(obj.items()):
        prefix = ''
        if list_context and i == 0:
            prefix = '- '
            key_pad = pad
        elif list_context:
            prefix = '  '
            key_pad = pad
        else:
            key_pad = pad
        key_str = k if not encoder.needs_quoting(k, delim) else f'"{k}"'
        if isinstance(v, (dict, list)):
            if isinstance(v, list):
                header = encoder._get_array_header(v, delim)
                out.append(f"{key_pad}{prefix}{key_str}{header}:")
                encoder._encode_array_contents(v, out, depth + 1 if not list_context else depth + 1, delim)
            else:
                if not v:
                    out.append(f"{key_pad}{prefix}{key_str}:")
                else:
                    out.append(f"{key_pad}{prefix}{key_str}:")
                    encoder._encode_object(v, out, depth + 1, False, delim)
        else:
            val_str = encoder.encode_primitive(v, delim)
            out.append(f"{key_pad}{prefix}{key_str}: {val_str}")
            
def _encode_array(arr, out, depth, list_context, delim):
    pad = ' ' * depth
    prefix = '- ' if list_context else ''
    header = encoder._get_array_header(arr, delim)
    out.append(f"{pad}{prefix}{header}:")
    encoder._encode_array_contents(arr, out, depth + 1, delim)
    
def _encode_array_contents(arr, out, content_depth, delim):
    if not arr: return
    pad = ' ' * content_depth
    fields = encoder._get_tabular_fields(arr)
    if fields:
        for item in arr:
            row = encoder._encode_row(item, fields, delim)
            out.append(f"{pad}{row}")
        return
    if all(encoder._is_primitive(x) for x in arr):
        parts = [encoder.encode_primitive(x, delim) for x in arr]
        out[-1] += f" {delim.join(parts)}"
        return
    for item in arr:
        if encoder._is_primitive(item):
            out.append(f"{pad}- {encoder.encode_primitive(item, delim)}")
        elif isinstance(item, list):
            encoder._encode_array(item, out, content_depth, True, delim)
        elif isinstance(item, dict):
            if not item:
                out.append(f"{pad}- ")
            else:
                encoder._encode_object(item, out, content_depth, True, delim)

encoder._encode_value = _encode_value
encoder._encode_object = _encode_object
encoder._encode_array = _encode_array
encoder._encode_array_contents = _encode_array_contents
encoder.encode(True) # Force compile

with open('project/real_samples/github_commits.json', 'r', encoding='utf-8') as f: data = json.load(f)
t = encoder.encode(data)
enc = tiktoken.get_encoding('cl100k_base')
print(f'TOON 1-Space: {len(enc.encode(t))}')

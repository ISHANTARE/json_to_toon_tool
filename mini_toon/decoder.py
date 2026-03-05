from .scanner import scan
from .strings import unescape
from .types import DecodeError

def parse_value(text):

    text = text.strip()

    # String
    if text.startswith('"'):

        if not text.endswith('"'):
            raise DecodeError("Unclosed string")

        return unescape(text[1:-1])

    # Boolean
    if text == "true":
        return True

    if text == "false":
        return False

    # Null
    if text == "null":
        return None

    # Number
    if "." in text:
        return float(text)

    return int(text)


def parse_block(lines, start, depth):

    obj = {}
    i = start

    while i < len(lines):

        line = lines[i]

        if line.depth < depth:
            break

        if line.depth > depth:
            raise DecodeError(f"Invalid indent at line {line.number}")

        text = line.text

        if ":" not in text:
            raise DecodeError(f"Missing ':' at line {line.number}")

        key, rest = text.split(":", 1)
        key = key.strip()
        rest = rest.strip()

        # Nested object
        if not rest:

            value, i = parse_block(lines, i + 1, depth + 1)
            obj[key] = value

        # Inline array
        elif rest.startswith("["):

            obj[key] = parse_array(rest)

            i += 1

        else:
            obj[key] = parse_value(rest)
            i += 1

    return obj, i


def parse_array(text):

    if not text.endswith("]"):
        raise DecodeError("Unclosed array")

    text = text[1:-1]

    if not text.strip():
        return []

    parts = split_array(text)

    return [parse_value(p) for p in parts]


def split_array(text):

    out = []
    buf = ""
    quoted = False

    i = 0

    while i < len(text):

        c = text[i]

        if c == '"' and (i == 0 or text[i-1] != "\\"):
            quoted = not quoted

        if c == "," and not quoted:
            out.append(buf.strip())
            buf = ""
        else:
            buf += c

        i += 1

    if buf:
        out.append(buf.strip())

    return out


def decode_toon(text):

    lines = scan(text)

    if not lines:
        return {}

    result, pos = parse_block(lines, 0, 0)

    if pos != len(lines):
        raise DecodeError("Extra content after root")

    return result

"""
String handling for TOON encoding and decoding.

Implements the quoting rules from the TOON v3.0 spec:
- Strings are unquoted by default (saves tokens)
- Quoted only when they could be misinterpreted as another type
  or contain syntax-breaking characters
"""

import re

# Patterns that look like numbers (integers, decimals, exponents, leading zeros)
_NUMBER_RE = re.compile(
    r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$'
)

# Leading-zero numbers like "05", "007" — these are strings in TOON
_LEADING_ZERO_RE = re.compile(r'^0\d+')

# Characters that always force quoting
_SPECIAL_CHARS = set(':"\\[]{}')

# Control characters that force quoting
_CONTROL_CHARS = {'\n', '\r', '\t'}

# Reserved literal words
_RESERVED = {'true', 'false', 'null'}


def needs_quoting(value: str, delimiter: str = ',') -> bool:
    """
    Determine if a string value needs to be quoted in TOON output.
    
    A string must be quoted if:
    - It's empty
    - It has leading or trailing whitespace
    - It equals true, false, or null
    - It looks like a number (including leading zeros)
    - It contains special chars: colon, quote, backslash, brackets, braces
    - It contains control characters (newline, tab, carriage return)
    - It contains the active delimiter
    - It equals "-" or starts with "- "
    """
    # Empty string
    if not value:
        return True

    # Leading or trailing whitespace
    if value != value.strip():
        return True

    # Reserved words (case-sensitive)
    if value in _RESERVED:
        return True

    # Looks like a number
    if _NUMBER_RE.match(value) or _LEADING_ZERO_RE.match(value):
        return True

    # Starts with dash (list item marker conflict)
    if value == '-' or value.startswith('-'):
        return True

    # Contains special characters
    if any(c in _SPECIAL_CHARS for c in value):
        return True

    # Contains control characters
    if any(c in _CONTROL_CHARS for c in value):
        return True

    # Contains the active delimiter
    if delimiter in value:
        return True

    return False


def escape(s: str) -> str:
    """
    Escape a string for TOON quoted output.
    Only 5 escape sequences are valid in TOON:
    \\  \"  \\n  \\r  \\t
    """
    return (
        s.replace('\\', '\\\\')
         .replace('"', '\\"')
         .replace('\n', '\\n')
         .replace('\r', '\\r')
         .replace('\t', '\\t')
    )


def unescape(s: str) -> str:
    """
    Unescape a TOON quoted string back to its original form.
    """
    out = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == 'n':
                out.append('\n')
            elif nxt == 'r':
                out.append('\r')
            elif nxt == 't':
                out.append('\t')
            elif nxt == '"':
                out.append('"')
            elif nxt == '\\':
                out.append('\\')
            else:
                # Unknown escape — pass through in lenient mode
                out.append(nxt)
            i += 2
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def encode_string(value: str, delimiter: str = ',') -> str:
    """
    Encode a string value for TOON output.
    Returns the string unquoted if safe, quoted otherwise.
    """
    if needs_quoting(value, delimiter):
        return f'"{escape(value)}"'
    return value


def encode_primitive(value, delimiter: str = ',') -> str:
    """
    Encode any JSON primitive to its TOON text representation.
    """
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, float):
        # Canonical decimal form — no trailing zeros, no exponent
        if value != value:  # NaN
            return 'null'
        if value == float('inf') or value == float('-inf'):
            return 'null'
        # Remove negative zero
        if value == 0.0:
            return '0'
        # Format without unnecessary trailing zeros
        formatted = f'{value}'
        # Python already does a decent job, but let's clean up
        if 'e' in formatted or 'E' in formatted:
            # Convert exponent notation to decimal
            formatted = f'{value:.20f}'.rstrip('0').rstrip('.')
        return formatted
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return encode_string(value, delimiter)

    raise TypeError(f"Not a JSON primitive: {type(value)}")

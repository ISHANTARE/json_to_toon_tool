from .strings import escape


def encode(value, depth=0, indent=2):

    pad = " " * (depth * indent)

    # Object
    if isinstance(value, dict):

        out = []

        for k, v in value.items():

            if isinstance(v, (dict, list)):
                out.append(f"{pad}{k}:")
                out.append(encode(v, depth + 1))
            else:
                out.append(f"{pad}{k}: {encode(v, 0)}")

        return "\n".join(out)

    # Array
    if isinstance(value, list):

        parts = []

        for v in value:
            parts.append(encode(v, 0))

        return "[" + ", ".join(parts) + "]"

    # String
    if isinstance(value, str):
        return f'"{escape(value)}"'

    # Boolean
    if isinstance(value, bool):
        return "true" if value else "false"

    # Null
    if value is None:
        return "null"

    return str(value)


def encode_json(data):

    return encode(data)

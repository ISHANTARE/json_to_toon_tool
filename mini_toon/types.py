JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list | dict


class DecodeError(Exception):
    pass

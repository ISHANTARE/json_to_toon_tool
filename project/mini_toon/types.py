"""
Type definitions and custom exceptions for the mini_toon library.
"""

# Type aliases for JSON data model
JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list | dict


class DecodeError(Exception):
    """Raised when TOON text cannot be parsed."""
    pass


class EncodeError(Exception):
    """Raised when data cannot be encoded to TOON."""
    pass

"""
Scanner for reading TOON text into line objects with depth tracking.
"""

from dataclasses import dataclass


@dataclass
class Line:
    text: str
    depth: int
    number: int


def scan(text: str, indent: int = 2) -> list[Line]:
    """
    Parse a string into a list of Line objects, tracking indentation depth.
    Empty lines or whitespace-only lines are ignored.
    """
    lines = []
    
    # Process text line by line
    raw_lines = text.split('\n')
    
    for i, raw in enumerate(raw_lines):
        # 1-based line number for error reporting
        num = i + 1
        
        # Skip empty or whitespace-only lines
        if not raw.strip():
            continue
            
        # Count leading spaces
        spaces = len(raw) - len(raw.lstrip(' '))
        
        # Calculate depth (must be uniform based on indent size)
        depth = spaces // indent
        
        # We strip leading whitespace but preserve trailing 
        # (though trailing whitespace usually gets stripped during parsing value)
        content = raw.lstrip(' ')
        
        lines.append(Line(content, depth, num))

    return lines

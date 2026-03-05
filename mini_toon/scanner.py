from dataclasses import dataclass


@dataclass
class Line:

    text: str
    depth: int
    number: int


def scan(text: str, indent=2):

    lines = []
    num = 1

    for raw in text.splitlines():

        if not raw.strip():
            num += 1
            continue

        spaces = len(raw) - len(raw.lstrip(" "))
        depth = spaces // indent

        content = raw.strip()

        lines.append(Line(content, depth, num))
        num += 1

    return lines

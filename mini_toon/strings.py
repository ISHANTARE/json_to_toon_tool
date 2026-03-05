def escape(s: str) -> str:

    return (
        s.replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\n", "\\n")
         .replace("\t", "\\t")
    )


def unescape(s: str) -> str:

    out = ""
    i = 0

    while i < len(s):

        if s[i] == "\\":
            i += 1

            if s[i] == "n":
                out += "\n"
            elif s[i] == "t":
                out += "\t"
            else:
                out += s[i]
        else:
            out += s[i]

        i += 1

    return out

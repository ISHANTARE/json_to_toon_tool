import json
import sys
import os

import mini_toon


def convert(json_file, toon_file):

    # Read JSON
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:
        print("Error reading JSON:", e)
        return

    # Convert to TOON
    try:
        toon_text = mini_toon.encode(data)

    except Exception as e:
        print("Encoding error:", e)
        return

    # Save TOON
    try:
        with open(toon_file, "w", encoding="utf-8") as f:
            f.write(toon_text)

    except Exception as e:
        print("Error writing TOON:", e)
        return

    print("✅ Conversion Successful!")
    print("JSON → TOON")
    print("Input :", json_file)
    print("Output:", toon_file)


def main():

    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert_json_to_toon.py input.json output.toon")
        return

    json_file = sys.argv[1]
    toon_file = sys.argv[2]

    if not os.path.exists(json_file):
        print("File not found:", json_file)
        return

    convert(json_file, toon_file)


if __name__ == "__main__":
    main()

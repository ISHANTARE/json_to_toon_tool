import json
import sys
import csv
import os

import tiktoken
import mini_toon


def count_tokens(text, model="gpt-4o-mini"):
    """
    Count tokens using OpenAI tokenizer.
    """
    try:
        enc = tiktoken.encoding_for_model(model)
    except:
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(text))


def benchmark(json_file, csv_file="results.csv"):

    # Read JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert
    json_text = json.dumps(data, indent=2)
    toon_text = mini_toon.encode(data)

    # Count tokens
    json_tokens = count_tokens(json_text)
    toon_tokens = count_tokens(toon_text)

    savings = json_tokens - toon_tokens
    percent = (savings / json_tokens) * 100

    # Print
    print("----- BENCHMARK RESULT -----")
    print("JSON tokens :", json_tokens)
    print("TOON tokens :", toon_tokens)
    print("Saved       :", savings)
    print("Reduction % :", round(percent, 2))

    # Save to CSV
    write_header = not os.path.exists(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow([
                "file",
                "json_tokens",
                "toon_tokens",
                "saved_tokens",
                "reduction_percent"
            ])

        writer.writerow([
            json_file,
            json_tokens,
            toon_tokens,
            savings,
            round(percent, 2)
        ])


def main():

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python benchmark_tokens.py input.json")
        return

    benchmark(sys.argv[1])


if __name__ == "__main__":
    main()

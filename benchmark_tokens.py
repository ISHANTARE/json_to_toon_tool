import json
import sys
import csv
import os
import time

try:
    import tiktoken
    has_tiktoken = True
except ImportError:
    has_tiktoken = False
    print("Warning: tiktoken not installed. Token counts will be 0.")

try:
    import yaml
    has_yaml = True
except ImportError:
    has_yaml = False
    print("Warning: pyyaml not installed. YAML stats will be skipped.")

import mini_toon

def count_tokens(text: str, model="gpt-4o-mini") -> int:
    if not has_tiktoken:
        return 0
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def run_benchmarks(sample_dir="samples", output_csv="benchmark_results.csv"):
    if not os.path.isdir(sample_dir):
        # Fallback to local file if dir doesn't exist
        files = ["sample.json"] if os.path.exists("sample.json") else []
    else:
        files = [os.path.join(sample_dir, f) for f in os.listdir(sample_dir) if f.endswith(".json")]
        if os.path.exists("sample.json"):
            files.append("sample.json")

    results = []

    print(f"{'File':<25} | {'Format':<12} | {'Tokens':<8} | {'Bytes':<8} | {'Time (ms)':<9} | {'Savings vs JSON':<15}")
    print("-" * 90)

    for file_path in files:
        file_name = os.path.basename(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        formats_data = {}

        # 1. JSON Pretty
        t0 = time.time()
        json_pretty = json.dumps(data, indent=2)
        t_json = (time.time() - t0) * 1000
        formats_data["JSON (Pretty)"] = {
            "text": json_pretty, "time": t_json
        }

        # 2. JSON Compact
        t0 = time.time()
        json_compact = json.dumps(data, separators=(',', ':'))
        t_compact = (time.time() - t0) * 1000
        formats_data["JSON (Compact)"] = {
            "text": json_compact, "time": t_compact
        }

        # 3. YAML
        if has_yaml:
            t0 = time.time()
            yaml_text = yaml.dump(data, sort_keys=False)
            t_yaml = (time.time() - t0) * 1000
            formats_data["YAML"] = {
                "text": yaml_text, "time": t_yaml
            }

        # 4. TOON
        t0 = time.time()
        toon_text = mini_toon.encode(data)
        t_toon = (time.time() - t0) * 1000
        formats_data["TOON"] = {
            "text": toon_text, "time": t_toon
        }

        # Calculate baseline
        baseline_tokens = count_tokens(formats_data["JSON (Pretty)"]["text"])

        for fmt_name, fmt_info in formats_data.items():
            text = fmt_info["text"]
            ms = fmt_info["time"]
            tokens = count_tokens(text)
            bytes_size = len(text.encode('utf-8'))
            
            savings = 0.0
            if baseline_tokens > 0 and fmt_name != "JSON (Pretty)":
                savings = ((baseline_tokens - tokens) / baseline_tokens) * 100

            savings_str = f"{savings:+.1f}%" if fmt_name != "JSON (Pretty)" else "---"
            if fmt_name == "TOON" and savings > 0:
                savings_str = f"\033[92m{savings_str}\033[0m" # Green if positive
            
            print(f"{file_name:<25} | {fmt_name:<12} | {tokens:<8} | {bytes_size:<8} | {ms:<9.2f} | {savings_str:<15}")
            
            results.append({
                "File": file_name,
                "Format": fmt_name,
                "Tokens": tokens,
                "Bytes": bytes_size,
                "Time_ms": round(ms, 2),
                "Savings_vs_JSON_pct": round(savings, 2)
            })
        print("-" * 90)

    # Save CSV
    keys = ["File", "Format", "Tokens", "Bytes", "Time_ms", "Savings_vs_JSON_pct"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n✅ Benchmarks complete. Saved full report to '{output_csv}'.")

def main():
    run_benchmarks()

if __name__ == "__main__":
    main()

# JSON to TOON Converter & Benchmark Toolkit

A comprehensive, 100% spec-compliant toolkit for **TOON (Token Optimized Object Notation) v3.0**, built specifically for Python environments. This project provides everything you need to serialize/deserialize TOON data, visualize the reductions in a browser, and run hard data benchmarks against JSON to support research papers or backend optimizations.

## 🌟 Why TOON?

TOON is designed to structure arbitrary JSON data into a prompt-friendly syntax that drastically reduces the number of AI tokens consumed by Large Language Models (LLMs). Depending on the shape of your data, it can save anywhere from **25% to over 60%** in token costs compared to standard JSON. It does this by:
1. Stripping away heavy syntax like `{`, `}`, and `"` where unnecessary.
2. Utilizing highly compressible CSV-like **Tabular Arrays** for uniform objects.
3. Leveraging YAML-like indentation for hierarchy without the aggressive strictness.

This toolkit was specifically engineered to be a powerful foundation for building review papers and testing pipelines determining the true LLM token-efficiency of TOON versus JSON or YAML.

---

## 🚀 Features

- **100% Spec Compliant Core:** Implements all advanced TOON v3.0 specs including Tabular Arrays (`[N]{fields}`), List Models, Inline Arrays, strict string quoting rules, empty node handling, and proper scalar parsing.
- **Benchmark Suite:** Compare LLM token costs (`cl100k_base` via `tiktoken`), exact byte sizes, and runtime execution speed against localized JSON (Pretty & Compact) and YAML formats.
- **Modern Web Interface:** A premium local server serving an interactive "Glassmorphism" UI for real-time bidirectional encoding/decoding and token visualization.
- **Lossless CLI Tool:** Built-in headless scripts for bulk format conversion and native round-trip assertions.

---

## 📊 Benchmark Findings

We conducted extensive token benchmarking on a suite of diverse data layouts. The results highlight exactly where TOON excels and where traditional formats hold their ground.

*Tokens measured using OpenAI's `cl100k_base` encoding.*

### 1. Tabular Arrays (Highly Uniform Data)
*File: `flat_employees.json` (Array of objects sharing identical keys)*
* **JSON (Pretty):** 507 tokens (0% savings)
* **JSON (Compact):** 297 tokens (~41% savings)
* **YAML:** 362 tokens (~28% savings)
* **TOON:** **185 tokens (~63.5% savings)**
> **Finding:** TOON maps highly uniform objects into its specialized Tabular format (`key[N]{fields}`), completely eliminating key-repetition. This results in massive 63% cost reductions over standard JSON.

### 2. Time-Series Data (Uniform Primitives)
*File: `timeseries.json`*
* **JSON (Pretty):** 492 tokens
* **TOON:** **280 tokens (~43.1% savings)**
> **Finding:** Numeric-heavy sequential data still benefits heavily from the tabular mapping, keeping numbers raw and separated purely by layout delimiters.

### 3. Deeply Nested / Mixed Configuration (Sparse Data)
*Files: `nested_config.json`, `mixed_logs.json`*
* **JSON (Pretty):** 228 - 257 tokens
* **JSON (Compact):** 134 - 152 tokens (~41% savings)
* **TOON:** 170 - 184 tokens (~25-28% savings)
> **Finding:** When data lacks uniformity (meaning objects cannot be collapsed into tables), TOON performs similarly to YAML using its fallback List-Item (`-`) format. In these specific heterogeneous layouts, JSON Compact currently outperforms TOON slightly by shedding all whitespace, whereas TOON relies on indents to define structure. 

### Conclusion
TOON is unbeatably efficient for **Arrays of Objects (tabular data)** and simple flat maps, making it exceptional for database dumps, function-calling payloads, and tabular context injection. For deeply nested, highly irregular JSON config trees, Compact JSON remains slightly more token efficient due to whitespace erasure.

---

## 🛠️ Usage & Installation

### Requirements
Ensure you are using Python 3.8+
```bash
git clone https://github.com/your-repo/json-to-toon.git
cd json-to-toon

# Install dependencies for Token counting and YAML tests
pip install tiktoken pyyaml pytest
```

### 1. Python Library (`mini_toon`)
The core library operates entirely on native dictionaries and lists, identical to the `json` module API.

```python
import mini_toon

data = { "players": [{"id": 1, "score": 90}, {"id": 2, "score": 140}] }

# Encode Python dict to TOON text
toon_text = mini_toon.encode(data)
print(toon_text)
# players[2]{id,score}:
# 1,90
# 2,140

# Decode TOON text back to Python dict
parsed = mini_toon.decode(toon_text)
```

### 2. Interactive Web UI
For visual review, side-by-side JSON editing, and living token savings charts:
```bash
python server.py
# 🚀 TOON Web Converter started at http://localhost:8000
```
Open `localhost:8000` in any web browser and select a sample from the toolbar.

### 3. Headless CLI (`toon_cli.py`)
Run conversions and automatically verify parsing logic straight from the terminal. 

**JSON ➔ TOON (with stats and round-trip verification):**
```bash
python toon_cli.py input.json output.toon --stats --roundtrip
```

**TOON ➔ JSON:**
```bash
python toon_cli.py data.toon output.json
```

### 4. Running the Benchmark Suite
To generate the metrics and spreadsheets used in the findings above:
```bash
# Add your own custom JSON structures into the /samples/ directory
python benchmark_tokens.py
```
This produces a terminal table across all files and updates `benchmark_results.csv`.

---

## 🧪 Testing
The library includes 19 rigorous `pytest` assertion blocks validating parser integrity, string quoting rules (like handling internal colons and arrays), and nested depth bounds.

```bash
python -m pytest tests/ -v
```

> Built to enable next-generation AI pipelines. Enjoy reduced context weight!

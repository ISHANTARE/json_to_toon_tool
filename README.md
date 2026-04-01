# JSON → TOON Converter Tool

A Python implementation of **Token-Oriented Object Notation (TOON)** with novel algorithmic extensions that outperform the official specification on real-world heterogeneous API datasets.

---

## What is TOON?

TOON (Token-Oriented Object Notation) is a data serialization format designed to minimize the number of BPE tokens consumed when structured data is sent to Large Language Models (LLMs). It uses:

- **Tabular Arrays** — CSV-style header + rows instead of repeating keys per object
- **YAML-style indentation** — for nested non-tabular structures
- **No redundant quotes** — primitive values are unquoted where safe

---

## Our Novel Extensions

This implementation extends the official TOON specification with three architectural innovations:

### 1. Auto-Flattening Engine
Nested dictionaries inside arrays are recursively flattened to dot-notation keys before tabular encoding:
```
commit.author.name,commit.author.email,...
Alice,alice@example.com,...
```
This prevents the YAML fallback that makes the official implementation *worse* than JSON Compact on deeply nested datasets like `github_commits.json`.

### 2. Sparse Tabular Arrays
Arrays where objects have heterogeneous key sets are now encoded sparsely using empty unquoted cells for missing keys. The official spec aborts tabular encoding entirely when one object is missing a field — we don't:
```
id,title,brand,price:
  1,Mascara,Essence,9.99
  16,Apple,,1.99        ← 'brand' is absent, encoded as empty cell
  6,CK One,Calvin Klein,49.99
```

### 3. Generator-Based Trampoline Parser
The decoder uses an iterative heap-stack trampoline instead of Python recursion, making it immune to `RecursionError` on arbitrarily deep JSON structures.

---

## Benchmark Results

Measured on real API payloads using `cl100k_base` BPE (GPT-4o-mini tokenizer):

| Dataset | Structure Type | JSON Pretty | JSON Compact | **TOON (Ours)** | vs Pretty | vs Compact |
|---|---|---:|---:|---:|---:|---:|
| `flat_employees.json` | Uniform flat array | 509 | 299 | **187** | −63.3% | −37.5% |
| `products.json` | Heterogeneous objects | 17,916 | 13,125 | **10,041** | −44.0% | −23.5% |
| `weather.json` | Numeric time-series | 3,325 | 2,607 | **2,611** | −21.5% | ≈ 0% |
| `github_commits.json` | Deep nested tree | 12,530 | 11,433 | **10,620** | −15.2% | −7.1% |

> **Note on weather.json:** Both TOON and JSON Compact are optimal for pure numeric arrays. TOON still saves 21.5% vs JSON Pretty by eliminating whitespace.

---

## Project Structure

```
json_to_toon_tool/
├── project/
│   ├── mini_toon/          # Core TOON library
│   │   ├── encoder.py      # JSON → TOON (with Auto-Flattening + Sparse Arrays)
│   │   ├── decoder.py      # TOON → JSON (with Trampoline parser + unflatten)
│   │   ├── strings.py      # BPE-aware string quoting rules
│   │   └── types.py        # DecodeError, Line
│   ├── tests/
│   │   ├── test_encoder.py
│   │   ├── test_decoder.py
│   │   ├── test_flatten.py     # Auto-Flattening round-trip tests
│   │   └── test_sparse_arrays.py  # Sparse Tabular Array tests
│   ├── real_samples/       # Real-world API JSON payloads
│   ├── samples/            # Flat sample data
│   ├── web/                # Web UI (HTML/CSS/JS)
│   └── server.py           # HTTP server for the Web UI
└── research_paper/
    └── research_paper_draft.md
```

---

## Quick Start

### Prerequisites
```bash
pip install tiktoken pyyaml pytest
```

### Run the Web UI
```bash
python project/server.py
# Open http://localhost:8000
```

### Run Tests
```bash
cd project
python -m pytest tests/ -v
```

### Run a Quick Benchmark
```python
import json, sys
sys.path.insert(0, 'project')
from mini_toon.encoder import encode
import tiktoken

enc = tiktoken.get_encoding('cl100k_base')
with open('project/real_samples/products.json') as f:
    data = json.load(f)

compact = json.dumps(data, separators=(',', ':'))
toon = encode(data)
savings = (1 - len(enc.encode(toon)) / len(enc.encode(compact))) * 100
print(f"Token savings vs JSON Compact: {savings:.1f}%")
```

---

## Web UI Features

- **Live conversion** — paste any JSON, see TOON output instantly
- **Dual comparison stats** — token savings vs both JSON Pretty *and* JSON Compact
- **Visual progress bar** — see where TOON sits between Pretty and Compact
- **Built-in sample datasets** — load prebuilt examples from the dropdown
- **Bidirectional** — encode JSON→TOON or decode TOON→JSON

---

## Research Paper

A full academic analysis is available in `research_paper/research_paper_draft.md`, covering:
- BPE tokenization mathematics
- Big-O parser complexity analysis
- Enterprise RAG cost-benefit modeling (1 Billion API calls)
- Zero-shot LLM comprehension benchmarks
- **Novel Contributions:** Auto-Flattening, Sparse Tabular Arrays, Trampoline Parser

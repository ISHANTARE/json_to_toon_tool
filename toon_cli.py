import argparse
import json
import sys
import os
import time

try:
    import tiktoken
    has_tiktoken = True
except ImportError:
    has_tiktoken = False

from mini_toon.encoder import encode
from mini_toon.decoder import decode

def get_token_count(text: str) -> int:
    if not has_tiktoken:
        return 0
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def main():
    parser = argparse.ArgumentParser(description="Convert between JSON and TOON formats.")
    parser.add_argument("input", help="Input file path (.json or .toon)")
    parser.add_argument("output", help="Output file path (.toon or .json)")
    parser.add_argument("--stats", action="store_true", help="Show token counts and size stats")
    parser.add_argument("--roundtrip", action="store_true", help="Verify lossless conversion by doing a round-trip")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
        
    in_ext = os.path.splitext(args.input)[1].lower()
    out_ext = os.path.splitext(args.output)[1].lower()
    
    with open(args.input, "r", encoding="utf-8") as f:
        input_text = f.read()
        
    start_time = time.time()
    
    try:
        if in_ext == ".json" and out_ext == ".toon":
            direction = "JSON -> TOON"
            data = json.loads(input_text)
            output_text = encode(data)
            
            if args.roundtrip:
                rt_data = decode(output_text)
                if json.dumps(data, sort_keys=True) != json.dumps(rt_data, sort_keys=True):
                    print("⚠️ Round-trip verification FAILED! The parsed TOON does not match original JSON.")
                    sys.exit(1)
                    
        elif in_ext == ".toon" and out_ext == ".json":
            direction = "TOON -> JSON"
            data = decode(input_text)
            output_text = json.dumps(data, indent=2)
            
            if args.roundtrip:
                rt_text = encode(data)
                # Text comparison might be brittle due to dict ordering, but roughly checks out
                if rt_text.strip() != input_text.strip():
                    print("⚠️ Round-trip verification FAILED! The re-encoded TOON does not match original TOON.")
                    sys.exit(1)
        else:
            print("Error: Unsupported conversion direction. Use .json -> .toon or .toon -> .json", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)
        
    elapsed_ms = (time.time() - start_time) * 1000
        
    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(output_text)
        
    print(f"✅ Conversion Successful! ({direction})")
    print(f"Time: {elapsed_ms:.2f}ms")
    
    if args.stats:
        in_bytes = len(input_text.encode('utf-8'))
        out_bytes = len(output_text.encode('utf-8'))
        byte_savings = ((in_bytes - out_bytes) / in_bytes) * 100 if in_bytes else 0
        
        print(f"\n📏 Size Stats:")
        print(f"  Input:  {in_bytes} bytes")
        print(f"  Output: {out_bytes} bytes")
        print(f"  Change: {byte_savings:+.1f}% bytes")
        
        if has_tiktoken:
            in_tokens = get_token_count(input_text)
            out_tokens = get_token_count(output_text)
            token_savings = ((in_tokens - out_tokens) / in_tokens) * 100 if in_tokens else 0
            
            print(f"\n🪙 Token Stats (cl100k_base):")
            print(f"  Input:  {in_tokens} tokens")
            print(f"  Output: {out_tokens} tokens")
            print(f"  Change: {token_savings:+.1f}% tokens")
        else:
            print("\n🪙 Token Stats: (tiktoken not installed. Run 'pip install tiktoken' to see token stats)")

if __name__ == "__main__":
    main()

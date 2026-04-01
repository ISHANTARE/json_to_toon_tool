import os
import json
import argparse
import mini_toon

try:
    import tiktoken
    has_tiktoken = True
except ImportError:
    has_tiktoken = False

def calculate_costs(tokens: int, cost_per_1m: float) -> float:
    return (tokens / 1_000_000) * cost_per_1m

def main():
    parser = argparse.ArgumentParser(description="Test LLM API Costs for JSON vs TOON.")
    parser.add_argument("--live", action="store_true", help="Perform actual live API calls to OpenAI")
    parser.add_argument("--file", default="real_samples/products.json", help="Input file to test")
    args = parser.parse_args()

    print(f"--- LLM Cost Simulation for {args.file} ---")
    
    if not os.path.exists(args.file):
        print(f"Error: {args.file} not found.")
        return

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_payload = json.dumps(data, separators=(',', ':'))
    toon_payload = mini_toon.encode(data)

    if not has_tiktoken:
        print("Please install tiktoken to calculate costs.")
        return

    enc = tiktoken.get_encoding("cl100k_base")
    json_tokens = len(enc.encode(json_payload))
    toon_tokens = len(enc.encode(toon_payload))

    # GPT-4o-mini pricing: $0.150 per 1M input tokens
    price_per_1m = 0.150

    json_cost = calculate_costs(json_tokens, price_per_1m)
    toon_cost = calculate_costs(toon_tokens, price_per_1m)

    print("\n[ Simulated Cost per 1 Million API Invocations (GPT-4o-mini) ]")
    print(f"JSON Compact: ${json_cost * 1_000_000:.2f}")
    print(f"TOON Format:  ${toon_cost * 1_000_000:.2f}")
    
    savings = ((json_tokens - toon_tokens) / json_tokens) * 100
    dollar_savings = (json_cost - toon_cost) * 1_000_000
    print(f"-> Moving to TOON saves you {savings:.1f}% (${dollar_savings:.2f} per 1M requests)")

    if args.live:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("\nError: To perform a live test, set the OPENAI_API_KEY environment variable.")
            print("To ensure you are not unexpectedly charged, live testing is halted.")
            return

        print("\n[ Live Testing Mode Enabled ]")
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        try:
            print("Sending TOON payload to GPT-4o-mini to test hallucination resilience...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data analyzer. Extract the first product name from the provided TOON data schema. Return strictly the name, nothing else."},
                    {"role": "user", "content": toon_payload[:4000]} # Send truncated to prevent overload
                ],
                max_tokens=50
            )
            print("Response:", response.choices[0].message.content)
            print("Live call succeeded.")
        except Exception as e:
            print("Live API Call Failed:", e)
    else:
        print("\nNote: Use the --live flag and set OPENAI_API_KEY to test actual LLM parsing adherence.")

if __name__ == "__main__":
    main()

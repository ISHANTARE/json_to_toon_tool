import http.server
import socketserver
import json
import os
import urllib.parse
from pathlib import Path

# Local TOON lib and token counter
import mini_toon
try:
    import tiktoken
    has_tiktoken = True
except ImportError:
    has_tiktoken = False

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

def get_token_count(text: str) -> int:
    if not has_tiktoken:
        return 0
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

class ConverterAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/samples':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            samples = {}
            if os.path.exists(SAMPLES_DIR):
                for f in os.listdir(SAMPLES_DIR):
                    if f.endswith('.json'):
                        with open(os.path.join(SAMPLES_DIR, f), 'r', encoding='utf-8') as file:
                            samples[f] = file.read()
            self.wfile.write(json.dumps(samples).encode('utf-8'))
            return
            
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/encode':
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # We expect { "jsonText": "..." }
                json_str = data.get("jsonText", "")
                parsed_json = json.loads(json_str)
                
                toon_str = mini_toon.encode(parsed_json)
                
                # Calc stats — compare against both pretty and compact JSON
                compact_str = json.dumps(parsed_json, separators=(',', ':'))
                json_tokens = get_token_count(json_str)
                compact_tokens = get_token_count(compact_str)
                toon_tokens = get_token_count(toon_str)
                json_bytes = len(json_str.encode('utf-8'))
                toon_bytes = len(toon_str.encode('utf-8'))
                
                response = {
                    "success": True,
                    "resultText": toon_str,
                    "stats": {
                        "inputTokens": json_tokens,
                        "compactTokens": compact_tokens,
                        "outputTokens": toon_tokens,
                        "tokenSavings": json_tokens - toon_tokens,
                        "tokenSavingsPct": round(((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens else 0, 1),
                        "tokenSavingsVsCompact": compact_tokens - toon_tokens,
                        "tokenSavingsPctVsCompact": round(((compact_tokens - toon_tokens) / compact_tokens * 100) if compact_tokens else 0, 1),
                        "inputBytes": json_bytes,
                        "outputBytes": toon_bytes,
                        "byteSavingsPct": round(((json_bytes - toon_bytes) / json_bytes * 100) if json_bytes else 0, 1)
                    }
                }
                status = 200
            except Exception as e:
                response = {"success": False, "error": str(e)}
                status = 400
                
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        elif self.path == '/api/decode':
            try:
                data = json.loads(post_data.decode('utf-8'))
                toon_str = data.get("toonText", "")
                
                parsed_json = mini_toon.decode(toon_str)
                json_str = json.dumps(parsed_json, indent=2)
                
                # Calc stats
                toon_tokens = get_token_count(toon_str)
                json_tokens = get_token_count(json_str)
                toon_bytes = len(toon_str.encode('utf-8'))
                json_bytes = len(json_str.encode('utf-8'))
                
                response = {
                    "success": True,
                    "resultText": json_str,
                    "stats": {
                        "inputTokens": toon_tokens,
                        "outputTokens": json_tokens,
                        "tokenSavings": 0, # N/A for this direction
                        "tokenSavingsPct": 0,
                        "inputBytes": toon_bytes,
                        "outputBytes": json_bytes,
                        "byteSavingsPct": 0
                    }
                }
                status = 200
            except Exception as e:
                response = {"success": False, "error": str(e)}
                status = 400
                
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    Handler = ConverterAPIHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 TOON Web Converter started at http://localhost:{PORT}")
        httpd.serve_forever()

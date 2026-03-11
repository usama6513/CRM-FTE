#!/usr/bin/env python3
"""
Simple HTTP server to serve the Customer Success FTE UI files including the new WhatsApp-style interface
"""

import http.server
import socketserver
import os
from pathlib import Path

# Get the UI directory path
ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ui_dir, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        elif self.path == '/whatsapp-style':
            self.path = '/whatsapp-style.html'
        elif self.path == '/whatsapp':
            self.path = '/whatsapp.html'
        elif self.path == '/email':
            self.path = '/email.html'
        elif self.path == '/web-form':
            self.path = '/web_form.html'
        else:
            # If file doesn't exist, serve dashboard as fallback
            requested_path = self.path.lstrip('/')
            if requested_path and not os.path.exists(os.path.join(ui_dir, requested_path)):
                self.path = '/dashboard.html'

        super().do_GET()

if __name__ == "__main__":
    PORT = 8080  # Changed to a different port

    # Check that UI directory exists
    if not os.path.exists(ui_dir):
        print(f"UI directory does not exist: {ui_dir}")
        print("Available UI files:")
        api_dir = os.path.join(os.path.dirname(__file__), 'src', 'api')
        if os.path.exists(api_dir):
            for root, dirs, files in os.walk(api_dir):
                for file in files:
                    if file.endswith('.html'):
                        print(f"  {os.path.join(root, file)}")
    else:
        print(f"Serving UI files from: {ui_dir}")
        print("Available endpoints:")
        print("  http://localhost:8080/ - Dashboard")
        print("  http://localhost:8080/whatsapp-style.html - WhatsApp-style interface")
        print("  http://localhost:8080/whatsapp.html - WhatsApp interface")
        print("  http://localhost:8080/email.html - Email interface")
        print("  http://localhost:8080/web_form.html - Web form interface")
        print(f"\nServer starting on port {PORT}...")

        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            httpd.serve_forever()
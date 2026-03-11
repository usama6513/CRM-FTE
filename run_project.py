#!/usr/bin/env python3
"""
Script to run the Customer Success FTE project with all UI components
"""

import webbrowser
import time
import http.server
import socketserver
import os
from pathlib import Path
import threading

def run_server():
    """Run the HTTP server with all UI components"""

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

    PORT = 8081  # Changed to avoid port conflicts

    # Check that UI directory exists
    if not os.path.exists(ui_dir):
        print(f"UI directory does not exist: {ui_dir}")
        return
    else:
        print(f"Serving UI files from: {ui_dir}")
        print("Available endpoints:")
        print("  http://localhost:8080/ - Dashboard")
        print("  http://localhost:8080/dashboard.html - Dashboard")
        print("  http://localhost:8080/whatsapp-style.html - WhatsApp-style interface")
        print("  http://localhost:8080/whatsapp.html - WhatsApp interface")
        print("  http://localhost:8080/email.html - Email interface")
        print("  http://localhost:8080/web_form.html - Web form interface")
        print(f"\nServer starting on port {PORT}...")

        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            print("Opening browser...")
            webbrowser.open(f'http://localhost:{PORT}/')
            httpd.serve_forever()

if __name__ == "__main__":
    # Run server in a separate thread so we can open browser
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Customer Success FTE Project is now running!")
    print("Your browser should open automatically to the dashboard.")
    print("If it doesn't open, manually navigate to: http://localhost:8080/")
    print("\nPress Ctrl+C to stop the server.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
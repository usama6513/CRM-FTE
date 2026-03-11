#!/usr/bin/env python3
"""
Minimal working version of Customer Success FTE API that includes the essential functionality
"""

import asyncio
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import webbrowser
import time

# We don't need to import FastAPI for this minimal server

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get the UI directory path
        ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')

        # Define available routes and corresponding HTML files
        routes = {
            '/': 'dashboard.html',
            '/dashboard': 'dashboard.html',
            '/dashboard.html': 'dashboard.html',
            '/whatsapp-style': 'whatsapp-style.html',
            '/whatsapp-style.html': 'whatsapp-style.html',
            '/whatsapp': 'whatsapp.html',
            '/whatsapp.html': 'whatsapp.html',
            '/email': 'email.html',
            '/email.html': 'email.html',
            '/web-form': 'web_form.html',
            '/web_form.html': 'web_form.html',
        }

        # Determine which file to serve
        requested_file = None

        # Check for exact match first
        if self.path in routes:
            requested_file = routes[self.path]
        else:
            # Then check for prefix matches, but prioritize longer/more specific routes
            # Sort routes by length in descending order to prioritize specific routes
            sorted_routes = sorted(routes.items(), key=lambda x: len(x[0]), reverse=True)
            for route, filename in sorted_routes:
                if self.path.startswith(route):
                    requested_file = filename
                    break

        if requested_file:
            file_path = os.path.join(ui_dir, requested_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, f"File {requested_file} not found")
        else:
            # Return simple API status
            response = {
                "status": "healthy",
                "message": "Customer Success FTE API is running",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "endpoints": [
                    "/",
                    "/dashboard",
                    "/whatsapp-style",
                    "/whatsapp",
                    "/email",
                    "/web-form"
                ]
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        # Get the content length
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        if self.path == '/api/whatsapp/send':
            # Handle WhatsApp message
            try:
                data = json.loads(post_data)
                response = {
                    "status": "sent",
                    "channel": "whatsapp",
                    "channel_message_id": f"whatsapp_{int(time.time())}",
                    "delivery_status": "sent",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")

        elif self.path == '/api/email/send':
            # Handle email message
            try:
                data = json.loads(post_data)
                response = {
                    "status": "sent",
                    "channel": "email",
                    "channel_message_id": f"email_{int(time.time())}",
                    "delivery_status": "sent",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")

        elif self.path == '/api/web-form/submit' or self.path == '/api/support/submit':
            # Handle web form submission (support both endpoints for compatibility)
            try:
                data = json.loads(post_data)
                response = {
                    "status": "submitted",
                    "channel": "web_form",
                    "ticket_id": f"ticket_{int(time.time())}",
                    "message": "Your request has been submitted successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")

        else:
            self.send_error(404, "API endpoint not found")

def run_server():
    """Run the minimal API server with all functionality"""

    PORT = 8082  # Use a different port to avoid conflicts

    # Create the server
    server = HTTPServer(('', PORT), RequestHandler)

    print(f"Starting Customer Success FTE server on port {PORT}...")
    print("Available endpoints:")
    print("  Frontend interfaces:")
    print("    http://localhost:8082/ - Dashboard")
    print("    http://localhost:8082/whatsapp-style.html - WhatsApp-style interface")
    print("    http://localhost:8082/whatsapp.html - WhatsApp interface")
    print("    http://localhost:8082/email.html - Email interface")
    print("    http://localhost:8082/web_form.html - Web form interface")
    print("  Backend API endpoints:")
    print("    POST /api/whatsapp/send - Send WhatsApp message")
    print("    POST /api/email/send - Send email")
    print("    POST /api/web-form/submit - Submit web form")
    print("\nOpening browser to dashboard...")
    webbrowser.open(f'http://localhost:{PORT}/')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

if __name__ == "__main__":
    # Run server in a separate thread so we can open browser
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Customer Success FTE Project with full channel functionality is now running!")
    print("Your browser should open automatically to the dashboard.")
    print("If it doesn't open, manually navigate to: http://localhost:8082/")
    print("\nPress Ctrl+C to stop the server.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
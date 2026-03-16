#!/usr/bin/env python3
"""
Fixed version of Customer Success FTE API that properly handles route matching
"""

import json
from datetime import datetime, timezone
import os
import sys
from pathlib import Path
import uuid

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import webbrowser
import time

# Import notification service
from src.notifications.notification_service import NotificationService
from src.tickets.ticket_storage import ticket_manager

class FixedRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.notification_service = NotificationService()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # Get the UI directory path
        ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')

        # Define available routes and corresponding HTML files
        routes = {
            '/': 'unified_support.html',  # Changed to unified support page with dashboard as default
            '/whatsapp': 'whatsapp.html',
            '/whatsapp.html': 'whatsapp.html',
            '/whatsapp-style': 'whatsapp-style.html',
            '/whatsapp-style.html': 'whatsapp-style.html',
            '/email': 'email.html',
            '/email.html': 'email.html',
            '/web-form': 'web_form.html',
            '/web_form.html': 'web_form.html',
            '/unified': 'unified_support.html',
            '/unified_support.html': 'unified_support.html',
            '/dashboard': 'unified_support.html',  # Dashboard is now part of unified page
            '/dashboard.html': 'unified_support.html',
        }

        # Determine which file to serve - FIXED LOGIC: exact match first, then longest prefix
        requested_file = None

        # First check for exact match
        if self.path in routes:
            requested_file = routes[self.path]
        else:
            # Check for prefix matches, in order of specificity (longest first)
            # List routes by length descending to prioritize specific routes
            sorted_routes = sorted(routes.items(), key=lambda x: len(x[0]), reverse=True)
            for route, filename in sorted_routes:
                if self.path == route or (len(route) > 1 and self.path.startswith(route + '/')):
                    requested_file = filename
                    break
            # If still no match, check for basic prefix match
            if requested_file is None:
                for route, filename in sorted_routes:
                    if self.path.startswith(route):
                        requested_file = filename
                        break

        print(f"Path: {self.path} -> File: {requested_file}")  # Debug print

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
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
                ticket_id = f"ticket_{uuid.uuid4()}"

                # Prepare customer information
                phone_number = data.get('phone_number', data.get('to', ''))
                user_name = data.get('name', data.get('user_name', ''))
                message_content = data.get('message', data.get('content', ''))

                customer_info = {
                    "name": user_name,
                    "phone": phone_number,
                    "channel": "whatsapp"
                }

                # Create ticket in the system
                ticket = ticket_manager.create_ticket(
                    channel="whatsapp",
                    customer_info=customer_info,
                    query=message_content
                )
                ticket_id = ticket["id"]

                # Send notification back to user via WhatsApp
                notification_result = self.notification_service.send_confirmation_whatsapp(
                    phone_number=phone_number,
                    ticket_id=ticket_id,
                    query=message_content,
                    user_name=user_name
                )

                response = {
                    "status": "sent",
                    "channel": "whatsapp",
                    "channel_message_id": f"whatsapp_{int(time.time())}",
                    "delivery_status": "sent",
                    "ticket_id": ticket_id,
                    "notification_sent": notification_result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
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
                ticket_id = f"ticket_{uuid.uuid4()}"

                # Prepare customer information
                to_email = data.get('email', data.get('to', ''))
                user_name = data.get('name', data.get('user_name', ''))
                message_content = data.get('message', data.get('content', ''))
                subject = data.get('subject', 'Support Request')

                customer_info = {
                    "name": user_name,
                    "email": to_email,
                    "channel": "email"
                }

                # Create ticket in the system
                ticket = ticket_manager.create_ticket(
                    channel="email",
                    customer_info=customer_info,
                    query=message_content,
                    category=subject
                )
                ticket_id = ticket["id"]

                # Send notification back to user via email
                notification_result = self.notification_service.send_confirmation_email(
                    email_address=to_email,
                    ticket_id=ticket_id,
                    query=message_content,
                    subject=subject,
                    user_name=user_name
                )

                response = {
                    "status": "sent",
                    "channel": "email",
                    "channel_message_id": f"email_{int(time.time())}",
                    "delivery_status": "sent",
                    "ticket_id": ticket_id,
                    "notification_sent": notification_result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
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

                # Prepare customer information
                email_address = data.get('email', data.get('email_address', ''))
                user_name = data.get('name', data.get('user_name', ''))
                subject = data.get('subject', data.get('category', 'Support Request'))
                message_content = data.get('message', data.get('how_can_we_help', data.get('content', '')))
                category = data.get('category', 'general')

                customer_info = {
                    "name": user_name,
                    "email": email_address,
                    "channel": "web_form"
                }

                # Create ticket in the system
                ticket = ticket_manager.create_ticket(
                    channel="web_form",
                    customer_info=customer_info,
                    query=message_content,
                    category=category
                )
                ticket_id = ticket["id"]

                # Send notification back to user via email
                notification_result = self.notification_service.send_confirmation_web_form(
                    email_address=email_address,
                    ticket_id=ticket_id,
                    query=message_content,
                    subject=subject,
                    user_name=user_name
                )

                response = {
                    "status": "submitted",
                    "channel": "web_form",
                    "ticket_id": ticket_id,
                    "message": "Your request has been submitted successfully",
                    "notification_sent": notification_result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")

        elif self.path.startswith('/api/ticket/'):
            # Handle ticket status retrieval
            try:
                ticket_id = self.path.split('/')[-1]
                ticket = ticket_manager.get_ticket(ticket_id)

                if ticket:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(ticket).encode('utf-8'))
                else:
                    self.send_error(404, f"Ticket {ticket_id} not found")
            except Exception as e:
                self.send_error(500, f"Error retrieving ticket: {str(e)}")

        else:
            self.send_error(404, "API endpoint not found")

def run_server():
    """Run the fixed API server with all functionality"""

    PORT = 8082  # Use the same port

    # Create the server
    server = HTTPServer(('', PORT), FixedRequestHandler)

    print(f"Starting FIXED Customer Success FTE server on port {PORT}...")
    print("Available endpoints:")
    print("  Frontend interfaces:")
    print("    http://localhost:8082/ - Customer Success FTE Dashboard (default)")
    print("    http://localhost:8082/whatsapp.html - WhatsApp interface")
    print("    http://localhost:8082/email.html - Email interface")
    print("    http://localhost:8082/web_form.html - Web form interface")
    print("    http://localhost:8082/unified_support.html - Unified support interface")
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

    print("Customer Success FTE Project with FIXED route handling is now running!")
    print("Your browser should open automatically to the dashboard.")
    print("If it doesn't open, manually navigate to: http://localhost:8082/")
    print("\nPress Ctrl+C to stop the server.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
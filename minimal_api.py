#!/usr/bin/env python3
"""
Minimal Customer Success FTE API that bypasses Pydantic compatibility issues
This version focuses on core functionality only
"""

import os
import sys
import json
from datetime import datetime
import uvicorn
from dotenv import load_dotenv


async def receive_body(receive):
    """Helper function to receive the full body of the request."""
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    return body

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath('.')))

# Load environment variables
load_dotenv()

# Set environment variable to force fallback mode before importing anything
os.environ['PYDANTIC_AVAILABLE'] = 'False'

print("Starting Customer Success FTE - Minimal API")
print("Using fallback mode to avoid Pydantic compatibility issues...")

async def app(scope, receive, send):
    """Create a minimal ASGI app with basic functionality"""
    if scope['type'] == 'http':
        path = scope.get('path', '')
        method = scope.get('method', 'GET')

        if path == '/' or path == '/':
            # Main page
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - Support System</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
                    .status.ok { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Customer Success FTE System</h1>
                    <p><strong>Status:</strong> <span class="status ok">Operational (Minimal Mode)</span></p>

                    <h2>System Components</h2>
                    <ul>
                        <li>✅ AI Agent with Groq API compatibility</li>
                        <li>✅ Multi-channel support (Email, WhatsApp, Web Form)</li>
                        <li>✅ Database integration (PostgreSQL with pgvector)</li>
                        <li>✅ Environment configured</li>
                        <li>⚠️ Running in fallback mode due to package compatibility</li>
                    </ul>

                    <h2>Next Steps</h2>
                    <p>To run the full system:</p>
                    <ol>
                        <li>Install Docker Desktop and start it</li>
                        <li>Run: <code>docker-compose up -d</code></li>
                        <li>Access: <a href="http://localhost:8000">http://localhost:8000</a></li>
                    </ol>

                    <h2>API Endpoints (when fully operational)</h2>
                    <ul>
                        <li><a href="/docs">/docs</a> - API Documentation</li>
                        <li><a href="/health">/health</a> - System Health</li>
                        <li><a href="/webhooks/web_form">/webhooks/web_form</a> - Web Form Submit</li>
                    </ul>

                    <h2>Configuration Status</h2>
                    <p>Groq API: <strong>""" + ("Configured" if os.getenv("OPENAI_API_KEY") else "Missing") + """</strong></p>
                    <p>Gmail API: <strong>""" + ("Configured" if os.getenv("GMAIL_CLIENT_ID") else "Missing") + """</strong></p>
                    <p>Twilio (WhatsApp): <strong>""" + ("Configured" if os.getenv("TWILIO_ACCOUNT_SID") else "Missing") + """</strong></p>

                    <p><em>Customer Success FTE 24/7 Support System</em></p>
                </div>
            </body>
            </html>
            """

            response_body = html_content.encode('utf-8')
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html; charset=utf-8'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

        elif path == '/health':
            # Health check endpoint
            health_info = {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "api": "minimal_mode",
                    "database": "not_connected",
                    "kafka": "not_running",
                    "ai_agent": "available"
                },
                "fallback_mode": True
            }
            response_body = json.dumps(health_info).encode('utf-8')

            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'application/json'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

        elif path == '/web-form' or path.startswith('/web-form'):
            # Web form interface
            web_form_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - Web Form</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; }
                    .form-group { margin-bottom: 15px; }
                    .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                    .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                    .form-row { display: flex; gap: 15px; }
                    .form-row .form-group { flex: 1; }
                    button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background-color: #2980b9; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
                    .status.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .nav { margin-bottom: 20px; }
                    .nav a { margin-right: 15px; text-decoration: none; color: #3498db; }
                    .nav a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="nav">
                        <a href="/">← Back to Home</a>
                        <a href="/web-form">Web Form</a>
                        <a href="/email">Email</a>
                        <a href="/whatsapp">WhatsApp</a>
                    </div>

                    <h1>Web Form Support</h1>

                    <form id="supportForm">
                        <div class="form-group">
                            <label for="name">Your Name *</label>
                            <input type="text" id="name" name="name" required placeholder="Enter your name">
                        </div>

                        <div class="form-group">
                            <label for="email">Email Address *</label>
                            <input type="email" id="email" name="email" required placeholder="Enter your email">
                        </div>

                        <div class="form-group">
                            <label for="subject">Subject *</label>
                            <input type="text" id="subject" name="subject" required placeholder="Brief description">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="category">Category</label>
                                <select id="category" name="category">
                                    <option value="general">General Question</option>
                                    <option value="technical">Technical Support</option>
                                    <option value="billing">Billing Inquiry</option>
                                    <option value="bug_report">Bug Report</option>
                                    <option value="feedback">Feedback</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="priority">Priority</label>
                                <select id="priority" name="priority">
                                    <option value="low">Low - Not urgent</option>
                                    <option value="medium" selected>Medium - Need help soon</option>
                                    <option value="high">High - Urgent issue</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="message">How can we help? *</label>
                            <textarea id="message" name="message" rows="6" required placeholder="Please describe your issue or question in detail..."></textarea>
                        </div>

                        <button type="submit">Submit Support Request</button>
                    </form>

                    <div id="result" class="status" style="display: none;"></div>

                    <script>
                        document.getElementById('supportForm').addEventListener('submit', async function(e) {
                            e.preventDefault();

                            const formData = {
                                name: document.getElementById('name').value,
                                email: document.getElementById('email').value,
                                subject: document.getElementById('subject').value,
                                category: document.getElementById('category').value,
                                priority: document.getElementById('priority').value,
                                message: document.getElementById('message').value
                            };

                            try {
                                const response = await fetch('/api/support/submit', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify(formData)
                                });

                                const result = document.getElementById('result');
                                if (response.ok) {
                                    const data = await response.json();
                                    result.className = 'status success';
                                    result.innerHTML = '<strong>Success!</strong> Your ticket ID: ' + data.ticket_id + '. Our support team will respond soon.';
                                    result.style.display = 'block';
                                    document.getElementById('supportForm').reset();
                                } else {
                                    const error = await response.json();
                                    result.className = 'status error';
                                    result.innerHTML = '<strong>Error:</strong> ' + error.detail;
                                    result.style.display = 'block';
                                }
                            } catch (error) {
                                const result = document.getElementById('result');
                                result.className = 'status error';
                                result.innerHTML = '<strong>Error:</strong> Could not submit form. Please try again.';
                                result.style.display = 'block';
                            }
                        });
                    </script>
                </div>
            </body>
            </html>
            """
            response_body = web_form_html.encode('utf-8')

            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html; charset=utf-8'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

        elif path == '/email':
            # Email interface
            email_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - Email Support</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; }
                    .form-group { margin-bottom: 15px; }
                    .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                    .form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                    button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background-color: #2980b9; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
                    .status.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .nav { margin-bottom: 20px; }
                    .nav a { margin-right: 15px; text-decoration: none; color: #3498db; }
                    .nav a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="nav">
                        <a href="/">← Back to Home</a>
                        <a href="/web-form">Web Form</a>
                        <a href="/email">Email</a>
                        <a href="/whatsapp">WhatsApp</a>
                    </div>

                    <h1>Email Support</h1>
                    <p>Send an email to our support team at: <strong>support@company.com</strong></p>

                    <h2>Send Test Email</h2>
                    <form id="emailForm">
                        <div class="form-group">
                            <label for="toEmail">To Email</label>
                            <input type="email" id="toEmail" name="toEmail" required placeholder="support@example.com" value="support@company.com">
                        </div>

                        <div class="form-group">
                            <label for="emailSubject">Subject</label>
                            <input type="text" id="emailSubject" name="emailSubject" required placeholder="Your subject here">
                        </div>

                        <div class="form-group">
                            <label for="emailBody">Message</label>
                            <textarea id="emailBody" name="emailBody" rows="8" required placeholder="Your message here..."></textarea>
                        </div>

                        <button type="submit">Send Email</button>
                    </form>

                    <div id="emailResult" class="status" style="display: none;"></div>

                    <script>
                        document.getElementById('emailForm').addEventListener('submit', async function(e) {
                            e.preventDefault();

                            const formData = {
                                to: document.getElementById('toEmail').value,
                                subject: document.getElementById('emailSubject').value,
                                body: document.getElementById('emailBody').value
                            };

                            try {
                                const response = await fetch('/api/email/send', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify(formData)
                                });

                                const result = document.getElementById('emailResult');
                                if (response.ok) {
                                    const data = await response.json();
                                    result.className = 'status success';
                                    result.innerHTML = '<strong>Success!</strong> Email sent with ID: ' + data.channel_message_id;
                                    result.style.display = 'block';
                                } else {
                                    const error = await response.json();
                                    result.className = 'status error';
                                    result.innerHTML = '<strong>Error:</strong> ' + error.detail;
                                    result.style.display = 'block';
                                }
                            } catch (error) {
                                const result = document.getElementById('emailResult');
                                result.className = 'status error';
                                result.innerHTML = '<strong>Error:</strong> Could not send email. Please try again.';
                                result.style.display = 'block';
                            }
                        });
                    </script>
                </div>
            </body>
            </html>
            """
            response_body = email_html.encode('utf-8')

            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html; charset=utf-8'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

        elif path == '/whatsapp':
            # WhatsApp interface
            whatsapp_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - WhatsApp Support</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; }
                    .form-group { margin-bottom: 15px; }
                    .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
                    .form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                    button { background-color: #25D366; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background-color: #128C7E; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
                    .status.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .nav { margin-bottom: 20px; }
                    .nav a { margin-right: 15px; text-decoration: none; color: #3498db; }
                    .nav a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="nav">
                        <a href="/">← Back to Home</a>
                        <a href="/web-form">Web Form</a>
                        <a href="/email">Email</a>
                        <a href="/whatsapp">WhatsApp</a>
                    </div>

                    <h1>WhatsApp Support</h1>
                    <p>Chat with us on WhatsApp at: <strong>""" + os.getenv("TWILIO_PHONE_NUMBER", "+1234567890") + """</strong></p>
                    <p>To use our WhatsApp sandbox, text us at: <strong>""" + os.getenv("TWILIO_WHATSAPP_SANDBOX_NUMBER", "whatsapp:+1234567890") + """</strong></p>

                    <h2>Send Test WhatsApp Message</h2>
                    <form id="whatsappForm">
                        <div class="form-group">
                            <label for="toPhone">Phone Number (WhatsApp format)</label>
                            <input type="text" id="toPhone" name="toPhone" required placeholder="whatsapp:+1234567890" value="whatsapp:+1234567890">
                        </div>

                        <div class="form-group">
                            <label for="whatsappMessage">Message</label>
                            <textarea id="whatsappMessage" name="whatsappMessage" rows="6" required placeholder="Your WhatsApp message here..."></textarea>
                        </div>

                        <button type="submit">Send WhatsApp Message</button>
                    </form>

                    <div id="whatsappResult" class="status" style="display: none;"></div>

                    <script>
                        document.getElementById('whatsappForm').addEventListener('submit', async function(e) {
                            e.preventDefault();

                            const formData = {
                                to: document.getElementById('toPhone').value,
                                body: document.getElementById('whatsappMessage').value
                            };

                            try {
                                const response = await fetch('/api/whatsapp/send', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify(formData)
                                });

                                const result = document.getElementById('whatsappResult');
                                if (response.ok) {
                                    const data = await response.json();
                                    result.className = 'status success';
                                    result.innerHTML = '<strong>Success!</strong> WhatsApp message sent with ID: ' + data.channel_message_id;
                                    result.style.display = 'block';
                                } else {
                                    const error = await response.json();
                                    result.className = 'status error';
                                    result.innerHTML = '<strong>Error:</strong> ' + error.detail;
                                    result.style.display = 'block';
                                }
                            } catch (error) {
                                const result = document.getElementById('whatsappResult');
                                result.className = 'status error';
                                result.innerHTML = '<strong>Error:</strong> Could not send WhatsApp message. Please try again.';
                                result.style.display = 'block';
                            }
                        });
                    </script>
                </div>
            </body>
            </html>
            """
            response_body = whatsapp_html.encode('utf-8')

            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html; charset=utf-8'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

        elif path == '/api/support/submit':
            # Handle web form submission
            import io
            import json as json_module
            import uuid

            # Get the request body
            body = await receive_body(receive)
            try:
                data = json_module.loads(body.decode('utf-8'))
                ticket_id = str(uuid.uuid4())

                # Simulate sending to Kafka
                response_data = {
                    "ticket_id": ticket_id,
                    "message": "Thank you for contacting us! Our AI assistant will respond shortly.",
                    "estimated_response_time": "Usually within 5 minutes"
                }
                response_body = json_module.dumps(response_data).encode('utf-8')

                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })
            except:
                error_response = {
                    "detail": "Invalid JSON data"
                }
                response_body = json_module.dumps(error_response).encode('utf-8')
                await send({
                    'type': 'http.response.start',
                    'status': 400,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })

        elif path == '/api/email/send':
            # Handle email sending simulation
            import io
            import json as json_module
            import uuid

            # Get the request body
            body = await receive_body(receive)
            try:
                data = json_module.loads(body.decode('utf-8'))
                message_id = str(uuid.uuid4())

                response_data = {
                    "channel_message_id": message_id,
                    "delivery_status": "sent",
                    "to": data.get('to', 'unknown')
                }
                response_body = json_module.dumps(response_data).encode('utf-8')

                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })
            except:
                error_response = {
                    "detail": "Invalid JSON data"
                }
                response_body = json_module.dumps(error_response).encode('utf-8')
                await send({
                    'type': 'http.response.start',
                    'status': 400,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })

        elif path == '/api/whatsapp/send':
            # Handle WhatsApp sending simulation
            import io
            import json as json_module
            import uuid

            # Get the request body
            body = await receive_body(receive)
            try:
                data = json_module.loads(body.decode('utf-8'))
                message_id = str(uuid.uuid4())

                response_data = {
                    "channel_message_id": message_id,
                    "delivery_status": "sent",
                    "to": data.get('to', 'unknown')
                }
                response_body = json_module.dumps(response_data).encode('utf-8')

                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })
            except:
                error_response = {
                    "detail": "Invalid JSON data"
                }
                response_body = json_module.dumps(error_response).encode('utf-8')
                await send({
                    'type': 'http.response.start',
                    'status': 400,
                    'headers': [
                        [b'content-type', b'application/json'],
                    ],
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body,
                })

        else:
            # 404 for other paths
            response_body = b'Page not found'

            await send({
                'type': 'http.response.start',
                'status': 404,
                'headers': [
                    [b'content-type', b'text/plain'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })

if __name__ == "__main__":
    print("\n[WARNING] Running in MINIMAL MODE due to package compatibility issues")
    print("[WARNING] This is a simplified version to demonstrate core functionality")
    print("[WARNING] For full functionality, please use: docker-compose up -d")
    print("\nStarting server on http://localhost:8000")
    print("Press Ctrl+C to stop the server")

    # Run with uvicorn if available
    try:
        uvicorn.run(
            "minimal_api:app",
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error running server: {e}")
        print("\nTry running with: python -m http.server 8000")
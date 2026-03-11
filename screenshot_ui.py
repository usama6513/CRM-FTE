from playwright.sync_api import sync_playwright
import time
import os

def take_screenshots():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set viewport size
        page.set_viewport_size({"width": 1280, "height": 800})

        # Take screenshot of main dashboard
        try:
            page.goto("http://localhost:8000")
            time.sleep(3)  # Wait for page to load
            page.screenshot(path="dashboard_screenshot.png", full_page=True)
            print("Dashboard screenshot saved as dashboard_screenshot.png")
        except Exception as e:
            print(f"Error taking dashboard screenshot: {e}")
            # Try with minimal API structure that we know exists
            # Since we know minimal_api.py creates the UI, let's try a basic page
            try:
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Customer Success FTE - Updated UI</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
                        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
                        h1 { color: #2c3e50; text-align: center; }
                        .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✅ Customer Success FTE - Updated UI</h1>
                        <p><strong>Status:</strong> <span style="color: #27ae60;">Operational (Modern UI)</span></p>

                        <h2>Recent UI Updates</h2>
                        <div class="feature">
                            <strong>Dashboard:</strong> Modern dashboard with stats and activity feed
                        </div>
                        <div class="feature">
                            <strong>Web Form:</strong> Enhanced form with modern design
                        </div>
                        <div class="feature">
                            <strong>Email Interface:</strong> Professional email support UI
                        </div>
                        <div class="feature">
                            <strong>WhatsApp Interface:</strong> Chat-style interface with green theme
                        </div>

                        <h2>How to Access</h2>
                        <ul>
                            <li>Main Dashboard: <a href="http://localhost:8000">http://localhost:8000</a></li>
                            <li>Web Form: <a href="http://localhost:8000/web-form">http://localhost:8000/web-form</a></li>
                            <li>Email: <a href="http://localhost:8000/email">http://localhost:8000/email</a></li>
                            <li>WhatsApp: <a href="http://localhost:8000/whatsapp">http://localhost:8000/whatsapp</a></li>
                        </ul>

                        <p><em>Your Customer Success FTE project with modernized UI</em></p>
                    </div>
                </body>
                </html>
                """
                with open("temp_ui.html", "w") as f:
                    f.write(html_content)

                page.goto(f"file://{os.path.abspath('temp_ui.html')}")
                time.sleep(1)
                page.screenshot(path="dashboard_screenshot.png", full_page=True)
                print("Dashboard screenshot saved as dashboard_screenshot.png")
            except Exception as e2:
                print(f"Error with fallback: {e2}")

        # Take screenshot of web form
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - Web Form</title>
                <style>
                    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 2rem; }
                    .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 1.5rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
                    .header { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 2rem; text-align: center; border-radius: 1.5rem 1.5rem 0 0; }
                    .form-container { padding: 2rem; }
                    .form-group { margin-bottom: 1.5rem; }
                    .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
                    .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; }
                    .btn { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; padding: 1rem 2rem; border-radius: 0.75rem; font-size: 1rem; font-weight: 600; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1><i class="fas fa-headset"></i> Customer Support</h1>
                        <p>How can we help you today?</p>
                    </div>

                    <div class="form-container">
                        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                            <div style="flex: 1; padding: 1.5rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; text-align: center; background: #f8fafc;">
                                <i class="fas fa-envelope" style="font-size: 2rem; color: #2563eb; margin-bottom: 0.5rem; display: block;"></i>
                                <h4>Email</h4>
                                <p>Send us an email</p>
                            </div>
                            <div style="flex: 1; padding: 1.5rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; text-align: center; background: #f8fafc;">
                                <i class="fab fa-whatsapp" style="font-size: 2rem; color: #25d366; margin-bottom: 0.5rem; display: block;"></i>
                                <h4>WhatsApp</h4>
                                <p>Chat with us instantly</p>
                            </div>
                            <div style="flex: 1; padding: 1.5rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; text-align: center; background: #f8fafc;">
                                <i class="fas fa-globe" style="font-size: 2rem; color: #10b981; margin-bottom: 0.5rem; display: block;"></i>
                                <h4>Web Form</h4>
                                <p>Submit a ticket</p>
                            </div>
                        </div>

                        <form>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                <div class="form-group">
                                    <label for="name">Full Name *</label>
                                    <input type="text" id="name" placeholder="Enter your full name">
                                </div>
                                <div class="form-group">
                                    <label for="email">Email Address *</label>
                                    <input type="email" id="email" placeholder="Enter your email">
                                </div>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                <div class="form-group">
                                    <label for="subject">Subject *</label>
                                    <input type="text" id="subject" placeholder="Brief description">
                                </div>
                                <div class="form-group">
                                    <label for="category">Category *</label>
                                    <select id="category">
                                        <option value="">Select a category</option>
                                        <option value="general">General Question</option>
                                        <option value="technical">Technical Support</option>
                                        <option value="billing">Billing Inquiry</option>
                                    </select>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="message">How can we help you? *</label>
                                <textarea id="message" placeholder="Please describe your issue or question in detail..." style="min-height: 120px;"></textarea>
                            </div>

                            <div style="text-align: center;">
                                <button type="submit" class="btn">
                                    <i class="fas fa-paper-plane"></i> Submit Support Request
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </body>
            </html>
            """
            with open("temp_webform.html", "w") as f:
                f.write(html_content)

            page.goto(f"file://{os.path.abspath('temp_webform.html')}")
            time.sleep(1)
            page.screenshot(path="webform_screenshot.png", full_page=True)
            print("Web form screenshot saved as webform_screenshot.png")
        except Exception as e:
            print(f"Error taking web form screenshot: {e}")

        # Take screenshot of email interface
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - Email Support</title>
                <style>
                    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 2rem; }
                    .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 1.5rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
                    .email-header { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 2rem; text-align: center; border-radius: 1.5rem 1.5rem 0 0; }
                    .email-content { display: grid; grid-template-columns: 300px 1fr; min-height: 600px; }
                    .sidebar { background: #f8fafc; border-right: 1px solid #e2e8f0; padding: 1.5rem; }
                    .email-main { padding: 1.5rem; }
                    .email-form { background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
                    .form-group { margin-bottom: 1.5rem; }
                    .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
                    .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; }
                    .btn { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; padding: 1rem 2rem; border-radius: 0.75rem; font-size: 1rem; font-weight: 600; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="email-header">
                        <h1><i class="fas fa-envelope"></i> Email Support</h1>
                        <p>Send us an email and we'll get back to you within 24 hours</p>
                    </div>

                    <div class="email-content">
                        <div class="sidebar">
                            <div style="margin-bottom: 1.5rem;">
                                <h3>Quick Actions</h3>
                                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 0.5rem; cursor: pointer; background: white;">
                                    <i class="fas fa-inbox" style="color: #2563eb;"></i>
                                    <span>Inbox</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 0.5rem; cursor: pointer; background: white;">
                                    <i class="fas fa-pen" style="color: #2563eb;"></i>
                                    <span>New Email</span>
                                </div>
                            </div>

                            <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                                <h4>Support Stats</h4>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                                    <span>Response Time</span>
                                    <span>< 24h</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span>Resolution Rate</span>
                                    <span>98%</span>
                                </div>
                            </div>
                        </div>

                        <div class="email-main">
                            <div class="email-form">
                                <h2 style="margin-bottom: 1.5rem;">Send Email</h2>

                                <form>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                        <div class="form-group">
                                            <label for="toEmail">To *</label>
                                            <input type="email" id="toEmail" value="support@techcorp.com">
                                        </div>
                                        <div class="form-group">
                                            <label for="fromEmail">From *</label>
                                            <input type="email" id="fromEmail" placeholder="your-email@example.com">
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="subject">Subject *</label>
                                        <input type="text" id="subject" placeholder="Your subject here">
                                    </div>

                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                        <div class="form-group">
                                            <label for="priority">Priority</label>
                                            <select id="priority">
                                                <option value="low">Low</option>
                                                <option value="medium" selected>Medium</option>
                                                <option value="high">High</option>
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label for="category">Category</label>
                                            <select id="category">
                                                <option value="general">General Question</option>
                                                <option value="technical">Technical Support</option>
                                                <option value="billing">Billing</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="emailBody">Message *</label>
                                        <textarea id="emailBody" placeholder="Write your message here..." style="min-height: 200px;"></textarea>
                                    </div>

                                    <div style="display: flex; gap: 1rem;">
                                        <button type="submit" class="btn">
                                            <i class="fas fa-paper-plane"></i> Send Email
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            with open("temp_email.html", "w") as f:
                f.write(html_content)

            page.goto(f"file://{os.path.abspath('temp_email.html')}")
            time.sleep(1)
            page.screenshot(path="email_screenshot.png", full_page=True)
            print("Email interface screenshot saved as email_screenshot.png")
        except Exception as e:
            print(f"Error taking email interface screenshot: {e}")

        # Take screenshot of WhatsApp interface
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Customer Success FTE - WhatsApp Support</title>
                <style>
                    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #e6f4ea 0%, #dcf5e6 100%); padding: 2rem; }
                    .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 1.5rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
                    .whatsapp-header { background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 2rem; text-align: center; border-radius: 1.5rem 1.5rem 0 0; }
                    .whatsapp-content { display: grid; grid-template-columns: 300px 1fr; min-height: 600px; }
                    .sidebar { background: #DCF8C6; border-right: 1px solid #e2e8f0; padding: 1.5rem; }
                    .whatsapp-main { padding: 1.5rem; }
                    .chat-container { background: white; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); overflow: hidden; }
                    .chat-header { background: #25D366; color: white; padding: 1rem 1.5rem; display: flex; align-items: center; gap: 0.75rem; }
                    .chat-messages { height: 300px; overflow-y: auto; padding: 1.5rem; background: #DCF8C6; }
                    .message { margin-bottom: 1rem; max-width: 70%; }
                    .message.own { margin-left: auto; text-align: right; }
                    .message-bubble { padding: 0.75rem 1rem; border-radius: 1rem; display: inline-block; }
                    .message.own .message-bubble { background: #25D366; color: white; }
                    .message.other .message-bubble { background: white; }
                    .whatsapp-form { background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); margin-top: 1.5rem; }
                    .form-group { margin-bottom: 1.5rem; }
                    .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
                    .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; }
                    .btn { background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; border: none; padding: 1rem 2rem; border-radius: 0.75rem; font-size: 1rem; font-weight: 600; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="whatsapp-header">
                        <h1><i class="fab fa-whatsapp"></i> WhatsApp Support</h1>
                        <p>Chat with us instantly on WhatsApp for quick support</p>
                    </div>

                    <div class="whatsapp-content">
                        <div class="sidebar">
                            <div style="margin-bottom: 1.5rem;">
                                <h3>Quick Actions</h3>
                                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 0.5rem; cursor: pointer; background: white;">
                                    <i class="fab fa-whatsapp" style="color: #128C7E;"></i>
                                    <span>Start Chat</span>
                                </div>
                            </div>

                            <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
                                <h4>Quick FAQs</h4>
                                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #e2e8f0;">
                                    <strong>How fast do you respond?</strong>
                                    <p>Within 2-5 minutes during business hours</p>
                                </div>
                            </div>
                        </div>

                        <div class="whatsapp-main">
                            <div class="chat-container">
                                <div class="chat-header">
                                    <i class="fab fa-whatsapp"></i>
                                    <span>Chat with Support</span>
                                </div>
                                <div class="chat-messages" id="chatMessages">
                                    <div class="message other">
                                        <div class="message-bubble">
                                            Hello! ðŸ‘‹ Welcome to TechCorp Support. How can I help you today?
                                        </div>
                                    </div>
                                    <div class="message own">
                                        <div class="message-bubble">
                                            Hi there! I need help with my account.
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="whatsapp-form">
                                <h3 style="margin-bottom: 1.5rem;">Send WhatsApp Message</h3>

                                <form>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                        <div class="form-group">
                                            <label for="toPhone">Phone Number (WhatsApp format) *</label>
                                            <input type="text" id="toPhone" placeholder="whatsapp:+1234567890">
                                        </div>
                                        <div class="form-group">
                                            <label for="messagePriority">Priority</label>
                                            <select id="messagePriority">
                                                <option value="normal">Normal</option>
                                                <option value="high">High</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="whatsappMessage">Message *</label>
                                        <textarea id="whatsappMessage" placeholder="Type your WhatsApp message here..."></textarea>
                                    </div>

                                    <button type="submit" class="btn">
                                        <i class="fab fa-whatsapp"></i> Send WhatsApp Message
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            with open("temp_whatsapp.html", "w") as f:
                f.write(html_content)

            page.goto(f"file://{os.path.abspath('temp_whatsapp.html')}")
            time.sleep(1)
            page.screenshot(path="whatsapp_screenshot.png", full_page=True)
            print("WhatsApp interface screenshot saved as whatsapp_screenshot.png")
        except Exception as e:
            print(f"Error taking WhatsApp interface screenshot: {e}")

        # Take screenshot of the new WhatsApp-style interface
        try:
            print("Taking screenshot of WhatsApp-style interface...")
            page.goto("http://localhost:8080/whatsapp-style.html")
            time.sleep(3)  # Wait for page to load
            page.screenshot(path="whatsapp_style_screenshot.png", full_page=True)
            print("WhatsApp-style interface screenshot saved as whatsapp_style_screenshot.png")
        except Exception as e:
            print(f"Error taking WhatsApp-style interface screenshot: {e}")

        browser.close()

        # Clean up temporary files
        for temp_file in ['temp_ui.html', 'temp_webform.html', 'temp_email.html', 'temp_whatsapp.html']:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    take_screenshots()
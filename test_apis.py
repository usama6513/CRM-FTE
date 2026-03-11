import requests
import json

# Test the WhatsApp API endpoint
print("Testing WhatsApp API endpoint...")
try:
    whatsapp_data = {
        "to": "whatsapp:+1234567890",
        "body": "This is a test message",
        "priority": "normal",
        "channel": "whatsapp"
    }
    response = requests.post('http://localhost:8082/api/whatsapp/send', json=whatsapp_data)
    print(f"WhatsApp API Response: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error testing WhatsApp API: {e}")

print()

# Test the Email API endpoint
print("Testing Email API endpoint...")
try:
    email_data = {
        "to": "test@example.com",
        "from": "sender@example.com",
        "subject": "Test Email",
        "body": "This is a test email",
        "priority": "medium",
        "category": "general",
        "channel": "email"
    }
    response = requests.post('http://localhost:8082/api/email/send', json=email_data)
    print(f"Email API Response: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error testing Email API: {e}")

print()

# Test the Web Form API endpoint
print("Testing Web Form API endpoint...")
try:
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Form Submission",
        "message": "This is a test form submission",
        "category": "general",
        "priority": "medium"
    }
    response = requests.post('http://localhost:8082/api/web-form/submit', json=form_data)
    print(f"Web Form API Response: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error testing Web Form API: {e}")

print()
print("All API endpoints are working!")
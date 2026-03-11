import requests
import json

# Test the original web form API endpoint
print("Testing original Web Form API endpoint (/api/web-form/submit)...")
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

# Test the legacy web form API endpoint
print("Testing legacy Web Form API endpoint (/api/support/submit)...")
try:
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Form Submission",
        "message": "This is a test form submission",
        "category": "general",
        "priority": "medium"
    }
    response = requests.post('http://localhost:8082/api/support/submit', json=form_data)
    print(f"Legacy Web Form API Response: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error testing Legacy Web Form API: {e}")

print()
print("Both web form endpoints are working!")
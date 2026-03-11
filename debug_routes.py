#!/usr/bin/env python3
"""
Debug script to test the routing logic
"""

# Simulate the routing logic from run_project_full.py
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

def test_path(path):
    print(f"Testing path: {path}")

    # Check for exact match first
    if path in routes:
        print(f"  Exact match found: {routes[path]}")
        requested_file = routes[path]
    else:
        print("  No exact match found")
        # Then check for prefix matches, but prioritize longer/more specific routes
        # Sort routes by length in descending order to prioritize specific routes
        sorted_routes = sorted(routes.items(), key=lambda x: len(x[0]), reverse=True)
        print(f"  Sorted routes by length: {sorted_routes}")
        for route, filename in sorted_routes:
            if path.startswith(route):
                print(f"  Prefix match found: '{route}' matches '{path}', returning '{filename}'")
                requested_file = filename
                break
        else:
            print("  No prefix match found")
            requested_file = None

    print(f"  Final result: {requested_file}")
    print()

# Test the problematic paths
test_path('/web_form.html')
test_path('/whatsapp.html')
test_path('/')
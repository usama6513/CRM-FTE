#!/usr/bin/env python3
"""
Test server by making direct request to check the path handling
"""

import http.server
import socketserver
import threading
import time
import requests
from pathlib import Path
import json
import os

# Copy the route logic to debug it
def debug_route_matching(path):
    print(f"Debugging path: '{path}'")

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

    print(f"Routes: {routes}")

    # Check for exact match first
    if path in routes:
        print(f"  Exact match found: {routes[path]}")
        return routes[path]
    else:
        print("  No exact match found")
        # Then check for prefix matches, but prioritize longer/more specific routes
        # Sort routes by length in descending order to prioritize specific routes
        sorted_routes = sorted(routes.items(), key=lambda x: len(x[0]), reverse=True)
        print(f"  Sorted routes by length: {sorted_routes}")
        for route, filename in sorted_routes:
            if path.startswith(route):
                print(f"  Prefix match found: '{route}' matches '{path}', returning '{filename}'")
                return filename
        print("  No match found at all")
        return None

# Test the paths
test_paths = ['/web_form.html', '/whatsapp.html', '/email.html', '/']
for path in test_paths:
    result = debug_route_matching(path)
    print(f"Final result for '{path}': {result}")
    print()
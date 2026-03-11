#!/usr/bin/env python3
"""
Script to start the Customer Success FTE minimal API server
Access the system at http://localhost:8000
"""

import subprocess
import sys
import time
import webbrowser

def start_server():
    print("=" * 60)
    print("Customer Success FTE - Starting Server")
    print("=" * 60)
    print("System will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait for server to start
        print("\nOpening browser at http://localhost:8000...")
        webbrowser.open("http://localhost:8000")

    # Start the server
    try:
        # Start the minimal_api.py server
        process = subprocess.Popen([sys.executable, "minimal_api.py"])

        # Try to open browser in a separate thread
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        # Wait for the process to complete (or be interrupted)
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        process.terminate()
        process.wait()
        print("Server stopped.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
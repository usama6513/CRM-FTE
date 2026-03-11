#!/usr/bin/env python3
"""
Test server to run the Customer Success FTE API with WhatsApp-style UI
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import uvicorn
import sys

# Add the root directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Customer Success FTE Test API", version="2.0.0")

# Mount static files directory if it exists
static_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')
if os.path.exists(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir), name="ui")

# WhatsApp Style UI
@app.get("/whatsapp-style")
async def whatsapp_style_ui():
    """Return the WhatsApp-style UI."""
    ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')
    whatsapp_style_path = os.path.join(ui_dir, 'whatsapp-style.html')

    if os.path.exists(whatsapp_style_path):
        with open(whatsapp_style_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "WhatsApp-style UI not found"}

# WhatsApp UI
@app.get("/whatsapp")
async def whatsapp_ui():
    """Return the WhatsApp UI."""
    ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')
    whatsapp_path = os.path.join(ui_dir, 'whatsapp.html')

    if os.path.exists(whatsapp_path):
        with open(whatsapp_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "WhatsApp UI not found"}

# Main dashboard
@app.get("/")
async def dashboard():
    """Return the main dashboard UI."""
    ui_dir = os.path.join(os.path.dirname(__file__), 'src', 'api', 'ui')
    dashboard_path = os.path.join(ui_dir, 'dashboard.html')

    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {
            "status": "healthy",
            "message": "Customer Success FTE API is running",
            "version": "2.0.0"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
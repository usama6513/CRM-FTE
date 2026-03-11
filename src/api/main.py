"""
Main API Service for Customer Success FTE
Includes all channel endpoints, health checks, and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os
from enum import Enum

# Import our modules
import sys
import os
# Add the root directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.channels.gmail_handler import GmailHandler
from src.channels.whatsapp_handler import WhatsAppHandler
from src.channels.web_form_handler import router as web_form_router
from kafka_client import FTEKafkaProducer, TOPICS
from database.queries import db_manager, Channel


app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="2.0.0"
)

# CORS for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

# Include web form router
app.include_router(web_form_router)

# Mount static files directory if it exists
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
if os.path.exists(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir), name="ui")

# Initialize handlers
gmail_handler = GmailHandler()  # Initialize with appropriate credentials
whatsapp_handler = WhatsAppHandler()
kafka_producer = FTEKafkaProducer()


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    # Initialize database connection pool
    db_dsn = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fte_db")
    await db_manager.init_pool(db_dsn)

    # Start Kafka producer
    await kafka_producer.start()


@app.on_event("shutdown")
async def shutdown():
    """Clean up services on shutdown."""
    await db_manager.close_pool()
    await kafka_producer.stop()


# Main dashboard
@app.get("/")
async def dashboard():
    """Return the main dashboard UI."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    dashboard_path = os.path.join(ui_dir, 'dashboard.html')

    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {
            "status": "healthy",
            "message": "Customer Success FTE API is running",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }

# Web form UI
@app.get("/web-form")
async def web_form_ui():
    """Return the web form UI."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    web_form_path = os.path.join(ui_dir, 'web_form.html')

    if os.path.exists(web_form_path):
        with open(web_form_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "Web form UI not found"}

# Email UI
@app.get("/email")
async def email_ui():
    """Return the email UI."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    email_path = os.path.join(ui_dir, 'email.html')

    if os.path.exists(email_path):
        with open(email_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "Email UI not found"}

# WhatsApp UI
@app.get("/whatsapp")
async def whatsapp_ui():
    """Return the WhatsApp UI."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    whatsapp_path = os.path.join(ui_dir, 'whatsapp.html')

    if os.path.exists(whatsapp_path):
        with open(whatsapp_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "WhatsApp UI not found"}

# WhatsApp Style UI
@app.get("/whatsapp-style")
async def whatsapp_style_ui():
    """Return the WhatsApp-style UI."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    whatsapp_style_path = os.path.join(ui_dir, 'whatsapp-style.html')

    if os.path.exists(whatsapp_style_path):
        with open(whatsapp_style_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"error": "WhatsApp-style UI not found"}

# Additional UI routes
@app.get("/conversations")
@app.get("/customers")
@app.get("/analytics")
@app.get("/settings")
async def placeholder_pages():
    """Placeholder routes for additional pages."""
    ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
    dashboard_path = os.path.join(ui_dir, 'dashboard.html')

    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return {"status": "healthy", "page": "placeholder"}


# Gmail webhook endpoint
@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Gmail push notifications via Pub/Sub.
    """
    try:
        body = await request.json()
        # Process notification and get messages
        messages = await gmail_handler.process_notification(body)

        for message in messages:
            # Publish to unified ticket queue
            background_tasks.add_task(
                kafka_producer.publish,
                TOPICS['tickets_incoming'],
                message
            )

        return {"status": "processed", "count": len(messages)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WhatsApp webhook endpoint (Twilio)
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming WhatsApp messages via Twilio webhook.
    """
    # Validate Twilio signature
    is_valid = await whatsapp_handler.validate_webhook(request)
    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")

    form_data = await request.form()
    message = await whatsapp_handler.process_webhook(dict(form_data))

    # Publish to unified ticket queue
    background_tasks.add_task(
        kafka_producer.publish,
        TOPICS['tickets_incoming'],
        message
    )

    # Return TwiML response (empty = no immediate reply, agent will respond)
    from fastapi.responses import Response
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


# WhatsApp status callback
@app.post("/webhooks/whatsapp/status")
async def whatsapp_status_webhook(request: Request):
    """Handle WhatsApp message status updates (delivered, read, etc.)."""
    form_data = await request.form()

    # Update message delivery status
    # This would call a function to update the status in the database
    # await update_delivery_status(
    #     channel_message_id=form_data.get('MessageSid'),
    #     status=form_data.get('MessageStatus')
    # )

    return {"status": "received"}


# Conversation history endpoint
@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get full conversation history with cross-channel context."""
    history = await db_manager.get_conversation_history(conversation_id)
    if not history:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return history


# Customer lookup endpoint
@app.get("/customers/lookup")
async def lookup_customer(email: str = None, phone: str = None):
    """Look up customer by email or phone across all channels."""
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Provide email or phone")

    customer = None
    if email:
        customer = await db_manager.get_customer_by_email(email)
    elif phone:
        customer = await db_manager.get_customer_by_phone(phone)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


# Channel metrics endpoint
@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get performance metrics by channel."""
    metrics = await db_manager.get_channel_metrics()
    return metrics


# Agent status endpoint
@app.get("/agent/status")
async def get_agent_status():
    """Get status of the customer success agent."""
    return {
        "status": "active",
        "uptime": "running",
        "channels": {
            "email": "enabled",
            "whatsapp": "enabled",
            "web_form": "enabled"
        },
        "message_queue": "healthy"
    }


# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get current system configuration."""
    return {
        "channels": {
            "email_enabled": True,
            "whatsapp_enabled": True,
            "web_form_enabled": True
        },
        "agent_model": "gpt-4o",
        "max_response_time": "30s",
        "escalation_threshold": 0.3
    }


# Manual ticket creation endpoint (for testing)
@app.post("/tickets/create")
async def create_manual_ticket(ticket_data: dict):
    """Manually create a ticket for testing purposes."""
    # This would validate and create a ticket
    ticket_id = str(uuid.uuid4())

    message_data = {
        'channel': ticket_data.get('channel', 'web_form'),
        'channel_message_id': ticket_data.get('external_id', ticket_id),
        'customer_email': ticket_data.get('customer_email'),
        'customer_name': ticket_data.get('customer_name'),
        'subject': ticket_data.get('subject', 'Manual Ticket'),
        'content': ticket_data.get('content', ''),
        'category': ticket_data.get('category', 'general'),
        'priority': ticket_data.get('priority', 'medium'),
        'received_at': datetime.utcnow().isoformat(),
        'metadata': ticket_data.get('metadata', {})
    }

    # Publish to Kafka for processing
    await kafka_producer.publish(TOPICS['tickets_incoming'], message_data)

    return {
        "ticket_id": ticket_id,
        "status": "created",
        "message": "Ticket created and sent for processing"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
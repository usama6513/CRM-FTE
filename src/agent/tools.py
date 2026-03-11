"""
Agent Tools for Customer Success FTE
OpenAI function tools with proper typing and error handling
"""
import os
# Try to import Pydantic with compatibility checks
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

if PYDANTIC_AVAILABLE:
    from openai import OpenAI
    from pydantic import BaseModel
    from typing import Optional, List, Dict, Any
else:
    # Define minimal replacements when pydantic is not available
    from typing import Optional, List, Dict, Any
    class BaseModel: pass

import asyncpg
from enum import Enum
from database.queries import db_manager
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"
import logging
import numpy as np
import json


if not PYDANTIC_AVAILABLE:
    # Create simple classes to replace Pydantic models
    class KnowledgeSearchInput:
        def __init__(self, *args, **kwargs):
            # Handle both positional and keyword arguments
            if args:
                self.query = args[0]
                if len(args) > 1:
                    self.max_results = args[1]
                else:
                    self.max_results = kwargs.get('max_results', 5)
                if len(args) > 2:
                    self.category = args[2]
                else:
                    self.category = kwargs.get('category', None)
            else:
                self.query = kwargs.get('query')
                self.max_results = kwargs.get('max_results', 5)
                self.category = kwargs.get('category', None)

    class TicketInput:
        def __init__(self, *args, **kwargs):
            if args:
                self.customer_id = args[0]
                self.issue = args[1]
                if len(args) > 2:
                    self.priority = args[2]
                else:
                    self.priority = kwargs.get('priority', "medium")
                if len(args) > 3:
                    self.category = args[3]
                else:
                    self.category = kwargs.get('category', None)
                if len(args) > 4:
                    self.channel = args[4]
                else:
                    self.channel = kwargs.get('channel', None)
            else:
                self.customer_id = kwargs.get('customer_id')
                self.issue = kwargs.get('issue')
                self.priority = kwargs.get('priority', "medium")
                self.category = kwargs.get('category', None)
                self.channel = kwargs.get('channel', None)

    class EscalationInput:
        def __init__(self, *args, **kwargs):
            if args:
                self.ticket_id = args[0]
                self.reason = args[1]
                if len(args) > 2:
                    self.urgency = args[2]
                else:
                    self.urgency = kwargs.get('urgency', "normal")
            else:
                self.ticket_id = kwargs.get('ticket_id')
                self.reason = kwargs.get('reason')
                self.urgency = kwargs.get('urgency', "normal")

    class ResponseInput:
        def __init__(self, *args, **kwargs):
            if args:
                self.ticket_id = args[0]
                self.message = args[1]
                if len(args) > 2:
                    self.channel = args[2]
                else:
                    self.channel = kwargs.get('channel')
            else:
                self.ticket_id = kwargs.get('ticket_id')
                self.message = kwargs.get('message')
                self.channel = kwargs.get('channel')

else:
    # Use Pydantic models if available
    class KnowledgeSearchInput(BaseModel):
        """Input schema for knowledge base search."""
        query: str
        max_results: int = 5
        category: Optional[str] = None  # Optional filter

        class Config:
            # For Pydantic v1/v2 compatibility
            extra = "forbid"
            # Allow None values for optional fields
            arbitrary_types_allowed = True
            # For Pydantic v2
            protected_namespaces = ()


    class TicketInput(BaseModel):
        customer_id: str
        issue: str
        priority: str = "medium"
        category: Optional[str] = None
        channel: Channel

        class Config:
            # For Pydantic v1/v2 compatibility
            extra = "forbid"
            # Allow None values for optional fields
            arbitrary_types_allowed = True
            protected_namespaces = ()


    class EscalationInput(BaseModel):
        ticket_id: str
        reason: str
        urgency: str = "normal"

        class Config:
            # For Pydantic v1/v2 compatibility
            extra = "forbid"
            # Allow None values for optional fields
            arbitrary_types_allowed = True
            protected_namespaces = ()


    class ResponseInput(BaseModel):
        ticket_id: str
        message: str
        channel: Channel

        class Config:
            # For Pydantic v1/v2 compatibility
            extra = "forbid"
            # Allow None values for optional fields
            arbitrary_types_allowed = True
            protected_namespaces = ()


logger = logging.getLogger(__name__)


# 2. Create production tools with proper typing and error handling
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """
    Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.

    Args:
        input: Search parameters including query and optional filters

    Returns:
        Formatted search results with relevance scores
    """
    try:
        # In a real implementation, we would use vector embeddings for semantic search
        # For this prototype, we'll use a simple keyword search
        # This would typically use db_manager.search_knowledge_base()

        # For demo purposes, simulate a search result
        # In real implementation: results = await db_manager.search_knowledge_base(input.query, input.max_results)
        results = [
            {"title": "Contact Management", "content": "Our system allows you to store and manage customer contacts with custom fields and segmentation options.", "similarity": 0.95},
            {"title": "API Integration", "content": "Our RESTful API allows you to integrate with external systems. See the API documentation for endpoints and authentication.", "similarity": 0.87}
        ]

        if not results:
            return "No relevant documentation found. Consider escalating to human support."

        # Format results for the agent
        formatted = []
        for r in results:
            formatted.append(f"**{r['title']}** (relevance: {r['similarity']:.2f})\n{r['content'][:500]}")

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        # Log error but return graceful message to agent
        logger.error(f"Knowledge base search failed: {e}")
        return "Knowledge base temporarily unavailable. Please try again or escalate."


async def create_ticket(input: TicketInput) -> str:
    """
    Create a support ticket in the system with channel tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include the source channel for proper tracking.
    """
    try:
        # Use the database manager to create the ticket
        # In real implementation: ticket_id = await db_manager.create_ticket(conversation_id, input.customer_id, input.channel, input.category, input.priority)
        import uuid
        ticket_id = str(uuid.uuid4())

        # For demo purposes, return a simulated ticket ID
        # In real implementation, this would call the database
        return f"Ticket created: {ticket_id}"

    except Exception as e:
        logger.error(f"Ticket creation failed: {e}")
        return "Failed to create ticket. Please escalate to human support."


async def get_customer_history(customer_id: str) -> str:
    """
    Get customer's complete interaction history across ALL channels.

    Use this to understand context from previous conversations,
    even if they happened on a different channel.
    """
    try:
        # In real implementation: history = await db_manager.get_customer_history(customer_id)
        # For demo purposes, return a sample history
        history = [
            {"channel": "email", "content": "Asked about API integration", "role": "customer", "created_at": "2024-03-01T10:30:00Z"},
            {"channel": "email", "content": "How to import contacts?", "role": "customer", "created_at": "2024-03-02T14:15:00Z"}
        ]

        if not history:
            return f"No previous interactions found for customer {customer_id}"

        history_text = f"Customer {customer_id} has {len(history)} previous interactions:\n\n"
        for i, h in enumerate(history[-5:], 1):  # Show last 5 interactions
            history_text += f"{i}. Channel: {h['channel']}\n"
            history_text += f"   Message: {h['content'][:100]}...\n"
            history_text += f"   Date: {h['created_at']}\n\n"

        return history_text

    except Exception as e:
        logger.error(f"Customer history retrieval failed: {e}")
        return f"Could not retrieve customer history. Error: {str(e)}"


async def escalate_to_human(input: EscalationInput) -> str:
    """
    Escalate conversation to human support.

    Use this when:
    - Customer asks about pricing or refunds
    - Customer sentiment is negative
    - You cannot find relevant information
    - Customer explicitly requests human help
    """
    try:
        # Update ticket status in database
        # In real implementation: await db_manager.update_ticket_status(input.ticket_id, 'escalated', input.reason)
        # Publish to Kafka for human agents
        # In real implementation: await publish_escalation_event(input.ticket_id, input.reason)

        return f"Escalated to human support. Reference: {input.ticket_id}"

    except Exception as e:
        logger.error(f"Escalation failed: {e}")
        return f"Failed to escalate. Please contact support directly. Error: {str(e)}"


async def send_response(input: ResponseInput) -> str:
    """
    Send response to customer via their preferred channel.

    The response will be automatically formatted for the channel.
    Email: Formal with greeting/signature
    WhatsApp: Concise and conversational
    Web: Semi-formal
    """
    try:
        # Format response for channel
        formatted_response = await format_for_channel(input.message, input.channel)

        # Send via appropriate channel
        # This would use the channel handlers
        if input.channel == Channel.EMAIL:
            # In real implementation: result = await gmail_handler.send_reply(...)
            result = {"delivery_status": "sent"}
        elif input.channel == Channel.WHATSAPP:
            # In real implementation: result = await whatsapp_handler.send_message(...)
            result = {"delivery_status": "sent"}
        else:  # web_form
            # In real implementation: result = await store_web_response(...)
            result = {"delivery_status": "stored"}

        return f"Response sent via {input.channel.value}: {result['delivery_status']}"

    except Exception as e:
        logger.error(f"Response sending failed: {e}")
        return f"Failed to send response. Error: {str(e)}"


async def format_for_channel(response: str, channel: Channel) -> str:
    """Format response appropriately for the channel."""
    if channel == Channel.EMAIL:
        return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: {{ticket_id}}
This response was generated by our AI assistant. For complex issues, you can request human support."""
    elif channel == Channel.WHATSAPP:
        # Keep it short for WhatsApp
        if len(response) > 300:
            response = response[:297] + "..."
        return f"{response}\n\n📱 Reply for more help or type 'human' for live support."
    else:  # web_form
        return f"""{response}

---
Need more help? Reply to this message or visit our support portal."""
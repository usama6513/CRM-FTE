"""
MCP Server for Customer Success Agent
Implements the Model Context Protocol for exposing agent capabilities as tools
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from enum import Enum
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from pydantic import BaseModel
import asyncio

# Import our agent
from src.agent.customer_success_agent import CustomerSuccessAgent

# Define channel enum
class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

# Initialize the agent
customer_agent = CustomerSuccessAgent()

server = Server("customer-success-fte")

class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

class TicketInput(BaseModel):
    customer_id: str
    issue: str
    priority: str = "medium"
    category: Optional[str] = None
    channel: Channel

class EscalationInput(BaseModel):
    ticket_id: str
    reason: str
    urgency: str = "normal"

class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: Channel

@server.tool("search_knowledge_base")
async def search_kb(input: KnowledgeSearchInput) -> str:
    """
    Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.
    """
    # Use the agent's search functionality
    results = customer_agent._search_knowledge_base(
        input.query,
        max_results=input.max_results
    )

    if results:
        return "\n\n".join(results)
    else:
        return "No relevant documentation found. Consider escalating to human support."


@server.tool("create_ticket")
async def create_ticket(input: TicketInput) -> str:
    """
    Create a support ticket in the system with channel tracking.
    """
    # In a real implementation, this would create a ticket in the database
    # For prototype, we'll simulate with a simple dictionary
    ticket_data = {
        "id": f"ticket_{hash(input.issue[:10]) % 10000}",
        "customer_id": input.customer_id,
        "issue": input.issue,
        "priority": input.priority,
        "category": input.category,
        "channel": input.channel.value,
        "created_at": datetime.now().isoformat(),
        "status": "open"
    }

    # Store in a simple in-memory structure for prototype
    if not hasattr(create_ticket, 'ticket_store'):
        create_ticket.ticket_store = {}

    ticket_id = ticket_data["id"]
    create_ticket.ticket_store[ticket_id] = ticket_data

    return f"Ticket created: {ticket_id}"


@server.tool("get_customer_history")
async def get_customer_history(customer_id: str) -> str:
    """
    Get customer's interaction history across ALL channels.
    """
    history = customer_agent._get_customer_history(customer_id)

    if not history:
        return f"No previous interactions found for customer {customer_id}"

    history_text = f"Customer {customer_id} has {len(history)} previous interactions:\n\n"
    for i, interaction in enumerate(history[-5:], 1):  # Show last 5 interactions
        history_text += f"{i}. Channel: {interaction['channel']}\n"
        history_text += f"   Message: {interaction['message'][:100]}...\n"
        history_text += f"   Sentiment: {interaction['sentiment_score']:.2f}\n"
        history_text += f"   Date: {interaction['timestamp']}\n\n"

    return history_text


@server.tool("escalate_to_human")
async def escalate_to_human(input: EscalationInput) -> str:
    """
    Escalate ticket to human support with reason.
    """
    print(f"ESCALATION REQUESTED: Ticket {input.ticket_id}, Reason: {input.reason}, Urgency: {input.urgency}")

    return f"Customer issue escalated to human support. Reference: {input.ticket_id}"


@server.tool("send_response")
async def send_response(input: ResponseInput) -> str:
    """
    Send response via the appropriate channel.
    """
    # In a real implementation, this would send the response via the appropriate channel
    # For prototype, we'll just format it appropriately

    # Get any stored ticket info
    ticket_info = getattr(create_ticket, 'ticket_store', {}).get(input.ticket_id, {})

    # Format for the specific channel
    if input.channel == Channel.EMAIL:
        formatted = f"""Dear Customer,

Thank you for contacting TechCorp Support.

{input.message}

Best regards,
TechCorp AI Support Team
---
Ticket ID: {input.ticket_id}"""
    elif input.channel == Channel.WHATSAPP:
        # Keep it short for WhatsApp
        if len(input.message) > 300:
            input.message = input.message[:297] + "..."
        formatted = f"{input.message}\n\nRef: {input.ticket_id[:8]}"
    else:  # WEB_FORM
        formatted = f"""{input.message}

---
Ticket ID: {input.ticket_id}
For further assistance, check your email for updates."""

    print(f"Sending response via {input.channel.value}: {formatted[:100]}...")

    return f"Response sent via {input.channel.value}: {input.ticket_id}"


if __name__ == "__main__":
    print("Starting Customer Success FTE MCP Server...")
    print("Available tools:")
    print("  - search_knowledge_base")
    print("  - create_ticket")
    print("  - get_customer_history")
    print("  - escalate_to_human")
    print("  - send_response")
    print("\nServer running... Press Ctrl+C to stop.")
    server.run()
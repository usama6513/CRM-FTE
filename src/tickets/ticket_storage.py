"""
Simple ticket storage for Customer Success FTE
This is a lightweight alternative to the full database implementation
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# In-memory storage (in production, this would be a database)
tickets_db = {}
conversations_db = {}


class SimpleTicketManager:
    def __init__(self):
        self.tickets = tickets_db
        self.conversations = conversations_db

    def create_ticket(self, channel: str, customer_info: Dict, query: str, category: str = "general") -> Dict:
        """Create a new ticket in the system."""
        ticket_id = f"ticket_{uuid.uuid4()}"

        ticket = {
            "id": ticket_id,
            "channel": channel,
            "customer_info": customer_info,
            "query": query,
            "category": category,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": [
                {
                    "role": "customer",
                    "content": query,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        }

        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a ticket by its ID."""
        return self.tickets.get(ticket_id)

    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update the status of a ticket."""
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            self.tickets[ticket_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def add_message_to_ticket(self, ticket_id: str, role: str, content: str) -> bool:
        """Add a message to a ticket's conversation."""
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.tickets[ticket_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            return True
        return False


# Global instance
ticket_manager = SimpleTicketManager()
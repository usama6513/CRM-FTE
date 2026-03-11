"""
Customer Success Agent Prototype
This is a basic prototype that handles customer queries from multiple channels
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import os
from pathlib import Path


class CustomerSuccessAgent:
    def __init__(self, knowledge_base_path: str = "../../context/product-docs.md"):
        """Initialize the agent with knowledge base and customer history."""
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.customer_history = {}
        self.sentiment_threshold = 0.3  # Below this is negative sentiment

    def _load_knowledge_base(self, path: str) -> str:
        """Load product documentation to use as knowledge base."""
        # Get the directory where this file is located
        current_dir = Path(__file__).parent
        # Resolve the knowledge base path relative to the project root
        full_path = current_dir.parent.parent / "context" / "product-docs.md"

        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Warning: Knowledge base file not found at {full_path}")
            return "Product documentation unavailable"

    def _extract_customer_id(self, channel_info: Dict) -> str:
        """Extract or create a customer ID from channel information."""
        if channel_info.get('email'):
            return f"email_{channel_info['email']}"
        elif channel_info.get('phone'):
            return f"phone_{channel_info['phone']}"
        else:
            # Create a generic ID based on other available info
            import hashlib
            info_str = f"{channel_info.get('name', '')}{channel_info.get('subject', '')}"
            return f"generic_{hashlib.md5(info_str.encode()).hexdigest()[:8]}"

    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis - returns score between 0 (negative) and 1 (positive)."""
        # Simple keyword-based sentiment analysis
        positive_keywords = [
            'thank', 'good', 'great', 'excellent', 'awesome', 'perfect',
            'love', 'amazing', 'fantastic', 'happy', 'pleased', 'satisfied'
        ]
        negative_keywords = [
            'hate', 'bad', 'terrible', 'awful', 'horrible', 'angry',
            'frustrated', 'annoyed', 'upset', 'disappointed', 'sucks', 'worst'
        ]

        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)

        positive_count = sum(1 for word in words if word in positive_keywords)
        negative_count = sum(1 for word in words if word in negative_keywords)

        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.5  # Neutral if no sentiment words found

        # Calculate sentiment score (0 = very negative, 1 = very positive)
        sentiment_score = max(0, min(1, (positive_count + 1) / (total_sentiment_words + 2)))
        return sentiment_score

    def _should_escalate(self, user_message: str, sentiment_score: float) -> tuple[bool, str]:
        """Determine if the query should be escalated to human support."""
        user_lower = user_message.lower()

        # Check for pricing or billing mentions
        pricing_keywords = ['price', 'pricing', 'cost', 'payment', 'bill', 'charge', 'refund', 'cancel', 'discount', 'quote']
        for keyword in pricing_keywords:
            if keyword in user_lower:
                return True, f"pricing_inquiry: {keyword} mentioned"

        # Check for legal mentions
        legal_keywords = ['lawyer', 'legal', 'compliance', 'audit', 'subpoena', 'court', 'sue', 'lawsuit', 'attorney']
        for keyword in legal_keywords:
            if keyword in user_lower:
                return True, f"legal_inquiry: {keyword} mentioned"

        # Check sentiment
        if sentiment_score < self.sentiment_threshold:
            return True, f"negative_sentiment: score {sentiment_score} below threshold {self.sentiment_threshold}"

        # Check for explicit escalation requests
        escalation_keywords = ['human', 'agent', 'representative', 'speak to']
        for keyword in escalation_keywords:
            if keyword in user_lower and 'human' in user_lower:
                return True, f"human_requested: user asked for human support"

        return False, ""

    def _search_knowledge_base(self, query: str, max_results: int = 3) -> List[str]:
        """Search the knowledge base for relevant information."""
        # Simple keyword matching for prototype
        query_lower = query.lower()
        sentences = re.split(r'[.!?]+', self.knowledge_base)

        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count how many query words appear in the sentence
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in sentence_lower)
            if matches > 0:
                relevant_sentences.append((sentence.strip(), matches))

        # Sort by match count and return top results
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in relevant_sentences[:max_results] if item[0].strip()]

    def _format_response_for_channel(self, response: str, channel: str) -> str:
        """Format response appropriately for the channel."""
        if channel == "email":
            return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
This response was generated by our AI assistant. For complex issues, you can request human support."""

        elif channel == "whatsapp":
            # Keep it short for WhatsApp
            if len(response) > 300:
                response = response[:297] + "..."
            return f"{response}\n\n📱 Reply for more help or type 'human' for live support."

        else:  # web_form
            return f"""{response}

---
Need more help? Reply to this message or visit our support portal."""

    def _get_customer_history(self, customer_id: str) -> List[Dict]:
        """Get customer's interaction history."""
        return self.customer_history.get(customer_id, [])

    def _update_customer_history(self, customer_id: str, interaction: Dict):
        """Update customer's interaction history."""
        if customer_id not in self.customer_history:
            self.customer_history[customer_id] = []
        self.customer_history[customer_id].append(interaction)

    def process_query(self, message: str, channel_info: Dict, channel: str = "email") -> Dict:
        """
        Process a customer query and return a response.

        Args:
            message: The customer's message
            channel_info: Dict with channel-specific info (email, phone, name, etc.)
            channel: The channel the message came from ('email', 'whatsapp', 'web_form')

        Returns:
            Dict with response and metadata
        """
        # Extract customer ID
        customer_id = self._extract_customer_id(channel_info)

        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(message)

        # Check if escalation needed
        should_escalate, escalation_reason = self._should_escalate(message, sentiment_score)

        if should_escalate:
            response = f"I understand your concern. This requires specialized attention from our human support team. They will contact you within 2-4 hours. Reference: {customer_id[:8]}"
            response_type = "escalation"
        else:
            # Search knowledge base
            search_results = self._search_knowledge_base(message)

            if search_results:
                # Use search results to answer
                answer = "Based on our documentation: " + " ".join(search_results[:2])
                response = answer
            else:
                # Try to answer generically
                response = "Thank you for your inquiry. Based on our records, I recommend checking our documentation or contacting support for this specific issue. If you need more help, please provide additional details."

            response_type = "answered"

        # Format response for channel
        formatted_response = self._format_response_for_channel(response, channel)

        # Create interaction record
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "message": message,
            "response": formatted_response,
            "sentiment_score": sentiment_score,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason
        }

        # Update customer history
        self._update_customer_history(customer_id, interaction)

        return {
            "response": formatted_response,
            "customer_id": customer_id,
            "sentiment_score": sentiment_score,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason,
            "response_type": response_type
        }

# Example usage
if __name__ == "__main__":
    agent = CustomerSuccessAgent()

    # Test with different channels
    print("=== Email Channel Example ===")
    email_response = agent.process_query(
        "How do I import contacts?",
        {"email": "test@example.com", "name": "John Doe"},
        "email"
    )
    print(f"Response: {email_response['response']}")
    print(f"Escalated: {email_response['escalated']}")
    print()

    print("=== WhatsApp Channel Example ===")
    whatsapp_response = agent.process_query(
        "Can't login to my CRM account",
        {"phone": "+1234567890"},
        "whatsapp"
    )
    print(f"Response: {whatsapp_response['response']}")
    print(f"Escalated: {whatsapp_response['escalated']}")
    print()

    print("=== Web Form Channel Example ===")
    web_response = agent.process_query(
        "I need help with the API",
        {"email": "dev@example.com", "name": "Dev User"},
        "web_form"
    )
    print(f"Response: {web_response['response']}")
    print(f"Escalated: {web_response['escalated']}")
    print()

    print("=== Escalation Example ===")
    escalation_response = agent.process_query(
        "What are your enterprise pricing plans?",
        {"email": "business@example.com", "name": "Business User"},
        "email"
    )
    print(f"Response: {escalation_response['response']}")
    print(f"Escalated: {escalation_response['escalated']}")
    print(f"Reason: {escalation_response['escalation_reason']}")
"""
Unified Message Processor for Customer Success FTE
Consumes messages from all channels through Kafka and processes them with the agent
"""

import asyncio
import sys
import os
# Add the root directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kafka_client import FTEKafkaConsumer, TOPICS
from src.agent.customer_success_agent_production import CustomerSuccessAgent
from src.channels.gmail_handler import GmailHandler
from src.channels.whatsapp_handler import WhatsAppHandler
from datetime import datetime
import logging
import os
from enum import Enum
from database.queries import db_manager
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedMessageProcessor:
    """Process incoming messages from all channels through the FTE agent."""

    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            # Use a mock API key for prototype mode
            self.openai_api_key = "mock_api_key"

        self.agent = CustomerSuccessAgent(api_key=self.openai_api_key)
        self.gmail = GmailHandler()  # Initialize with appropriate credentials
        self.whatsapp = WhatsAppHandler()
        self.running = False

    async def start(self):
        """Start the message processor."""
        # Initialize database connection pool
        db_dsn = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fte_db")
        await db_manager.init_pool(db_dsn)

        consumer = FTEKafkaConsumer(
            topics=[TOPICS['tickets_incoming']],
            group_id='fte-message-processor'
        )
        await consumer.start()

        logger.info("Message processor started, listening for tickets...")
        self.running = True
        await consumer.consume(self.process_message)

    async def process_message(self, topic: str, message: dict):
        """Process a single incoming message from any channel."""
        try:
            start_time = datetime.utcnow()

            # Extract channel
            channel = Channel(message['channel'])

            # Get or create customer
            customer_id = await self.resolve_customer(message)

            # Get or create conversation
            conversation_id = await self.get_or_create_conversation(
                customer_id=customer_id,
                channel=channel,
                message=message
            )

            # Store incoming message
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel,
                direction='inbound',
                role='customer',
                content=message['content'],
                channel_message_id=message.get('channel_message_id')
            )

            # Load conversation history
            history = await self.load_conversation_history(conversation_id)

            # Run agent
            result = await self.run_agent_process(
                history=history,
                context={
                    'customer_id': customer_id,
                    'conversation_id': conversation_id,
                    'channel': channel.value,
                    'ticket_subject': message.get('subject', 'Support Request'),
                    'metadata': message.get('metadata', {})
                }
            )

            # Calculate metrics
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Store agent response
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel,
                direction='outbound',
                role='agent',
                content=result.output,
                latency_ms=latency_ms,
                tool_calls=result.tool_calls
            )

            # Publish metrics
            # This would publish to the metrics topic in a real implementation
            # await self.producer.publish(TOPICS['metrics'], {
            #     'event_type': 'message_processed',
            #     'channel': channel.value,
            #     'latency_ms': latency_ms,
            #     'escalated': result.escalated,
            #     'tool_calls_count': len(result.tool_calls)
            # })

            logger.info(f"Processed {channel.value} message in {latency_ms:.0f}ms")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.handle_error(message, e)

    async def resolve_customer(self, message: dict) -> str:
        """Resolve or create customer from message identifiers."""
        # Check for email first
        if email := message.get('customer_email'):
            customer = await db_manager.get_customer_by_email(email)
            if customer:
                return str(customer['id'])

            # Create new customer
            customer_id = await db_manager.create_customer(
                email=email,
                name=message.get('customer_name', '')
            )
            # Add email to identifiers
            await db_manager.create_customer_identifier(customer_id, 'email', email)
            return customer_id

        # Check for phone for WhatsApp
        if phone := message.get('customer_phone'):
            customer = await db_manager.get_customer_by_phone(phone)
            if customer:
                return str(customer['id'])

            # Create new customer with phone
            customer_id = await db_manager.create_customer(phone=phone)
            # Add phone to identifiers
            await db_manager.create_customer_identifier(customer_id, 'phone', phone)
            return customer_id

        raise ValueError("Could not resolve customer from message")

    async def get_or_create_conversation(
        self,
        customer_id: str,
        channel: Channel,
        message: dict
    ) -> str:
        """Get active conversation or create new one."""
        # Check for active conversation (within last 24 hours)
        active = await db_manager.get_active_conversation(customer_id)

        if active:
            return str(active['id'])

        # Create new conversation
        conversation_id = await db_manager.create_conversation(customer_id, channel)
        return conversation_id

    async def store_message(
        self,
        conversation_id: str,
        channel: Channel,
        direction: str,
        role: str,
        content: str,
        channel_message_id: str = None,
        latency_ms: float = None,
        tool_calls: list = None
    ):
        """Store message in the database."""
        await db_manager.create_message(
            conversation_id=conversation_id,
            channel=channel,
            direction=direction,
            role=role,
            content=content,
            channel_message_id=channel_message_id
        )

    async def load_conversation_history(self, conversation_id: str) -> list:
        """Load conversation history for the agent."""
        # Fetch messages from database
        messages = await db_manager.get_conversation_history(conversation_id)

        # Convert to the format expected by the agent
        formatted_history = []
        for msg in messages:
            formatted_history.append({
                "role": "user" if msg['role'] == 'customer' else 'assistant',
                "content": msg['content']
            })

        return formatted_history

    async def run_agent_process(self, history: list, context: dict):
        """Run the agent with the conversation history and context."""
        # For the prototype, we'll simulate the agent response
        # In a real implementation, this would use the OpenAI agent

        # Extract message content from history
        last_message = history[-1]['content'] if history else "Hello"

        # Process with the actual customer success agent
        result = self.agent.run(
            messages=history,
            context=context
        )

        # Create a result object that matches what the code expects
        class AgentResult:
            def __init__(self, output, escalated, tool_calls):
                self.output = output
                self.escalated = escalated
                self.tool_calls = tool_calls

        return AgentResult(
            output=result.get('output', ''),
            escalated=result.get('escalated', False),
            tool_calls=result.get('tool_calls', [])
        )

    async def handle_error(self, message: dict, error: Exception):
        """Handle processing errors gracefully."""
        # Send apologetic response via appropriate channel
        channel = Channel(message['channel'])
        apology = "I'm sorry, I'm having trouble processing your request right now. A human agent will follow up shortly."

        try:
            if channel == Channel.EMAIL and self.gmail:
                await self.gmail.send_reply(
                    to_email=message['customer_email'],
                    subject=message.get('subject', 'Support Request'),
                    body=apology
                )
            elif channel == Channel.WHATSAPP and self.whatsapp:
                await self.whatsapp.send_message(
                    to_phone=message['customer_phone'],
                    body=apology
                )
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")

        # Log escalation
        logger.error(f"Processing error for message: {message}, error: {error}")

    def stop(self):
        """Stop the message processor."""
        self.running = False


async def main():
    processor = UnifiedMessageProcessor()
    try:
        await processor.start()
    except KeyboardInterrupt:
        logger.info("Shutting down message processor...")
        processor.stop()
        await db_manager.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import sys
import os
# Add the root directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kafka_client import FTEKafkaConsumer, TOPICS
from src.agent.customer_success_agent_production import CustomerSuccessAgent
from database.queries import db_manager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalMessageProcessor:
    """Minimal message processor that bypasses problematic channel imports."""

    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        # Don't initialize agent here since it requires API connection
        # We'll handle the agent processing separately for testing
        self.running = False

    async def start(self):
        """Start the message processor."""
        # Initialize database connection pool
        db_dsn = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fte_db")
        await db_manager.init_pool(db_dsn)

        consumer = FTEKafkaConsumer(
            topics=[TOPICS['tickets_incoming']],
            group_id='fte-message-processor-minimal'
        )
        await consumer.start()

        logger.info("Minimal message processor started, listening for tickets...")
        self.running = True

        # For testing, let's just process a single test message instead of infinite loop
        test_message = {
            'channel': 'web_form',
            'customer_email': 'test@example.com',
            'customer_name': 'Test Customer',
            'subject': 'Test Inquiry',
            'content': 'Hello, I have a question about your service.',
            'category': 'general',
            'priority': 'medium',
            'received_at': datetime.utcnow().isoformat()
        }

        result = await self.process_message('fte.tickets.incoming', test_message)
        logger.info(f"Test processing completed: {result}")

        await consumer.stop()
        await db_manager.close_pool()
        return result

    async def process_message(self, topic: str, message: dict):
        """Process a single incoming message."""
        try:
            start_time = datetime.utcnow()

            # Extract channel
            from database.queries import Channel
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

            logger.info(f"Processed {channel.value} message in {latency_ms:.0f}ms")
            return {"status": "success", "latency_ms": latency_ms, "response": result.output}

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"status": "error", "error": str(e)}

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

    async def get_or_create_conversation(self, customer_id: str, channel, message: dict) -> str:
        """Get active conversation or create new one."""
        # Check for active conversation (within last 24 hours)
        active = await db_manager.get_active_conversation(customer_id)

        if active:
            return str(active['id'])

        # Create new conversation
        conversation_id = await db_manager.create_conversation(customer_id, channel)
        return conversation_id

    async def store_message(self, conversation_id: str, channel, direction: str, role: str, content: str, channel_message_id: str = None, latency_ms: float = None, tool_calls: list = None):
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
        # For testing purposes, return a mock response since actual agent needs API connection
        # In a real scenario, this would call the agent's run method
        return type('Result', (), {
            'output': 'Thank you for your inquiry. This is a test response from the Customer Success FTE agent. How else may I assist you?',
            'escalated': False,
            'tool_calls': []
        })()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable with your Groq API key")
        print("You can get a Groq API key from: https://console.groq.com/docs/keys")
        print("Use model 'openai/gpt-oss-20b' with Groq API")
        return

    processor = MinimalMessageProcessor()
    try:
        result = asyncio.run(processor.start())
        print(f"Test completed: {result}")
    except KeyboardInterrupt:
        print("Shutting down message processor...")
    except Exception as e:
        print(f"Error running processor: {e}")

if __name__ == "__main__":
    main()
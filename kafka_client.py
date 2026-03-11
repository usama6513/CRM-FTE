"""
Kafka Client for Customer Success FTE
Handles event streaming between channels and the agent
"""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from datetime import datetime
import os
from typing import Callable, Dict, Any


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# Topic definitions for multi-channel FTE
TOPICS = {
    # Incoming tickets from all channels
    'tickets_incoming': 'fte.tickets.incoming',

    # Channel-specific inbound
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',

    # Channel-specific outbound
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',

    # Escalations
    'escalations': 'fte.escalations',

    # Metrics and monitoring
    'metrics': 'fte.metrics',

    # Dead letter queue for failed processing
    'dlq': 'fte.dlq'
}


class FTEKafkaProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def publish(self, topic: str, event: dict):
        event["timestamp"] = datetime.utcnow().isoformat()
        await self.producer.send_and_wait(topic, event)


class FTEKafkaConsumer:
    def __init__(self, topics: list, group_id: str):
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def consume(self, handler: Callable):
        async for msg in self.consumer:
            await handler(msg.topic, msg.value)


# Global producer for use in other modules
producer = FTEKafkaProducer()


async def publish_to_kafka(topic: str, message: Dict[str, Any]):
    """
    Convenience function to publish messages to Kafka.
    This is used by various handlers to send messages to the agent.
    """
    await producer.start()  # Ensure producer is started
    await producer.publish(topic, message)
    # Note: In a real implementation, we might not want to stop/start for each message
    # This is a simplification for the prototype


async def setup_topics():
    """
    Setup topics if they don't exist.
    This would typically be handled by a Kafka admin client.
    """
    pass  # In a real implementation, this would use kafka.admin


# Initialize producer on module import
# async def init_kafka():
#     await producer.start()
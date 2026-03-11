"""
Database queries for the Customer Success FTE CRM system
Handles all PostgreSQL database operations using asyncpg
"""

import asyncpg
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def init_pool(self, dsn: str):
        """Initialize the connection pool."""
        self.pool = await asyncpg.create_pool(
            dsn,
            command_timeout=60,
            min_size=5,
            max_size=20
        )

    async def close_pool(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()

    async def create_customer(self, email: str = None, phone: str = None, name: str = None) -> str:
        """Create a new customer record and return customer ID."""
        async with self.pool.acquire() as conn:
            customer_id = await conn.fetchval("""
                INSERT INTO customers (email, phone, name)
                VALUES ($1, $2, $3)
                RETURNING id
            """, email, phone, name or "")

            return str(customer_id)

    async def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """Get customer by email address."""
        async with self.pool.acquire() as conn:
            customer = await conn.fetchrow("""
                SELECT id, email, phone, name, created_at, metadata
                FROM customers
                WHERE email = $1
            """, email)

            return dict(customer) if customer else None

    async def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number."""
        async with self.pool.acquire() as conn:
            customer = await conn.fetchrow("""
                SELECT id, email, phone, name, created_at, metadata
                FROM customers
                WHERE phone = $1
            """, phone)

            return dict(customer) if customer else None

    async def create_customer_identifier(self, customer_id: str, identifier_type: str, identifier_value: str):
        """Create a customer identifier for cross-channel matching."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, verified)
                VALUES ($1, $2, $3, TRUE)
            """, customer_id, identifier_type, identifier_value)

    async def get_customer_by_identifier(self, identifier_type: str, identifier_value: str) -> Optional[Dict]:
        """Get customer by identifier (email, phone, etc.)."""
        async with self.pool.acquire() as conn:
            # First check customer_identifiers table
            customer_identifier = await conn.fetchrow("""
                SELECT customer_id FROM customer_identifiers
                WHERE identifier_type = $1 AND identifier_value = $2
            """, identifier_type, identifier_value)

            if customer_identifier:
                customer = await conn.fetchrow("""
                    SELECT id, email, phone, name, created_at, metadata
                    FROM customers
                    WHERE id = $1
                """, customer_identifier['customer_id'])
                return dict(customer) if customer else None

            # If not found in identifiers, try direct match in customers table
            if identifier_type == 'email':
                return await self.get_customer_by_email(identifier_value)
            elif identifier_type == 'phone':
                return await self.get_customer_by_phone(identifier_value)

            return None

    async def create_conversation(self, customer_id: str, initial_channel: Channel) -> str:
        """Create a new conversation record and return conversation ID."""
        async with self.pool.acquire() as conn:
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (customer_id, initial_channel)
                VALUES ($1, $2)
                RETURNING id
            """, customer_id, initial_channel.value)

            return str(conversation_id)

    async def get_active_conversation(self, customer_id: str) -> Optional[Dict]:
        """Get active conversation for a customer (within last 24 hours)."""
        async with self.pool.acquire() as conn:
            conversation = await conn.fetchrow("""
                SELECT id, initial_channel, started_at, status
                FROM conversations
                WHERE customer_id = $1
                  AND status = 'active'
                  AND started_at > NOW() - INTERVAL '24 hours'
                ORDER BY started_at DESC
                LIMIT 1
            """, customer_id)

            return dict(conversation) if conversation else None

    async def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get all messages in a conversation."""
        async with self.pool.acquire() as conn:
            messages = await conn.fetch("""
                SELECT channel, direction, role, content, created_at, latency_ms
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
            """, conversation_id)

            return [dict(msg) for msg in messages]

    async def create_message(self, conversation_id: str, channel: Channel, direction: str,
                           role: str, content: str, channel_message_id: str = None):
        """Create a message record in the conversation."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (conversation_id, channel, direction, role, content, channel_message_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, conversation_id, channel.value, direction, role, content, channel_message_id)

    async def create_ticket(self, conversation_id: str, customer_id: str, source_channel: Channel,
                          category: str = None, priority: str = 'medium') -> str:
        """Create a support ticket and return ticket ID."""
        async with self.pool.acquire() as conn:
            ticket_id = await conn.fetchval("""
                INSERT INTO tickets (conversation_id, customer_id, source_channel, category, priority)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, conversation_id, customer_id, source_channel.value, category, priority)

            return str(ticket_id)

    async def update_ticket_status(self, ticket_id: str, status: str, resolution_notes: str = None):
        """Update ticket status and optionally add resolution notes."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE tickets
                SET status = $1, resolved_at = CASE WHEN $1 = 'resolved' THEN NOW() ELSE resolved_at END,
                    resolution_notes = COALESCE($2, resolution_notes)
                WHERE id = $3
            """, status, resolution_notes, ticket_id)

    async def search_knowledge_base(self, query_embedding: List[float], max_results: int = 5) -> List[Dict]:
        """Search knowledge base using vector similarity."""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT title, content,
                       1 - (embedding <=> $1::vector) as similarity
                FROM knowledge_base
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_embedding, max_results)

            return [dict(row) for row in results]

    async def add_knowledge_base_entry(self, title: str, content: str, category: str = None):
        """Add a new entry to the knowledge base."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO knowledge_base (title, content, category)
                VALUES ($1, $2, $3)
            """, title, content, category)

    async def get_customer_history(self, customer_id: str) -> List[Dict]:
        """Get complete customer history across all channels."""
        async with self.pool.acquire() as conn:
            history = await conn.fetch("""
                SELECT c.initial_channel, c.started_at, c.status,
                       m.content, m.role, m.channel, m.created_at
                FROM conversations c
                JOIN messages m ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                ORDER BY m.created_at DESC
                LIMIT 20
            """, customer_id)

            return [dict(row) for row in history]

    async def get_channel_metrics(self, days_back: int = 1) -> Dict[str, Any]:
        """Get performance metrics by channel."""
        async with self.pool.acquire() as conn:
            metrics = await conn.fetch("""
                SELECT
                    initial_channel as channel,
                    COUNT(*) as total_conversations,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) FILTER (WHERE status = 'escalated') as escalations
                FROM conversations
                WHERE started_at > NOW() - INTERVAL '$1 days'
                GROUP BY initial_channel
            """, days_back)

            return {row['channel']: dict(row) for row in metrics}

    async def record_metric(self, metric_name: str, metric_value: float, channel: Channel = None):
        """Record a performance metric."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_metrics (metric_name, metric_value, channel)
                VALUES ($1, $2, $3)
            """, metric_name, metric_value, channel.value if channel else None)

    async def get_channel_config(self, channel: Channel) -> Optional[Dict]:
        """Get configuration for a specific channel."""
        async with self.pool.acquire() as conn:
            config = await conn.fetchrow("""
                SELECT * FROM channel_configs WHERE channel = $1
            """, channel.value)

            return dict(config) if config else None

    async def update_channel_config(self, channel: Channel, config: Dict, enabled: bool = None):
        """Update configuration for a specific channel."""
        async with self.pool.acquire() as conn:
            # Check if channel config exists
            exists = await conn.fetchval("""
                SELECT id FROM channel_configs WHERE channel = $1
            """, channel.value)

            if exists:
                await conn.execute("""
                    UPDATE channel_configs
                    SET config = $1, enabled = COALESCE($2, enabled)
                    WHERE channel = $3
                """, config, enabled, channel.value)
            else:
                await conn.execute("""
                    INSERT INTO channel_configs (channel, config, enabled)
                    VALUES ($1, $2, $3)
                """, channel.value, config, enabled if enabled is not None else True)


# Global database instance
db_manager = DatabaseManager()
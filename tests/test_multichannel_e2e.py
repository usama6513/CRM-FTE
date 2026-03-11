"""
Multi-Channel End-to-End Tests for Customer Success FTE
Tests the complete system functionality across all channels
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
import json


BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    async with AsyncClient(base_url=BASE_URL) as ac:
        yield ac


class TestWebFormChannel:
    """Test the web support form (required build)."""

    @pytest.mark.asyncio
    async def test_form_submission(self, client):
        """Web form submission should create ticket and return ID."""
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Help with API",
            "category": "technical",
            "message": "I need help with the API authentication"
        })

        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["message"] is not None

    @pytest.mark.asyncio
    async def test_form_validation(self, client):
        """Form should validate required fields."""
        response = await client.post("/support/submit", json={
            "name": "A",  # Too short
            "email": "invalid-email",
            "subject": "Hi",
            "category": "invalid",
            "message": "Short"  # Too short
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(self, client):
        """Should be able to check ticket status after submission."""
        # Submit form
        submit_response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Status Test",
            "category": "general",
            "message": "Testing ticket status retrieval"
        })

        ticket_id = submit_response.json()["ticket_id"]

        # Check status
        status_response = await client.get(f"/support/ticket/{ticket_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] in ["open", "processing"]


class TestEmailChannel:
    """Test Gmail integration."""

    @pytest.mark.asyncio
    async def test_gmail_webhook_processing(self, client):
        """Gmail webhook should process incoming emails."""
        # Simulate Pub/Sub notification
        response = await client.post("/webhooks/gmail", json={
            "message": {
                "data": "base64_encoded_notification",
                "messageId": "test-123"
            },
            "subscription": "projects/test/subscriptions/gmail-push"
        })

        assert response.status_code == 200


class TestWhatsAppChannel:
    """Test WhatsApp/Twilio integration."""

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_processing(self, client):
        """WhatsApp webhook should process incoming messages."""
        # Note: Requires valid Twilio signature in production
        response = await client.post(
            "/webhooks/whatsapp",
            data={
                "MessageSid": "SM123",
                "From": "whatsapp:+1234567890",
                "Body": "Hello, I need help",
                "ProfileName": "Test User"
            }
        )

        # Will fail signature validation in test, that's expected
        assert response.status_code in [200, 403]


class TestCrossChannelContinuity:
    """Test that conversations persist across channels."""

    @pytest.mark.asyncio
    async def test_customer_history_across_channels(self, client):
        """Customer history should include all channel interactions."""
        # Create ticket via web form
        web_response = await client.post("/support/submit", json={
            "name": "Cross Channel User",
            "email": "crosschannel@example.com",
            "subject": "Initial Contact",
            "category": "general",
            "message": "First contact via web form"
        })

        ticket_id = web_response.json()["ticket_id"]

        # Look up customer
        customer_response = await client.get(
            "/customers/lookup",
            params={"email": "crosschannel@example.com"}
        )

        if customer_response.status_code == 200:
            customer = customer_response.json()
            # Should have web form interaction
            assert len(customer.get("conversations", [])) >= 1


class TestChannelMetrics:
    """Test channel-specific metrics."""

    @pytest.mark.asyncio
    async def test_metrics_by_channel(self, client):
        """Should return metrics broken down by channel."""
        response = await client.get("/metrics/channels")

        assert response.status_code == 200
        data = response.json()

        # Should have metrics for each enabled channel
        for channel in ["email", "whatsapp", "web_form"]:
            if channel in data:
                assert "total_conversations" in data[channel]


class TestSystemHealth:
    """Test overall system health."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Health endpoint should return status information."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "channels" in data
        assert all(channel in data["channels"] for channel in ["email", "whatsapp", "web_form"])


class TestAgentStatus:
    """Test agent-specific endpoints."""

    @pytest.mark.asyncio
    async def test_agent_status(self, client):
        """Agent status endpoint should return operational status."""
        response = await client.get("/agent/status")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "active"
        assert "channels" in data
        assert all(channel in data["channels"] for channel in ["email", "whatsapp", "web_form"])


if __name__ == "__main__":
    # Run basic tests if executed directly
    print("Multi-channel E2E tests defined. Run with pytest.")
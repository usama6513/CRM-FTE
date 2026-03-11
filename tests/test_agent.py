"""
Basic tests for the customer success agent prototype
"""

import pytest
from src.agent.customer_success_agent import CustomerSuccessAgent


def test_agent_initialization():
    """Test that the agent initializes correctly."""
    agent = CustomerSuccessAgent()
    assert agent is not None
    assert hasattr(agent, 'knowledge_base')
    assert hasattr(agent, 'customer_history')


def test_sentiment_analysis_positive():
    """Test sentiment analysis with positive text."""
    agent = CustomerSuccessAgent()
    positive_text = "This is great! I love your product, it's amazing!"
    sentiment = agent._analyze_sentiment(positive_text)
    assert 0.5 <= sentiment <= 1.0  # Should be more positive than neutral


def test_sentiment_analysis_negative():
    """Test sentiment analysis with negative text."""
    agent = CustomerSuccessAgent()
    negative_text = "I hate this product, it's terrible and awful!"
    sentiment = agent._analyze_sentiment(negative_text)
    assert 0.0 <= sentiment <= 0.5  # Should be more negative than neutral


def test_sentiment_analysis_neutral():
    """Test sentiment analysis with neutral text."""
    agent = CustomerSuccessAgent()
    neutral_text = "I need help with the API integration."
    sentiment = agent._analyze_sentiment(neutral_text)
    # Should be around neutral (0.5), give some tolerance
    assert 0.4 <= sentiment <= 0.6


def test_escalation_pricing():
    """Test that pricing-related queries are escalated."""
    agent = CustomerSuccessAgent()

    pricing_queries = [
        "What are your pricing plans?",
        "How much does the enterprise plan cost?",
        "I want to know about your pricing structure",
        "Can you provide a quote for 20 users?"
    ]

    for query in pricing_queries:
        should_escalate, reason = agent._should_escalate(query, 0.8)
        assert should_escalate, f"Query '{query}' should be escalated"
        assert "pricing" in reason.lower()


def test_escalation_negative_sentiment():
    """Test that negative sentiment triggers escalation."""
    agent = CustomerSuccessAgent()
    message = "This is terrible and I'm very frustrated!"

    should_escalate, reason = agent._should_escalate(message, 0.1)  # Low sentiment
    assert should_escalate, "Low sentiment message should be escalated"
    assert "negative_sentiment" in reason


def test_knowledge_base_search():
    """Test that knowledge base search returns relevant results."""
    agent = CustomerSuccessAgent()

    # Search for "contacts" which should be in the knowledge base
    results = agent._search_knowledge_base("contacts", max_results=2)

    assert len(results) > 0, "Should find results for 'contacts'"
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0


def test_customer_id_extraction():
    """Test customer ID extraction from channel info."""
    agent = CustomerSuccessAgent()

    # Test email-based ID
    email_info = {"email": "test@example.com", "name": "Test User"}
    email_id = agent._extract_customer_id(email_info)
    assert email_id.startswith("email_")
    assert "test@example.com" in email_id

    # Test phone-based ID
    phone_info = {"phone": "+1234567890"}
    phone_id = agent._extract_customer_id(phone_info)
    assert phone_id.startswith("phone_")
    assert "+1234567890" in phone_id


def test_response_formatting_email():
    """Test email response formatting."""
    agent = CustomerSuccessAgent()
    response = "This is a test response."
    formatted = agent._format_response_for_channel(response, "email")

    assert "Dear Customer" in formatted
    assert "Best regards" in formatted
    assert "TechCorp AI Support Team" in formatted


def test_response_formatting_whatsapp():
    """Test WhatsApp response formatting."""
    agent = CustomerSuccessAgent()
    response = "This is a test response."
    formatted = agent._format_response_for_channel(response, "whatsapp")

    assert "more help" in formatted
    assert "human" in formatted
    assert "for live support" in formatted


def test_response_formatting_web_form():
    """Test web form response formatting."""
    agent = CustomerSuccessAgent()
    response = "This is a test response."
    formatted = agent._format_response_for_channel(response, "web_form")

    assert "Need more help?" in formatted
    assert "support portal" in formatted


def test_process_query_basic():
    """Test basic query processing."""
    agent = CustomerSuccessAgent()

    result = agent.process_query(
        "How do I create a new contact?",
        {"email": "test@example.com", "name": "Test User"},
        "email"
    )

    assert "response" in result
    assert "customer_id" in result
    assert "sentiment_score" in result
    assert "escalated" in result
    assert "response_type" in result

    # Should not be escalated for a basic help query
    assert not result["escalated"]


def test_process_query_escalation():
    """Test that pricing queries are escalated."""
    agent = CustomerSuccessAgent()

    result = agent.process_query(
        "What are your enterprise pricing plans?",
        {"email": "business@example.com", "name": "Business User"},
        "email"
    )

    assert result["escalated"]
    assert "pricing" in result["escalation_reason"].lower()


def test_customer_history():
    """Test customer history tracking."""
    agent = CustomerSuccessAgent()

    # Process a query
    result = agent.process_query(
        "How do I import contacts?",
        {"email": "test@example.com", "name": "Test User"},
        "email"
    )

    # Check that history was updated
    customer_id = result["customer_id"]
    history = agent._get_customer_history(customer_id)

    assert len(history) == 1
    assert history[0]["message"] == "How do I import contacts?"
    assert history[0]["channel"] == "email"


if __name__ == "__main__":
    # Run basic tests
    test_agent_initialization()
    test_sentiment_analysis_positive()
    test_sentiment_analysis_negative()
    test_sentiment_analysis_neutral()
    test_escalation_pricing()
    test_escalation_negative_sentiment()
    test_knowledge_base_search()
    test_customer_id_extraction()
    test_response_formatting_email()
    test_response_formatting_whatsapp()
    test_response_formatting_web_form()
    test_process_query_basic()
    test_process_query_escalation()
    test_customer_history()

    print("All tests passed!")
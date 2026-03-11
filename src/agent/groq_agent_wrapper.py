"""
Groq API Wrapper for Customer Success FTE
Provides OpenAI-compatible interface for Groq API to avoid library compatibility issues
"""
import httpx
import json
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class GroqClient:
    """A minimal Groq API client that mimics OpenAI's interface for basic operations."""

    def __init__(self, api_key: str = None, base_url: str = "https://api.groq.com/openai/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  # Using same env var for compatibility
        if not self.api_key:
            raise ValueError("API key is required")
        self.base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completions_create(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """Mimic OpenAI's chat.completions.create method."""
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        with httpx.Client() as client:
            response = client.post(url, headers=self._headers, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()

    def beta_assistants_create(self, name: str, instructions: str, model: str, tools: List[Dict]):
        """Create a Groq-compatible assistant."""
        # For local testing, we'll create a placeholder assistant
        # In a real implementation, this would call Groq's API
        return MockAssistant(id="asst_groq_local_123", name=name, model=model)


class MockAssistant:
    """Mock assistant object to simulate OpenAI's assistant object."""

    def __init__(self, id: str, name: str, model: str):
        self.id = id
        self.name = name
        self.model = model


class MockThread:
    """Mock thread object to simulate OpenAI's thread object."""

    def __init__(self, id: str, messages: List[Dict[str, str]] = None):
        self.id = id
        self.messages = messages or []


class MockRun:
    """Mock run object to simulate OpenAI's run object."""

    def __init__(self, id: str, thread_id: str, assistant_id: str, status: str = "completed"):
        self.id = id
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.status = status
        self.required_action = None  # For tool calls


class GroqAssistantClient:
    """Wrapper for Groq API that mimics OpenAI's Assistant API."""

    def __init__(self, api_key: str = None):
        self.client = GroqClient(api_key)

    def beta(self):
        return self

    @property
    def assistants(self):
        return self

    @property
    def threads(self):
        return self

    def create(self, name: str, instructions: str, model: str, tools: List[Dict] = None):
        """Create a Groq assistant."""
        return self.client.beta_assistants_create(name, instructions, model, tools or [])

    def delete(self, assistant_id: str):
        """Mock assistant deletion."""
        return {"id": assistant_id, "deleted": True}

    def create_thread(self, messages: List[Dict[str, str]] = None):
        """Create a thread."""
        import uuid
        return MockThread(id=f"thread_{uuid.uuid4().hex[:8]}", messages=messages)

    def runs(self):
        return self

    def create_run(self, thread_id: str, assistant_id: str, **kwargs):
        """Create a run."""
        import uuid
        return MockRun(id=f"run_{uuid.uuid4().hex[:8]}", thread_id=thread_id, assistant_id=assistant_id)

    def retrieve(self, thread_id: str, run_id: str = None):
        """Retrieve a run."""
        if run_id:
            return MockRun(id=run_id, thread_id=thread_id, assistant_id="mock", status="completed")
        else:
            # Return thread if only thread_id is provided
            return MockThread(id=thread_id)

    def retrieve_run(self, thread_id: str, run_id: str):
        """Retrieve a specific run."""
        return MockRun(id=run_id, thread_id=thread_id, assistant_id="mock", status="completed")

    def submit_tool_outputs(self, thread_id: str, run_id: str, tool_outputs: List[Dict]):
        """Submit tool outputs."""
        return MockRun(id=run_id, thread_id=thread_id, assistant_id="mock", status="completed")


def get_groq_client(api_key: str = None):
    """Factory function to get a Groq client that mimics OpenAI interface."""
    return GroqAssistantClient(api_key)
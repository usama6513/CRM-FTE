import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Customer Success FTE - Simple Test")
print("=" * 40)

# Test importing core components with fallback systems
try:
    print("1. Testing agent import...")
    from src.agent.customer_success_agent_production import CustomerSuccessAgent, OPENAI_AVAILABLE
    print(f"   [SUCCESS] Agent imported (OpenAI available: {OPENAI_AVAILABLE})")

    print("2. Testing tools import...")
    from src.agent import tools
    print(f"   [SUCCESS] Tools imported (using {'Pydantic models' if tools.PYDANTIC_AVAILABLE else 'Fallback models'})")

    print("3. Testing database import...")
    from database.queries import db_manager, Channel
    print(f"   [SUCCESS] Database manager imported")
    print(f"   [INFO] Channel enum: {list(Channel)}")

    print("4. Testing API import (with error handling)...")
    try:
        from fastapi import FastAPI
        print("   [SUCCESS] FastAPI imported")
    except Exception as e:
        print(f"   [WARNING] FastAPI import issue: {str(e)[:100]}...")

    print("5. Testing environment variables...")
    api_key = os.getenv("OPENAI_API_KEY")
    db_url = os.getenv("DATABASE_URL")
    print(f"   [INFO] API Key set: {bool(api_key)}")
    print(f"   [INFO] DB URL: {db_url}")

    print("\n" + "=" * 40)
    print("PARTIAL SYSTEM TEST PASSED!")
    print("Core components are working with fallback systems.")
    print("=" * 40)
    print("\nTo run the full system, you would need:")
    print("1. A running PostgreSQL database")
    print("2. A running Kafka server")
    print("3. Proper API keys")
    print("\nCurrently, the system works in fallback mode without full functionality.")

except Exception as e:
    print(f"Error during import: {e}")
    import traceback
    traceback.print_exc()
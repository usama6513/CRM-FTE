"""
Local test setup for Customer Success FTE with Groq API
Verifies that all components work with local environment compatibility fixes
"""
import sys
import os

# Add root directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing local setup for Customer Success FTE...")

# Test basic imports
try:
    from src.agent.customer_success_agent_production import CustomerSuccessAgent
    print("[SUCCESS] CustomerSuccessAgent import successful")
except Exception as e:
    print(f"[ERROR] CustomerSuccessAgent import failed: {e}")

try:
    from src.agent import tools
    print("[SUCCESS] Tools import successful")
    # Test creating an input object
    if tools.PYDANTIC_AVAILABLE:
        print("   Using Pydantic models")
    else:
        print("   Using fallback models")
except Exception as e:
    print(f"[ERROR] Tools import failed: {e}")

try:
    from kafka_client import TOPICS
    print(f"[SUCCESS] Kafka client import successful, topics: {len(TOPICS)} available")
except Exception as e:
    print(f"[ERROR] Kafka client import failed: {e}")

try:
    from database.queries import db_manager
    print("[SUCCESS] Database manager import successful")
except Exception as e:
    print(f"[ERROR] Database manager import failed: {e}")

# Test environment variables
print("\nChecking environment variables:")
required_vars = [
    "OPENAI_API_KEY",  # This should be your Groq API key
    "DATABASE_URL",
    "KAFKA_BOOTSTRAP_SERVERS"
]

for var in required_vars:
    if os.getenv(var):
        print(f"[SET] {var} is set")
    else:
        print(f"[NOT SET] {var} not set (will use default)")

print("\nCustomer Success FTE local setup verification complete!")
print("\nTo run the API service:")
print("  cd src/api && python main.py")
print("\nTo run the message processor:")
print("  cd src/workers && python message_processor.py")

# Check if using Groq API
api_key = os.getenv("OPENAI_API_KEY", "")
if "groq" in api_key.lower():
    print("\n[SUCCESS] Using Groq API key for gpt-oss-20b model")
else:
    print(f"\n[INFO] Using API key: {'Set' if api_key else 'Not set'}")
    print("   Remember to use your Groq API key with model 'openai/gpt-oss-20b'")
#!/usr/bin/env python3
"""
Test script to verify Pydantic compatibility fixes
"""

import sys
import os

# Add the root directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules import without Pydantic errors."""
    print("Testing imports for Pydantic compatibility...")

    try:
        print("1. Testing tools import...")
        from src.agent import tools
        print("   ✓ Tools imported successfully")

        print("2. Testing customer_success_agent_production import...")
        from src.agent import customer_success_agent_production
        print("   ✓ Customer Success Agent imported successfully")

        print("3. Testing message_processor import...")
        from src.workers import message_processor
        print("   ✓ Message Processor imported successfully")

        print("4. Testing whatsapp_handler import...")
        from src.channels import whatsapp_handler
        print("   ✓ WhatsApp Handler imported successfully")

        print("5. Testing database queries import...")
        from database import queries
        print("   ✓ Database queries imported successfully")

        print("\nAll imports completed successfully! Pydantic compatibility issues appear to be fixed.")
        return True

    except Exception as e:
        print(f"Error during import test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pydantic_models():
    """Test that Pydantic models can be instantiated without errors."""
    print("\nTesting Pydantic model instantiation...")

    try:
        from src.agent.tools import (
            KnowledgeSearchInput, TicketInput,
            EscalationInput, ResponseInput, Channel
        )

        print("1. Testing KnowledgeSearchInput...")
        ksi = KnowledgeSearchInput(query="test query", max_results=5)
        print(f"   ✓ KnowledgeSearchInput created: {ksi.query}")

        print("2. Testing TicketInput...")
        ti = TicketInput(
            customer_id="test_customer",
            issue="test issue",
            channel=Channel.EMAIL
        )
        print(f"   ✓ TicketInput created: {ti.customer_id}, {ti.channel}")

        print("3. Testing EscalationInput...")
        ei = EscalationInput(ticket_id="test_ticket", reason="test reason")
        print(f"   ✓ EscalationInput created: {ei.ticket_id}")

        print("4. Testing ResponseInput...")
        ri = ResponseInput(
            ticket_id="test_ticket",
            message="test message",
            channel=Channel.WHATSAPP
        )
        print(f"   ✓ ResponseInput created: {ri.ticket_id}, {ri.channel}")

        print("\nAll Pydantic models instantiated successfully!")
        return True

    except Exception as e:
        print(f"Error during Pydantic model test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running Pydantic compatibility tests...\n")

    imports_ok = test_imports()
    models_ok = test_pydantic_models()

    if imports_ok and models_ok:
        print("\n🎉 All tests passed! Pydantic compatibility issues have been resolved.")
        print("The AI Message Processor should now run without errors.")
    else:
        print("\n❌ Some tests failed. Please review the error messages above.")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test Gemini AI Integration
"""
from core.config import settings
from services.gemini_service import GeminiService

print("="*60)
print("GEMINI AI TEST")
print("="*60)

print(f"\nGemini Enabled: {settings.USE_GEMINI_AI}")
print(f"API Key Set: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
print(f"Model: {settings.GEMINI_MODEL}")

gemini = GeminiService()
print(f"\nGemini Service Enabled: {gemini.enabled}")

if gemini.enabled:
    print("\n--- Testing Gemini Chat ---")
    response = gemini.chat("Hello, how are you?", "en")

    if response.get("success"):
        print(f"[SUCCESS] Chat test passed!")
        print(f"Response: {response.get('response')}")
    else:
        print(f"[FAILED] Chat test failed!")
        print(f"Error: {response.get('error')}")

    print("\n--- Testing Intent Analysis ---")
    intent_result = gemini.analyze_intent("create a task to buy groceries", "en")

    if intent_result.get("success"):
        print(f"[SUCCESS] Intent analysis passed!")
        print(f"Intent: {intent_result.get('intent')}")
        print(f"Confidence: {intent_result.get('confidence')}")
    else:
        print(f"[FAILED] Intent analysis failed!")
        print(f"Error: {intent_result.get('error')}")
else:
    print("\n[ERROR] Gemini is not enabled!")
    print("Check your .env file:")
    print("  USE_GEMINI_AI=True")
    print("  GEMINI_API_KEY=your-api-key-here")

print("\n" + "="*60)

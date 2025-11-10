#!/usr/bin/env python3
"""
List Available Gemini Models
"""
import google.generativeai as genai
from core.config import settings

print("="*60)
print("LISTING AVAILABLE GEMINI MODELS")
print("="*60)

if not settings.GEMINI_API_KEY:
    print("\n[ERROR] No API key configured!")
    exit(1)

print(f"\nUsing API Key: {settings.GEMINI_API_KEY[:20]}...")

genai.configure(api_key=settings.GEMINI_API_KEY)

print("\nAvailable Models:")
print("-"*60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\nModel Name: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supported Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"\n[ERROR] Failed to list models: {e}")
    print("\nTrying alternative approach...")
    try:
        # Try with just the API
        import requests
        response = requests.get(
            f"https://generativelanguage.googleapis.com/v1/models?key={settings.GEMINI_API_KEY}"
        )
        print(f"\nAPI Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\nModels from API:")
            for model in data.get('models', []):
                print(f"  - {model.get('name')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e2:
        print(f"[ERROR] Alternative approach failed: {e2}")

print("\n" + "="*60)

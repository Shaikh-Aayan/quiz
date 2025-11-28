#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clear the Railway database by calling the DELETE endpoint"""

import requests
import json

BACKEND_URL = "https://quiz-production-cf4b.up.railway.app"

print("="*70)
print("🧹 CLEARING RAILWAY DATABASE")
print("="*70)

# Call the DELETE endpoint
print("\n📤 Calling DELETE /questions/all endpoint...")
try:
    response = requests.delete(f"{BACKEND_URL}/questions/all", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS: Deleted {data.get('deleted_count', 0)} questions")
    else:
        print(f"\n❌ FAILED: {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
print("Now upload fresh PDFs - they should work correctly!")
print("="*70)

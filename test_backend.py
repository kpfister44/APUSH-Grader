#!/usr/bin/env python3
"""Simple test script to verify the backend is working"""

import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/Users/kyle.pfister/APUSH-Grader/backend')

try:
    # Import and test the app
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    print("Testing backend endpoints...")
    
    # Test health endpoint
    print("\n1. Testing /health endpoint:")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test grading endpoint with sample data
    print("\n2. Testing /api/v1/grade endpoint:")
    test_request = {
        "essay_text": "The American Revolution was a significant event in history that changed the course of the nation. The colonists fought for independence from British rule due to various factors including taxation without representation. This struggle lasted from 1775 to 1783 and resulted in the formation of the United States of America.",
        "essay_type": "LEQ",
        "prompt": "Evaluate the extent to which the American Revolution changed American society in the period from 1775 to 1800."
    }
    
    response = client.post("/api/v1/grade", json=test_request)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Score: {result['score']}/{result['max_score']}")
        print(f"Letter Grade: {result['letter_grade']}")
        print(f"Performance Level: {result['performance_level']}")
        print("✅ Backend is working correctly!")
    else:
        print(f"Error: {response.text}")
    
except Exception as e:
    print(f"❌ Error testing backend: {e}")
    import traceback
    traceback.print_exc()
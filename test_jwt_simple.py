#!/usr/bin/env python3
"""
Simple test script to verify JWT authentication works with the FastAPI goals API
"""

import requests
import json
import sys

# Test JWT token provided by the user
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItZGVtbyIsImVtYWlsIjoidGVzdC5kZW1vQGV4YW1wbGUuY29tIiwibmFtZSI6IkRlbW8gVGVzdCBVc2VyIiwidGVzdF9hY2NvdW50Ijp0cnVlLCJpc192ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzYyOTcwNTMyfQ.QY265AVFyHEElwNoT1L1-w4oZMEXjTMI7Zpkm1m2w88"

def main():
    print("🚀 Testing JWT Authentication for FastAPI Goals API")
    print("=" * 60)
    
    # Test 1: Health endpoint (no auth required)
    print("🧪 Test 1: Health endpoint (should work without auth)")
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ SUCCESS: Health endpoint works without auth")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ FAILED: Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 2: Protected endpoint without token (should fail)
    print("🧪 Test 2: Protected endpoint WITHOUT token (should return 401)")
    try:
        response = requests.get("http://localhost:8000/api/crud-goals")
        if response.status_code == 401:
            print("✅ SUCCESS: Correctly rejected request without token")
        else:
            print(f"❌ FAILED: Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 3: Protected endpoint with valid token (should work)
    print("🧪 Test 3: Protected endpoint WITH valid token (should work)")
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    try:
        response = requests.get("http://localhost:8000/api/crud-goals", headers=headers)
        if response.status_code == 200:
            print("✅ SUCCESS: Authenticated request worked")
            goals = response.json()
            print(f"Found {len(goals)} goals")
        elif response.status_code == 401:
            print("❌ FAILED: Token was rejected")
            print(f"Error: {response.json()}")
        else:
            print(f"⚠️  UNEXPECTED: Got status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    # Test 4: Create goal with auth
    print("🧪 Test 4: Create goal with authentication")
    goal_data = {
        "title": "JWT Test Goal",
        "description": "Testing JWT authentication",
        "priority": "high",
        "goal_type": "monthly"
    }
    try:
        response = requests.post("http://localhost:8000/api/crud-goals", 
                               headers=headers, json=goal_data)
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS: Goal created with authentication")
            result = response.json()
            print(f"Created: {result.get('message', 'Success')}")
        elif response.status_code == 401:
            print("❌ FAILED: Token was rejected for goal creation")
        else:
            print(f"⚠️  UNEXPECTED: Got status {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print()
    
    print("=" * 60)
    print("🎉 JWT Authentication Test Complete!")

if __name__ == "__main__":
    main()
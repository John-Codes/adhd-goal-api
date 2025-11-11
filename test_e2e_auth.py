#!/usr/bin/env python3
"""
Comprehensive E2E tests for Goals API and LLM endpoint with authentication
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the real API key from environment for testing
REAL_API_KEY = os.getenv("OPENROUTER_API_KEY", "test-key-12345")
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItZGVtbyIsImVtYWlsIjoidGVzdC5kZW1vQGV4YW1wbGUuY29tIiwibmFtZSI6IkRlbW8gVGVzdCBVc2VyIiwidGVzdF9hY2NvdW50Ijp0cnVlLCJpc192ZXJpZmllZCI6dHJ1ZSwiZXhwIjoxNzYyOTcwNTMyfQ.QY265AVFyHEElwNoT1L1-w4oZMEXjTMI7Zpkm1m2w88"

BASE_URL = "http://localhost:8000"

def get_headers():
    """Get request headers with JWT token"""
    return {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }

def test_health_check():
    """Test if the API server is running"""
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("PASS: Health check")
            return True
        else:
            print("FAIL: Server not responding correctly")
            return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Cannot connect to server - {e}")
        return False

def test_list_goals():
    """Test listing goals"""
    print("2. Testing List CRUD Goals...")
    try:
        response = requests.get(f"{BASE_URL}/api/crud-goals", headers=get_headers())
        print(f"Status: {response.status_code}")
        goals = response.json()
        print(f"Found {len(goals)} goals")
        if goals:
            print(f"First goal: {goals[0]['goalTitle']}")
        print("PASS: List goals")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_create_goal():
    """Test creating a goal"""
    print("3. Testing Create Goal...")
    try:
        goal_data = {
            "title": "Test API Goal",
            "description": "Testing the API functionality",
            "priority": "high",
            "goal_type": "monthly",
            "tags": ["test", "api", "validation"],
            "deadline_days": 30
        }
        response = requests.post(f"{BASE_URL}/api/crud-goals", json=goal_data, headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
            if "goal" in result and "_id" in result["goal"]:
                goal_id = result["goal"]["_id"]
                print(f"PASS: Create goal! Goal ID: {goal_id}")
                return goal_id
            else:
                print("FAIL: No goal ID in response")
                return None
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"FAIL: {e}")
        return None

def test_get_goal(goal_id):
    """Test getting a specific goal"""
    print("4. Testing Get Specific Goal...")
    try:
        response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}", headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            goal = response.json()
            print(f"Goal Title: {goal['goalTitle']}")
            print(f"Goal Text: {goal['goalText']}")
            print("PASS: Get goal")
            return True
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_update_goal(goal_id):
    """Test updating a goal"""
    print("5. Testing Update Goal...")
    try:
        update_data = {
            "title": "Updated Test Goal",
            "description": "Goal has been updated successfully",
            "priority": "medium",
            "status": "active",
            "tags": ["test", "updated", "api"]
        }
        response = requests.put(f"{BASE_URL}/api/crud-goals/{goal_id}", json=update_data, headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
            print("PASS: Update goal")
            return True
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_delete_goal(goal_id):
    """Test deleting a goal"""
    print("6. Testing Delete Goal...")
    try:
        response = requests.delete(f"{BASE_URL}/api/crud-goals/{goal_id}", headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
            print("PASS: Delete goal")
            return True
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_llm_without_api_key():
    """Test LLM endpoint without providing API key (should use environment variable)"""
    print("7. Testing LLM endpoint without API key (uses env var)...")
    try:
        request_data = {
            "message": "Help me with my goals for this week",
            "model": "tngtech/deepseek-r1t2-chimera:free"
        }
        
        response = requests.post(f"{BASE_URL}/api/llmquerygoals", json=request_data, headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            if "response" in result:
                response_text = result["response"]
                print("Response snippet:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                print("PASS: LLM endpoint without API key")
                return True
            else:
                print("FAIL: No response field in response")
                return False
        else:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"FAIL: {response.status_code} - {error_detail}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Request error - {e}")
        return False

def test_llm_with_api_key():
    """Test LLM endpoint with explicit API key"""
    print("8. Testing LLM endpoint with explicit API key...")
    try:
        request_data = {
            "message": "What are some productivity tips for ADHD?",
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "api_key": REAL_API_KEY  # Use real API key from environment
        }
        
        response = requests.post(f"{BASE_URL}/api/llmquerygoals", json=request_data, headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            if "response" in result:
                response_text = result["response"]
                print("Response snippet:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                print("PASS: LLM endpoint with API key")
                return True
            else:
                print("FAIL: No response field in response")
                return False
        else:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"FAIL: {response.status_code} - {error_detail}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Request error - {e}")
        return False

def test_llm_chat_history():
    """Test LLM endpoint with chat history"""
    print("9. Testing LLM endpoint with chat history...")
    try:
        request_data = {
            "message": "Can you help me prioritize these?",
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "chat_history": [
                {"role": "user", "content": "I have 5 goals to complete this month"},
                {"role": "assistant", "content": "That's a lot! Which 3 are most critical?"},
                {"role": "user", "content": "Actually, let me focus on just 2"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/api/llmquerygoals", json=request_data, headers=get_headers())
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            if "response" in result:
                response_text = result["response"]
                print("Response snippet:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                print("PASS: LLM endpoint with chat history")
                return True
            else:
                print("FAIL: No response field in response")
                return False
        else:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"FAIL: {response.status_code} - {error_detail}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Request error - {e}")
        return False

def main():
    """Run all E2E tests"""
    print("Comprehensive E2E Testing for Goals API and LLM Endpoint (WITH AUTH)")
    print("=" * 70)
    
    # Check if server is running
    if not test_health_check():
        print("Cannot proceed with tests - server not running")
        print("Please start the API server first with: python run_api.py")
        return
    
    # Run all tests
    tests_passed = 0
    total_tests = 9  # Excluding health check
    
    if test_list_goals():
        tests_passed += 1
    
    goal_id = test_create_goal()
    if goal_id:
        tests_passed += 1
        if test_get_goal(goal_id):
            tests_passed += 1
        if test_update_goal(goal_id):
            tests_passed += 1
        if test_delete_goal(goal_id):
            tests_passed += 1
    
    if test_llm_without_api_key():
        tests_passed += 1
    
    if test_llm_with_api_key():
        tests_passed += 1
    
    if test_llm_chat_history():
        tests_passed += 1
    
    print("=" * 70)
    print(f"E2E Tests Complete: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("SUCCESS: All tests passed! The API is working correctly with authentication.")
    else:
        print("WARNING: Some tests failed. Check the server logs for more details.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the API server is running: python run_api.py")
        print("2. Verify OPENROUTER_API_KEY is set in your environment")
        print("3. Check that port 8000 is not blocked by firewall")
        print("4. MongoDB connection issues may prevent goals CRUD operations")

if __name__ == "__main__":
    main()
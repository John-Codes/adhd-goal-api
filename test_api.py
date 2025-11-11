#!/usr/bin/env python3
"""
Simple test script to verify the cleaned API functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    print("1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "goals_count" in response.json()
    print("PASS: Health check\n")

def test_list_goals():
    print("2. Testing List CRUD Goals...")
    response = requests.get(f"{BASE_URL}/api/crud-goals")
    print(f"Status: {response.status_code}")
    goals = response.json()
    print(f"Found {len(goals)} goals")
    if goals:
        print(f"First goal: {goals[0]['goalTitle']}")
    print("PASS: List goals\n")

def test_create_goal():
    print("3. Testing Create Goal...")
    goal_data = {
        "name": "Test API Goal",
        "description": "Testing the cleaned API functionality",
        "due_date": None
    }
    response = requests.post(f"{BASE_URL}/api/crud-goals", json=goal_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "goal" in response.json()
    goal_id = response.json()["goal"]["_id"]
    print(f"PASS: Create goal! Goal ID: {goal_id}\n")
    return goal_id

def test_get_goal(goal_id):
    print("4. Testing Get Specific Goal...")
    response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}")
    print(f"Status: {response.status_code}")
    goal = response.json()
    print(f"Goal Title: {goal['goalTitle']}")
    print(f"Goal Text: {goal['goalText']}")
    assert response.status_code == 200
    assert goal["_id"] == goal_id
    print("PASS: Get goal\n")
    return goal

def test_update_goal(goal_id):
    print("5. Testing Update Goal...")
    update_data = {
        "name": "Updated Test Goal",
        "description": "Goal has been updated successfully",
        "due_date": None
    }
    response = requests.put(f"{BASE_URL}/api/crud-goals/{goal_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "goal" in response.json()
    print("PASS: Update goal\n")

def test_delete_goal(goal_id):
    print("6. Testing Delete Goal...")
    response = requests.delete(f"{BASE_URL}/api/crud-goals/{goal_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json()
    print("PASS: Delete goal\n")

def main():
    print("Testing Cleaned Goals API\n")
    
    # Test basic functionality
    test_health_check()
    test_list_goals()
    
    # Test CRUD operations
    goal_id = test_create_goal()
    test_get_goal(goal_id)
    test_update_goal(goal_id)
    test_delete_goal(goal_id)
    
    print("SUCCESS: All tests passed! The cleaned API is working correctly.")

if __name__ == "__main__":
    main()
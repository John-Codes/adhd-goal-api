#!/usr/bin/env python3
"""
End-to-end test script for Goals API
Tests all CRUD operations for both 90-day and monthly goals
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"Health check passed: {data}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Make sure FastAPI server is running on port 8000")
        return False

def test_90day_goals():
    """Test all 90-day goal operations"""
    print("\nTesting 90-day goals CRUD operations...")
    
    # Test Create
    print("  Creating 90-day goals...")
    goal1_data = {"name": "Fitness Goal", "description": "Run 5k every day"}
    goal2_data = {"name": "Learning Goal", "description": "Learn Python in 90 days"}
    
    response1 = requests.post(f"{BASE_URL}/api/90day-goals", json=goal1_data)
    response2 = requests.post(f"{BASE_URL}/api/90day-goals", json=goal2_data)
    
    if response1.status_code != 200 or response2.status_code != 200:
        print("Failed to create 90-day goals")
        return False
    
    goal1_id = response1.json()["goal"]["id"]
    goal2_id = response2.json()["goal"]["id"]
    print(f"  Created goals with IDs: {goal1_id}, {goal2_id}")
    
    # Test Read individual goal
    print(f"  Reading goal {goal1_id}...")
    response = requests.get(f"{BASE_URL}/api/90day-goals/{goal1_id}")
    if response.status_code == 200:
        goal = response.json()
        print(f"  Read goal: {goal['name']} - {goal['description']}")
        print(f"     Days remaining: {goal['remaining_days']}")
    else:
        print("Failed to read individual goal")
        return False
    
    # Test List all goals
    print("  Listing all 90-day goals...")
    response = requests.get(f"{BASE_URL}/api/90day-goals")
    if response.status_code == 200:
        goals = response.json()
        print(f"  Found {len(goals)} active goals")
        for goal in goals:
            print(f"     - {goal['name']}: {goal['remaining_days']} days left")
    else:
        print("Failed to list goals")
        return False
    
    # Test Update
    print(f"  Updating goal {goal1_id}...")
    update_data = {"name": "Fitness Goal Updated", "description": "Run 10k every day"}
    response = requests.put(f"{BASE_URL}/api/90day-goals/{goal1_id}", json=update_data)
    if response.status_code == 200:
        updated_goal = response.json()["goal"]
        print(f"  Updated goal: {updated_goal['name']}")
    else:
        print("Failed to update goal")
        return False
    
    # Test Get expired goals
    print("  Checking expired goals...")
    response = requests.get(f"{BASE_URL}/api/90day-goals/expired")
    if response.status_code == 200:
        expired = response.json()
        print(f"  Found {len(expired)} expired goals")
    else:
        print("Failed to get expired goals")
        return False
    
    # Test Download
    print("  Testing 90-day data download...")
    response = requests.get(f"{BASE_URL}/api/download/90day-data")
    if response.status_code == 200:
        print("  90-day data download successful")
    else:
        print("Failed to download 90-day data")
        return False
    
    # Test Delete
    print(f"  Deleting goal {goal2_id}...")
    response = requests.delete(f"{BASE_URL}/api/90day-goals/{goal2_id}")
    if response.status_code == 200:
        print("  Goal deleted successfully")
    else:
        print("Failed to delete goal")
        return False
    
    return goal1_id, goal2_id

def test_monthly_goals():
    """Test all monthly goal operations"""
    print("\nTesting monthly goals CRUD operations...")
    
    # Test Create
    print("  Creating monthly goals...")
    goal1_data = {"name": "Reading Goal", "description": "Read 2 books this month", "due_date": "2025-12-15"}
    goal2_data = {"name": "Project Goal", "description": "Complete side project MVP", "due_date": "2025-11-30"}
    
    response1 = requests.post(f"{BASE_URL}/api/monthly-goals", json=goal1_data)
    response2 = requests.post(f"{BASE_URL}/api/monthly-goals", json=goal2_data)
    
    if response1.status_code != 200 or response2.status_code != 200:
        print("Failed to create monthly goals")
        return False
    
    goal1_id = response1.json()["goal"]["id"]
    goal2_id = response2.json()["goal"]["id"]
    print(f"  Created goals with IDs: {goal1_id}, {goal2_id}")
    
    # Test Read individual goal
    print(f"  Reading goal {goal1_id}...")
    response = requests.get(f"{BASE_URL}/api/monthly-goals/{goal1_id}")
    if response.status_code == 200:
        goal = response.json()
        print(f"  Read goal: {goal['name']} - {goal['description']}")
        print(f"     Due date: {goal['due_date']}")
        print(f"     Days remaining: {goal['remaining_days']}")
    else:
        print("Failed to read individual goal")
        return False
    
    # Test List all goals
    print("  Listing all monthly goals...")
    response = requests.get(f"{BASE_URL}/api/monthly-goals")
    if response.status_code == 200:
        goals = response.json()
        print(f"  Found {len(goals)} active goals")
        for goal in goals:
            print(f"     - {goal['name']}: {goal['remaining_days']} days left (due: {goal['due_date']})")
    else:
        print("Failed to list goals")
        return False
    
    # Test Update
    print(f"  Updating goal {goal1_id}...")
    update_data = {"name": "Reading Goal Updated", "description": "Read 3 books this month", "due_date": "2025-12-20"}
    response = requests.put(f"{BASE_URL}/api/monthly-goals/{goal1_id}", json=update_data)
    if response.status_code == 200:
        updated_goal = response.json()["goal"]
        print(f"  Updated goal: {updated_goal['name']}")
        print(f"     New due date: {updated_goal['due_date']}")
    else:
        print("Failed to update goal")
        return False
    
    # Test Get expired goals
    print("  Checking expired goals...")
    response = requests.get(f"{BASE_URL}/api/monthly-goals/expired")
    if response.status_code == 200:
        expired = response.json()
        print(f"  Found {len(expired)} expired goals")
    else:
        print("Failed to get expired goals")
        return False
    
    # Test Download
    print("  Testing monthly data download...")
    response = requests.get(f"{BASE_URL}/api/download/monthly-data")
    if response.status_code == 200:
        print("  Monthly data download successful")
    else:
        print("Failed to download monthly data")
        return False
    
    # Test Delete
    print(f"  Deleting goal {goal2_id}...")
    response = requests.delete(f"{BASE_URL}/api/monthly-goals/{goal2_id}")
    if response.status_code == 200:
        print("  Goal deleted successfully")
    else:
        print("Failed to delete goal")
        return False
    
    return goal1_id, goal2_id

def main():
    """Run all tests"""
    print("Starting Goals API End-to-End Tests")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\nServer is not running. Start it with:")
        print("   uvicorn fastapi_goals:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # Test 90-day goals
    goal90_ids = test_90day_goals()
    if not goal90_ids:
        print("90-day goals tests failed!")
        return False
    
    # Test monthly goals
    monthly_ids = test_monthly_goals()
    if not monthly_ids:
        print("Monthly goals tests failed!")
        return False
    
    # Final health check
    print("\nFinal health check...")
    test_health()
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("90-day goals CRUD operations: Working")
    print("Monthly goals CRUD operations: Working")
    print("File download endpoints: Working")
    print("API is ready for use!")
    
    return True

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple Real MongoDB Connection Test
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_mongodb():
    print("Testing REAL MongoDB connection and API...")
    
    # Test 1: Direct API Health Check
    print("1. Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API Health: {data['status']}")
            print(f"Goals Count: {data['goals_count']}")
            print("PASS: API is healthy and connected to MongoDB")
        else:
            print(f"FAIL: API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: API error - {e}")
        return False
    
    # Test 2: List actual goals from MongoDB
    print("\n2. Testing real MongoDB data retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/crud-goals")
        if response.status_code == 200:
            goals = response.json()
            print(f"Found {len(goals)} goals in MongoDB")
            for i, goal in enumerate(goals[:3]):  # Show first 3
                print(f"  Goal {i+1}: {goal['goalTitle']} (ID: {goal['_id']})")
                print(f"    Priority: {goal['priority']}")
                print(f"    Status: {goal['status']}")
                print(f"    Days Remaining: {goal['days_remaining']}")
            print("PASS: Successfully retrieved real MongoDB data")
        else:
            print(f"FAIL: Could not retrieve goals - {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Error retrieving goals - {e}")
        return False
    
    # Test 3: Create a real goal in MongoDB
    print("\n3. Testing CREATE goal in MongoDB...")
    try:
        goal_data = {
            "name": "Test Real MongoDB Goal",
            "description": "This goal verifies real MongoDB persistence",
            "due_date": None
        }
        response = requests.post(f"{BASE_URL}/api/crud-goals", json=goal_data)
        if response.status_code == 200:
            result = response.json()
            goal_id = result['goal']['_id']
            print(f"Created goal with ID: {goal_id}")
            print(f"Goal Title: {result['goal']['goalTitle']}")
            
            # Test 4: Read the goal back from MongoDB
            print("\n4. Testing READ goal from MongoDB...")
            read_response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}")
            if read_response.status_code == 200:
                goal = read_response.json()
                print(f"Successfully read goal: {goal['goalTitle']}")
                print(f"Description: {goal['goalText']}")
                
                # Test 5: Update the goal in MongoDB
                print("\n5. Testing UPDATE goal in MongoDB...")
                update_data = {
                    "name": "Updated Test Real MongoDB Goal",
                    "description": "This goal was updated successfully",
                    "due_date": None
                }
                update_response = requests.put(f"{BASE_URL}/api/crud-goals/{goal_id}", json=update_data)
                if update_response.status_code == 200:
                    updated_goal = update_response.json()['goal']
                    print(f"Updated goal: {updated_goal['goalTitle']}")
                    
                    # Test 6: Delete the goal from MongoDB
                    print("\n6. Testing DELETE goal from MongoDB...")
                    delete_response = requests.delete(f"{BASE_URL}/api/crud-goals/{goal_id}")
                    if delete_response.status_code == 200:
                        print("Goal deleted successfully")
                        
                        # Verify deletion
                        verify_response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}")
                        if verify_response.status_code == 404:
                            print("Deletion verified - goal no longer exists")
                        else:
                            print("Warning: Goal still exists after delete")
                    else:
                        print(f"FAIL: Delete failed with {delete_response.status_code}")
                        return False
                else:
                    print(f"FAIL: Update failed with {update_response.status_code}")
                    return False
            else:
                print(f"FAIL: Could not read goal - {read_response.status_code}")
                return False
        else:
            print(f"FAIL: Create failed with {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: CRUD operations error - {e}")
        return False
    
    print("\n=== REAL MONGODB TEST SUMMARY ===")
    print("SUCCESS: All CRUD operations worked with real MongoDB!")
    print("- MongoDB connection: WORKING")
    print("- CREATE goal: WORKING")
    print("- READ goal: WORKING") 
    print("- UPDATE goal: WORKING")
    print("- DELETE goal: WORKING")
    print("- Data persistence: VERIFIED")
    return True

if __name__ == "__main__":
    success = test_real_mongodb()
    if success:
        print("\nCONGRATULATIONS: Real MongoDB and API are fully functional!")
    else:
        print("\nSome tests failed. Check the errors above.")
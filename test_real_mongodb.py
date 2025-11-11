#!/usr/bin/env python3
"""
Real MongoDB connection and CRUD operations test
No mocks - only real database testing
"""
import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mongodb_handler import MongoDBHandler
from goals import GoalMonth

BASE_URL = "http://localhost:8000"

def test_mongodb_connection():
    """Test direct MongoDB connection"""
    print("1. Testing Direct MongoDB Connection...")
    try:
        # Test MongoDB connection directly
        mongo_handler = MongoDBHandler()
        print(f"✓ MongoDB URI: {mongo_handler.mongodb_uri}")
        print(f"✓ Database Name: {mongo_handler.database_name}")
        print(f"✓ Collection Name: {mongo_handler.collection_name}")
        print("✓ MongoDB connection successful!")
        
        # Test basic database operations
        db = mongo_handler.db
        collection = mongo_handler.collection
        print(f"✓ Connected to database: {db.name}")
        print(f"✓ Using collection: {collection.name}")
        
        # List some collections to verify access
        collections = db.list_collection_names()
        print(f"✓ Available collections: {collections}")
        
        mongo_handler.close_connection()
        print("✓ MongoDB connection test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def test_direct_goals_crud():
    """Test Goals class directly against MongoDB"""
    print("2. Testing Direct Goals CRUD Operations...")
    try:
        goals_tracker = GoalMonth(collection_name="goals", user_id="testuser001")
        
        # CREATE: Test creating a goal
        print("  - Testing CREATE...")
        goal_id = goals_tracker.create(
            goal_title="Test Goal - MongoDB Verification",
            goal_text="This goal verifies real MongoDB persistence",
            priority="high",
            tags=["test", "mongodb", "verification"]
        )
        print(f"  ✓ Goal created with ID: {goal_id}")
        
        # READ: Test reading the goal back
        print("  - Testing READ...")
        goal = goals_tracker.read(goal_id)
        if goal:
            print(f"  ✓ Goal read successfully: {goal['goalTitle']}")
            print(f"  ✓ Goal text: {goal['goalText']}")
            print(f"  ✓ Goal priority: {goal['priority']}")
            print(f"  ✓ Goal tags: {goal['tags']}")
        else:
            print("  ✗ Failed to read goal")
            return False
        
        # UPDATE: Test updating the goal
        print("  - Testing UPDATE...")
        success = goals_tracker.update(
            goal_id,
            goal_title="Updated Test Goal - MongoDB Verification",
            goal_text="This goal has been updated successfully",
            priority="medium"
        )
        if success:
            updated_goal = goals_tracker.read(goal_id)
            print(f"  ✓ Goal updated successfully: {updated_goal['goalTitle']}")
            print(f"  ✓ New priority: {updated_goal['priority']}")
        else:
            print("  ✗ Failed to update goal")
            return False
        
        # LIST: Test listing goals
        print("  - Testing LIST...")
        all_goals = goals_tracker.list_goals()
        print(f"  ✓ Found {len(all_goals)} total goals for user")
        
        # DELETE: Test deleting the goal
        print("  - Testing DELETE...")
        delete_success = goals_tracker.delete(goal_id)
        if delete_success:
            # Verify it's deleted
            deleted_goal = goals_tracker.read(goal_id)
            if not deleted_goal:
                print(f"  ✓ Goal deleted successfully")
            else:
                print(f"  ✗ Goal still exists after delete")
                return False
        else:
            print("  ✗ Failed to delete goal")
            return False
        
        goals_tracker.close_connection()
        print("✓ Direct Goals CRUD test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Direct Goals CRUD test failed: {e}")
        return False

def test_api_end_to_end():
    """Test full API endpoints with real data persistence"""
    print("3. Testing API End-to-End CRUD Operations...")
    try:
        # Test health check
        print("  - Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✓ API is healthy. Goals count: {health_data.get('goals_count', 'N/A')}")
        else:
            print(f"  ✗ Health check failed: {response.status_code}")
            return False
        
        # CREATE: Test creating goal via API
        print("  - Testing CREATE via API...")
        goal_data = {
            "name": "API Test Goal - Real MongoDB",
            "description": "This goal tests real API-to-MongoDB persistence",
            "due_date": None
        }
        create_response = requests.post(f"{BASE_URL}/api/crud-goals", json=goal_data)
        if create_response.status_code == 200:
            create_result = create_response.json()
            goal_id = create_result["goal"]["_id"]
            print(f"  ✓ Goal created via API with ID: {goal_id}")
        else:
            print(f"  ✗ Create via API failed: {create_response.status_code}")
            print(f"  Response: {create_response.text}")
            return False
        
        # READ: Test reading goal via API
        print("  - Testing READ via API...")
        read_response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}")
        if read_response.status_code == 200:
            goal = read_response.json()
            print(f"  ✓ Goal read via API: {goal['goalTitle']}")
            print(f"  ✓ Goal description: {goal['goalText']}")
        else:
            print(f"  ✗ Read via API failed: {read_response.status_code}")
            return False
        
        # UPDATE: Test updating goal via API
        print("  - Testing UPDATE via API...")
        update_data = {
            "name": "Updated API Test Goal - Real MongoDB",
            "description": "This goal has been updated via API",
            "due_date": None
        }
        update_response = requests.put(f"{BASE_URL}/api/crud-goals/{goal_id}", json=update_data)
        if update_response.status_code == 200:
            updated_goal = update_response.json()["goal"]
            print(f"  ✓ Goal updated via API: {updated_goal['goalTitle']}")
        else:
            print(f"  ✗ Update via API failed: {update_response.status_code}")
            return False
        
        # LIST: Test listing goals via API
        print("  - Testing LIST via API...")
        list_response = requests.get(f"{BASE_URL}/api/crud-goals")
        if list_response.status_code == 200:
            goals = list_response.json()
            print(f"  ✓ Found {len(goals)} goals via API")
            # Verify our test goal is in the list
            test_goal_found = any(g['_id'] == goal_id for g in goals)
            if test_goal_found:
                print(f"  ✓ Test goal verified in list")
            else:
                print(f"  ✗ Test goal not found in list")
                return False
        else:
            print(f"  ✗ List via API failed: {list_response.status_code}")
            return False
        
        # DELETE: Test deleting goal via API
        print("  - Testing DELETE via API...")
        delete_response = requests.delete(f"{BASE_URL}/api/crud-goals/{goal_id}")
        if delete_response.status_code == 200:
            print(f"  ✓ Goal deleted via API")
            
            # Verify deletion
            verify_response = requests.get(f"{BASE_URL}/api/crud-goals/{goal_id}")
            if verify_response.status_code == 404:
                print(f"  ✓ Goal deletion verified - goal no longer accessible")
            else:
                print(f"  ✗ Goal still accessible after delete")
                return False
        else:
            print(f"  ✗ Delete via API failed: {delete_response.status_code}")
            return False
        
        print("✓ API End-to-End test PASSED\n")
        return True
    except Exception as e:
        print(f"✗ API End-to-End test failed: {e}")
        return False

def verify_data_persistence():
    """Verify data is actually persisting in MongoDB"""
    print("4. Verifying Data Persistence in MongoDB...")
    try:
        # Direct MongoDB query to verify data
        mongo_handler = MongoDBHandler()
        db = mongo_handler.db
        goals_collection = db["goals"]
        
        # Count goals
        total_goals = goals_collection.count_documents({"isDeleted": False})
        print(f"  ✓ Total active goals in MongoDB: {total_goals}")
        
        # List some recent goals
        recent_goals = list(goals_collection.find({"isDeleted": False}).sort("createdAt", -1).limit(3))
        print(f"  ✓ Recent goals in MongoDB:")
        for i, goal in enumerate(recent_goals, 1):
            print(f"    {i}. {goal.get('goalTitle', 'No title')} (ID: {goal.get('_id')})")
            print(f"       Created: {goal.get('createdAt')}")
            print(f"       Priority: {goal.get('priority')}")
        
        mongo_handler.close_connection()
        print("✓ Data persistence verification PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Data persistence verification failed: {e}")
        return False

def main():
    print("=== REAL MONGODB & API END-TO-END TESTING ===")
    print("Testing with actual MongoDB connection and data persistence\n")
    
    tests = [
        ("MongoDB Connection", test_mongodb_connection),
        ("Direct Goals CRUD", test_direct_goals_crud),
        ("API End-to-End", test_api_end_to_end),
        ("Data Persistence", verify_data_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"{test_name} test FAILED\n")
        except Exception as e:
            print(f"{test_name} test FAILED with exception: {e}\n")
    
    print("=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! MongoDB and API are working correctly with real data persistence.")
    else:
        print("❌ Some tests failed. Please check the MongoDB connection and API functionality.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from mongodb_handler import MongoDBHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoalMonth:
    """A MongoDB-backed monthly goal tracker with CRUD operations."""
    
    def __init__(self, collection_name: str = "goals", user_id: Optional[str] = None):
        """
        Initialize the GoalMonth tracker with MongoDB.
        
        Args:
            collection_name: MongoDB collection name for goals
            user_id: User ID for filtering goals (ObjectId string)
        """
        # Initialize MongoDB handler with goals collection
        self.mongo_handler = MongoDBHandler()
        # Override the collection settings for goals
        self.collection_name = collection_name
        # Make sure the database is connected
        if self.mongo_handler.db is not None:
            self.collection = self.mongo_handler.db[collection_name]
        else:
            raise Exception("Failed to connect to MongoDB database")
        
        self.user_id = user_id or "000000000000000000000001"  # Default test user ID
        
        logger.info(f"GoalMonth initialized with collection: {collection_name}")
    
    def create(self, goal_title: str, goal_text: str, priority: str = "medium",
               goal_type: str = "monthly", tags: Optional[List[str]] = None, deadline_days: int = 30) -> str:
        """
        Create a new goal with MongoDB integration.
        
        Args:
            goal_title: Title of the goal
            goal_text: Description of the goal
            priority: "high", "medium", or "low"
            goal_type: "monthly" or "quarterly"
            tags: List of tags for categorization
            deadline_days: Days until deadline (30 for monthly, 90 for quarterly)
            
        Returns:
            str: MongoDB ObjectId as string
        """
        now = datetime.now(timezone.utc)
        # Calculate deadline - add days to current date
        deadline = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        deadline = deadline.replace(day=min(deadline.day + deadline_days, 28))  # Handle month boundaries
        
        goal_data = {
            "userId": ObjectId(self.user_id),
            "goalType": goal_type,
            "goalText": goal_text,
            "goalTitle": goal_title,
            "priority": priority,
            "status": "active",
            "tags": tags or [],
            "createdAt": now,
            "updatedAt": now,
            "deadline": deadline,
            "isDeleted": False
        }
        
        try:
            result = self.collection.insert_one(goal_data)
            goal_id = str(result.inserted_id)
            logger.info(f"Created goal with ID: {goal_id}")
            return goal_id
        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            raise
    
    def read(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a goal by ID and calculate remaining days.
        
        Args:
            goal_id: MongoDB ObjectId as string
            
        Returns:
            Dict or None: Goal data with calculated fields
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(goal_id)
            
            # Find goal for current user
            query = {
                "_id": object_id,
                "userId": ObjectId(self.user_id),
                "isDeleted": False
            }
            
            goal = self.collection.find_one(query)
            if not goal:
                return None
            
            # Calculate remaining days
            now = datetime.now(timezone.utc)
            deadline = goal["deadline"]
            
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            
            # Ensure both datetimes have timezone info
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            
            remaining_days = (deadline - now).days
            
            # Convert ObjectId to string for JSON serialization
            goal_copy = goal.copy()
            goal_copy["_id"] = str(goal_copy["_id"])
            goal_copy["userId"] = str(goal_copy["userId"])
            goal_copy["days_remaining"] = max(0, remaining_days)
            goal_copy["is_expired"] = remaining_days < 0
            goal_copy["is_due_today"] = remaining_days == 0
            
            # Convert datetime objects to ISO strings
            if isinstance(goal_copy["createdAt"], datetime):
                goal_copy["createdAt"] = goal_copy["createdAt"].isoformat()
            if isinstance(goal_copy["updatedAt"], datetime):
                goal_copy["updatedAt"] = goal_copy["updatedAt"].isoformat()
            if isinstance(goal_copy["deadline"], datetime):
                goal_copy["deadline"] = goal_copy["deadline"].isoformat()
            
            return goal_copy
            
        except Exception as e:
            logger.error(f"Error reading goal {goal_id}: {e}")
            return None
    
    def update(self, goal_id: str, goal_title: Optional[str] = None, 
               goal_text: Optional[str] = None, priority: Optional[str] = None,
               status: Optional[str] = None, tags: Optional[List[str]] = None,
               deadline: Optional[str] = None) -> bool:
        """
        Update an existing goal.
        
        Args:
            goal_id: MongoDB ObjectId as string
            goal_title: New title (optional)
            goal_text: New description (optional)
            priority: New priority (optional)
            status: New status (optional)
            tags: New tags (optional)
            deadline: New deadline ISO string (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            object_id = ObjectId(goal_id)
            
            # Build update query
            update_fields = {}
            
            if goal_title is not None:
                update_fields["goalTitle"] = goal_title
            if goal_text is not None:
                update_fields["goalText"] = goal_text
            if priority is not None:
                update_fields["priority"] = priority
            if status is not None:
                update_fields["status"] = status
            if tags is not None:
                update_fields["tags"] = tags
            if deadline is not None:
                update_fields["deadline"] = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            
            # Always update the updatedAt timestamp
            update_fields["updatedAt"] = datetime.now(timezone.utc)
            
            # Update goal for current user
            query = {
                "_id": object_id,
                "userId": ObjectId(self.user_id),
                "isDeleted": False
            }
            
            result = self.collection.update_one(
                query,
                {"$set": update_fields}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated goal {goal_id}")
                return True
            else:
                logger.warning(f"Goal {goal_id} not found or not modified")
                return False
                
        except Exception as e:
            logger.error(f"Error updating goal {goal_id}: {e}")
            return False
    
    def delete(self, goal_id: str) -> bool:
        """
        Delete a goal (soft delete).
        
        Args:
            goal_id: MongoDB ObjectId as string
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            object_id = ObjectId(goal_id)
            
            # Soft delete - mark as deleted
            query = {
                "_id": object_id,
                "userId": ObjectId(self.user_id),
                "isDeleted": False
            }
            
            update = {
                "isDeleted": True,
                "status": "deleted",
                "updatedAt": datetime.now(timezone.utc)
            }
            
            result = self.collection.update_one(query, {"$set": update})
            
            if result.modified_count > 0:
                logger.info(f"Deleted goal {goal_id}")
                return True
            else:
                logger.warning(f"Goal {goal_id} not found or already deleted")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting goal {goal_id}: {e}")
            return False
    
    def list_goals(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all active goals for the current user.
        
        Args:
            status_filter: Optional status filter ("active", "completed", "archived")
            
        Returns:
            List[Dict]: List of goal data
        """
        try:
            # Build query
            query = {
                "userId": ObjectId(self.user_id),
                "isDeleted": False
            }
            
            if status_filter:
                query["status"] = status_filter
            
            # Find goals and sort by created date (newest first)
            cursor = self.collection.find(query).sort("createdAt", -1)
            
            goals = []
            now = datetime.now(timezone.utc)
            
            for goal in cursor:
                # Calculate remaining days
                deadline = goal["deadline"]
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                
                # Ensure both datetimes have timezone info
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=timezone.utc)
                
                remaining_days = (deadline - now).days
                
                # Prepare goal data
                goal_data = {
                    "_id": str(goal["_id"]),
                    "userId": str(goal["userId"]),
                    "goalType": goal["goalType"],
                    "goalText": goal["goalText"],
                    "goalTitle": goal["goalTitle"],
                    "priority": goal["priority"],
                    "status": goal["status"],
                    "tags": goal["tags"],
                    "createdAt": goal["createdAt"].isoformat() if isinstance(goal["createdAt"], datetime) else goal["createdAt"],
                    "updatedAt": goal["updatedAt"].isoformat() if isinstance(goal["updatedAt"], datetime) else goal["updatedAt"],
                    "deadline": goal["deadline"].isoformat() if isinstance(goal["deadline"], datetime) else goal["deadline"],
                    "days_remaining": max(0, remaining_days),
                    "is_expired": remaining_days < 0,
                    "is_due_today": remaining_days == 0
                }
                
                goals.append(goal_data)
            
            logger.info(f"Found {len(goals)} goals for user {self.user_id}")
            return goals
            
        except Exception as e:
            logger.error(f"Error listing goals: {e}")
            return []
    
    def get_expired_goals(self) -> List[Dict[str, Any]]:
        """
        Get all expired goals (past deadline).
        
        Returns:
            List[Dict]: List of expired goal data
        """
        try:
            now = datetime.now(timezone.utc)
            
            query = {
                "userId": ObjectId(self.user_id),
                "isDeleted": False,
                "deadline": {"$lt": now},
                "status": {"$ne": "completed"}  # Don't include completed goals
            }
            
            cursor = self.collection.find(query).sort("deadline", 1)
            
            expired_goals = []
            for goal in cursor:
                goal_data = {
                    "_id": str(goal["_id"]),
                    "goalTitle": goal["goalTitle"],
                    "goalText": goal["goalText"],
                    "deadline": goal["deadline"].isoformat() if isinstance(goal["deadline"], datetime) else goal["deadline"],
                    "priority": goal["priority"],
                    "status": goal["status"]
                }
                expired_goals.append(goal_data)
            
            return expired_goals
            
        except Exception as e:
            logger.error(f"Error getting expired goals: {e}")
            return []
    
    def get_due_today_goals(self) -> List[Dict[str, Any]]:
        """
        Get all goals due today.
        
        Returns:
            List[Dict]: List of due-today goal data
        """
        try:
            today = datetime.now(timezone.utc).date()
            tomorrow = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
            tomorrow = tomorrow.replace(day=tomorrow.day + 1)
            
            start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.utc)
            
            query = {
                "userId": ObjectId(self.user_id),
                "isDeleted": False,
                "deadline": {
                    "$gte": start_of_day,
                    "$lt": tomorrow
                }
            }
            
            cursor = self.collection.find(query)
            
            due_today_goals = []
            for goal in cursor:
                goal_data = {
                    "_id": str(goal["_id"]),
                    "goalTitle": goal["goalTitle"],
                    "goalText": goal["goalText"],
                    "deadline": goal["deadline"].isoformat() if isinstance(goal["deadline"], datetime) else goal["deadline"],
                    "priority": goal["priority"],
                    "status": goal["status"]
                }
                due_today_goals.append(goal_data)
            
            return due_today_goals
            
        except Exception as e:
            logger.error(f"Error getting due-today goals: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection."""
        self.mongo_handler.close_connection()


def main():
    """Test the MongoDB-backed monthly goal tracker."""
    print("=== MongoDB Goal Tracker Test ===\n")
    
    tracker = None
    try:
        # Initialize tracker
        tracker = GoalMonth(collection_name="goals", user_id="000000000000000000000001")
        
        # Test Create operations
        print("1. Creating goals...")
        goal1_id = tracker.create(
            goal_title="Fitness Goal",
            goal_text="Run 3x per week",
            priority="high",
            tags=["fitness", "health"]
        )
        
        goal2_id = tracker.create(
            goal_title="Reading Challenge",
            goal_text="Read 2 books this month",
            priority="medium",
            goal_type="monthly",
            tags=["reading", "education"]
        )
        
        goal3_id = tracker.create(
            goal_title="Project Deadline",
            goal_text="Complete side project MVP",
            priority="high",
            deadline_days=7,  # Due next week
            tags=["project", "development"]
        )
        
        print(f"Created goals with IDs: {goal1_id}, {goal2_id}, {goal3_id}")
        
        # Test Read operations
        print("\n2. Reading goals with details:")
        for goal_id in [goal1_id, goal2_id, goal3_id]:
            goal = tracker.read(goal_id)
            if goal:
                print(f"Goal {goal['_id']} - {goal['goalTitle']}: {goal['goalText']}")
                print(f"  Priority: {goal['priority']}")
                print(f"  Status: {goal['status']}")
                print(f"  Deadline: {goal['deadline']}")
                print(f"  Days remaining: {goal['days_remaining']}")
                if goal.get('is_expired'):
                    print("  ⚠️  EXPIRED!")
                if goal.get('is_due_today'):
                    print("  🔔 DUE TODAY!")
                print(f"  Tags: {goal['tags']}")
                print()
        
        # Test Update
        print("3. Updating goal 1...")
        tracker.update(goal1_id,
                      goal_title="Fitness Goal Updated",
                      goal_text="Run 4x per week",
                      priority="high",
                      status="active")
        
        updated_goal = tracker.read(goal1_id)
        if updated_goal:
            print(f"Updated: {updated_goal['goalTitle']} - {updated_goal['goalText']}")
            print(f"Priority: {updated_goal['priority']}")
        
        # Test List all goals
        print("\n4. All active goals:")
        all_goals = tracker.list_goals()
        for goal in all_goals:
            print(f"  {goal['_id']}: {goal['goalTitle']} - {goal['goalText']} ({goal['days_remaining']} days left)")
            print(f"     Priority: {goal['priority']}, Status: {goal['status']}")
        
        # Test Filter by status
        print("\n5. High priority goals:")
        high_priority_goals = [g for g in all_goals if g['priority'] == 'high']
        for goal in high_priority_goals:
            print(f"  {goal['goalTitle']}: {goal['goalText']} (Status: {goal['status']})")
        
        # Test Delete
        print("\n6. Deleting goal 2...")
        success = tracker.delete(goal2_id)
        print(f"Delete successful: {success}")
        
        # Verify deletion
        deleted_goal = tracker.read(goal2_id)
        print(f"Goal still accessible after delete: {deleted_goal is not None}")
        
        # Final list
        print("\n7. Final goal list (after delete):")
        final_goals = tracker.list_goals()
        for goal in final_goals:
            print(f"  {goal['_id']}: {goal['goalTitle']} - {goal['goalText']} ({goal['days_remaining']} days left)")
        
        # Test expired goals
        print("\n8. Expired goals:")
        expired = tracker.get_expired_goals()
        if expired:
            for goal in expired:
                print(f"  {goal['_id']}: {goal['goalTitle']} - {goal['goalText']}")
                print(f"     Deadline: {goal['deadline']}")
        else:
            print("  No expired goals yet!")
        
        # Test due today goals
        print("\n9. Goals due today:")
        due_today = tracker.get_due_today_goals()
        if due_today:
            for goal in due_today:
                print(f"  {goal['goalTitle']}: {goal['goalText']}")
        else:
            print("  No goals due today!")
        
        print("\n=== Test Complete ===")
        
        # Clean up
        tracker.close_connection()
        print("MongoDB connection closed.")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        if tracker is not None:
            try:
                tracker.close_connection()
            except:
                pass


if __name__ == "__main__":
    main()
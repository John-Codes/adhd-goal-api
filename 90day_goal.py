import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

class Goal90:
    """A simple 90-day goal tracker with CRUD operations and persistence."""
    
    def __init__(self, storage_file: str = "goals_data.txt"):
        self.storage_file = storage_file
        self.goals: List[Dict[str, Any]] = []
        self.load_goals()
    
    def create(self, name: str, description: str) -> int:
        """Create a new 90-day goal with auto-assigned ID."""
        goal_data = {
            "id": len(self.goals),
            "name": name,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "is_active": True
        }
        
        self.goals.append(goal_data)
        self.save_goals()
        return goal_data["id"]
    
    def read(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """Read a goal and calculate remaining days."""
        if goal_id < 0 or goal_id >= len(self.goals):
            return None
        
        goal = self.goals[goal_id].copy()
        if not goal["is_active"]:
            return None
        
        created_date = datetime.fromisoformat(goal["created_date"])
        days_passed = (datetime.now() - created_date).days
        remaining_days = max(0, 90 - days_passed)
        
        goal["days_passed"] = days_passed
        goal["remaining_days"] = remaining_days
        goal["is_expired"] = remaining_days == 0
        
        return goal
    
    def update(self, goal_id: int, name: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
        """Update an existing goal."""
        if goal_id < 0 or goal_id >= len(self.goals):
            return False
        
        if name is not None:
            self.goals[goal_id]["name"] = name
        if description is not None:
            self.goals[goal_id]["description"] = description
        if is_active is not None:
            self.goals[goal_id]["is_active"] = is_active
        
        self.save_goals()
        return True
    
    def delete(self, goal_id: int) -> bool:
        """Delete a goal (soft delete)."""
        if goal_id < 0 or goal_id >= len(self.goals):
            return False
        
        self.goals[goal_id]["is_active"] = False
        self.save_goals()
        return True
    
    def list_goals(self) -> List[Dict[str, Any]]:
        """List all active goals with remaining days."""
        active_goals = []
        for goal in self.goals:
            if goal["is_active"]:
                goal_info = self.read(goal["id"])
                if goal_info:
                    active_goals.append(goal_info)
        return active_goals
    
    def save_goals(self):
        """Save goals to file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.goals, f, indent=2)
    
    def load_goals(self):
        """Load goals from file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    loaded_goals = json.load(f)
                    self.goals = loaded_goals
            except:
                self.goals = []
        else:
            self.goals = []
    
    def get_expired_goals(self) -> List[Dict[str, Any]]:
        """Get all expired goals (90+ days old)."""
        expired = []
        for goal in self.goals:
            if goal["is_active"]:
                goal_info = self.read(goal["id"])
                if goal_info and goal_info.get("is_expired", False):
                    expired.append(goal_info)
        return expired

def main():
    """Test the 90-day goal tracker."""
    print("=== 90-Day Goal Tracker ===\n")
    
    # Initialize tracker
    tracker = Goal90()
    
    # Test Create operations
    print("1. Creating goals...")
    goal1_id = tracker.create("Fitness", "Run 5k every day")
    goal2_id = tracker.create("Reading", "Read 1 book per week")
    goal3_id = tracker.create("Learning", "Learn Python in 90 days")
    print(f"Created goals with IDs: {goal1_id}, {goal2_id}, {goal3_id}")
    
    # Test Read operations
    print("\n2. Reading goals with remaining days:")
    for goal_id in [goal1_id, goal2_id, goal3_id]:
        goal = tracker.read(goal_id)
        if goal:
            print(f"Goal {goal['id']} - {goal['name']}: {goal['description']}")
            print(f"  Days passed: {goal['days_passed']}")
            print(f"  Remaining days: {goal['remaining_days']}")
            if goal['is_expired']:
                print("  ⚠️  EXPIRED!")
            print()
    
    # Test Update
    print("3. Updating goal 1...")
    tracker.update(goal1_id, name="Fitness Goal", description="Run 10k every day")
    updated_goal = tracker.read(goal1_id)
    if updated_goal:
        print(f"Updated: {updated_goal['name']} - {updated_goal['description']}")
    
    # Test List all goals
    print("\n4. All active goals:")
    all_goals = tracker.list_goals()
    for goal in all_goals:
        print(f"  {goal['id']}: {goal['name']} - {goal['description']} ({goal['remaining_days']} days left)")
    
    # Test expired goals
    print("\n5. Expired goals:")
    expired = tracker.get_expired_goals()
    if expired:
        for goal in expired:
            print(f"  {goal['id']}: {goal['name']} - {goal['description']}")
    else:
        print("  No expired goals yet!")
    
    # Test Delete
    print("\n6. Deleting goal 2...")
    success = tracker.delete(goal2_id)
    print(f"Delete successful: {success}")
    
    # Final list
    print("\n7. Final goal list:")
    final_goals = tracker.list_goals()
    for goal in final_goals:
        print(f"  {goal['id']}: {goal['name']} - {goal['description']} ({goal['remaining_days']} days left)")
    
    print("\n=== Test Complete ===")
    print(f"Goals saved to: {tracker.storage_file}")

if __name__ == "__main__":
    main()
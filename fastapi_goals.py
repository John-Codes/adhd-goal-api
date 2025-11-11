from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from goals import GoalMonth

app = FastAPI(title="Goals CRUD API", description="Simple CRUD API for goals")

# Initialize goal tracker
monthly_tracker = GoalMonth()

# Pydantic models for request/response
class GoalCreate(BaseModel):
    name: str
    description: str
    due_date: Optional[str] = None

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    is_active: Optional[bool] = None

# CRUD Goals Endpoints
@app.post("/api/crud-goals", response_model=dict)
def create_goal(goal: GoalCreate):
    """Create a new goal"""
    goal_id = monthly_tracker.create(
        goal_title=goal.name,
        goal_text=goal.description,
        deadline_days=30
    )
    created_goal = monthly_tracker.read(goal_id)
    if created_goal:
        return {"message": "Goal created successfully", "goal": created_goal}
    else:
        raise HTTPException(status_code=500, detail="Failed to create goal")

@app.get("/api/crud-goals/expired")
def get_expired_goals():
    """Get all expired goals"""
    return monthly_tracker.get_expired_goals()

@app.get("/api/crud-goals/{goal_id}", response_model=dict)
def get_goal(goal_id: str):
    """Get a specific goal"""
    goal = monthly_tracker.read(goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.get("/api/crud-goals", response_model=List[dict])
def list_goals():
    """List all active goals"""
    return monthly_tracker.list_goals()

@app.put("/api/crud-goals/{goal_id}", response_model=dict)
def update_goal(goal_id: str, goal: GoalUpdate):
    """Update a goal"""
    success = monthly_tracker.update(
        goal_id,
        goal_title=goal.name,
        goal_text=goal.description,
        deadline=goal.due_date
    )
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    updated_goal = monthly_tracker.read(goal_id)
    return {"message": "Goal updated successfully", "goal": updated_goal}

@app.delete("/api/crud-goals/{goal_id}", response_model=dict)
def delete_goal(goal_id: str):
    """Delete a goal (soft delete)"""
    success = monthly_tracker.delete(goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted successfully"}

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "goals_count": len(monthly_tracker.list_goals())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_goals:app", host="0.0.0.0", port=8000, reload=True)
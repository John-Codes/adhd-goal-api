from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from QuarterGoals import Goal90
from monthly_goals import GoalMonth
from LLM import LLMClient

app = FastAPI(title="Goals API", description="Simple CRUD API for 90-day and monthly goals")

# Initialize goal trackers
goal90_tracker = Goal90()
monthly_tracker = GoalMonth()

# Initialize LLM client
llm_client = LLMClient()

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

# LLM Chat Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class LLMChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[ChatMessage]] = []

# 90-Day Goals Endpoints
@app.post("/api/90day-goals", response_model=dict)
def create_90day_goal(goal: GoalCreate):
    """Create a new 90-day goal"""
    goal_id = goal90_tracker.create(goal.name, goal.description)
    created_goal = goal90_tracker.read(goal_id)
    if created_goal:
        return {"message": "90-day goal created successfully", "goal": created_goal}
    else:
        raise HTTPException(status_code=500, detail="Failed to create goal")

@app.get("/api/90day-goals/expired")
def get_expired_90day_goals():
    """Get all expired 90-day goals"""
    return goal90_tracker.get_expired_goals()

@app.get("/api/90day-goals/{goal_id}", response_model=dict)
def get_90day_goal(goal_id: int):
    """Get a specific 90-day goal"""
    goal = goal90_tracker.read(goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.get("/api/90day-goals", response_model=List[dict])
def list_90day_goals():
    """List all active 90-day goals"""
    return goal90_tracker.list_goals()

@app.put("/api/90day-goals/{goal_id}", response_model=dict)
def update_90day_goal(goal_id: int, goal: GoalUpdate):
    """Update a 90-day goal"""
    success = goal90_tracker.update(
        goal_id,
        name=goal.name,
        description=goal.description,
        is_active=goal.is_active
    )
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    updated_goal = goal90_tracker.read(goal_id)
    return {"message": "90-day goal updated successfully", "goal": updated_goal}

@app.delete("/api/90day-goals/{goal_id}", response_model=dict)
def delete_90day_goal(goal_id: int):
    """Delete a 90-day goal (soft delete)"""
    success = goal90_tracker.delete(goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "90-day goal deleted successfully"}

# Monthly Goals Endpoints
@app.post("/api/monthly-goals", response_model=dict)
def create_monthly_goal(goal: GoalCreate):
    """Create a new monthly goal"""
    goal_id = monthly_tracker.create(goal.name, goal.description, goal.due_date)
    created_goal = monthly_tracker.read(goal_id)
    if created_goal:
        return {"message": "Monthly goal created successfully", "goal": created_goal}
    else:
        raise HTTPException(status_code=500, detail="Failed to create goal")

@app.get("/api/monthly-goals/expired")
def get_expired_monthly_goals():
    """Get all expired monthly goals"""
    return monthly_tracker.get_expired_goals()

@app.get("/api/monthly-goals/{goal_id}", response_model=dict)
def get_monthly_goal(goal_id: int):
    """Get a specific monthly goal"""
    goal = monthly_tracker.read(goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.get("/api/monthly-goals", response_model=List[dict])
def list_monthly_goals():
    """List all active monthly goals"""
    return monthly_tracker.list_goals()

@app.put("/api/monthly-goals/{goal_id}", response_model=dict)
def update_monthly_goal(goal_id: int, goal: GoalUpdate):
    """Update a monthly goal"""
    success = monthly_tracker.update(
        goal_id,
        name=goal.name,
        description=goal.description,
        due_date=goal.due_date,
        is_active=goal.is_active
    )
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    updated_goal = monthly_tracker.read(goal_id)
    return {"message": "Monthly goal updated successfully", "goal": updated_goal}

@app.delete("/api/monthly-goals/{goal_id}", response_model=dict)
def delete_monthly_goal(goal_id: int):
    """Delete a monthly goal (soft delete)"""
    success = monthly_tracker.delete(goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Monthly goal deleted successfully"}

# File Download Endpoints
@app.get("/api/download/90day-data")
def download_90day_data():
    """Download 90-day goals data file"""
    if not os.path.exists(goal90_tracker.storage_file):
        raise HTTPException(status_code=404, detail="Data file not found")
    return FileResponse(
        path=goal90_tracker.storage_file,
        filename="90day_goals_data.txt",
        media_type="text/plain"
    )

@app.get("/api/download/monthly-data")
def download_monthly_data():
    """Download monthly goals data file"""
    if not os.path.exists(monthly_tracker.storage_file):
        raise HTTPException(status_code=404, detail="Data file not found")
    return FileResponse(
        path=monthly_tracker.storage_file,
        filename="monthly_goals_data.txt",
        media_type="text/plain"
    )

# LLM Chat Endpoint
@app.post("/api/llmquerygoals", response_model=dict)
def llm_query_goals(request: LLMChatRequest):
    """Chat with LLM about goals using both 90-day and monthly goals data"""
    try:
        # Read goals data
        with open(goal90_tracker.storage_file, 'r') as f:
            goals_90day = json.load(f)
        
        with open(monthly_tracker.storage_file, 'r') as f:
            monthly_goals = json.load(f)
        
# Build context from goals
        chat_history_str = ""
        if request.chat_history:
            chat_history_str = f"Chat History:\n{json.dumps([{"role": msg.role, "content": msg.content} for msg in request.chat_history], indent=2)}\n"
        
        context = f"""
        You are a no-nonsense coach for someone with ADHD. 
        Your job: keep their life laser-focused. 
        Every time they try to add a goal-monthly or daily-first check: Does this move the needle on their 90-day (quarter) goals? 
        If not, don't let it in. Say something like, Hold up-that's splitting you too thin. 
        Your quarter goal is X; this doesn't fit. Want to drop it or reframe it to help X? 
        If they insist, let them park it in a 'later' list, but nag: 
        Remember, focus wins. When they ask for summaries, say what they're ignoring, what they're crushing, and end with: 
        Pick one thing this week-don't wander. Keep it short, direct, loving-but-firm. Include the KISS principle (Keep It Simple, Stupid). And always tie back to their quarter goals. With some famous entrepreneurs advice sprinkled in. 
Here are your current goals:


90-Day Goals:
{json.dumps([g for g in goals_90day if g.get('is_active', True)], indent=2)}

Monthly Goals:
{json.dumps([g for g in monthly_goals if g.get('is_active', True)], indent=2)}

{chat_history_str}
"""
        
        # Combine context with user message
        prompt = f"{context}\n\nUser: {request.message}\n\nAssistant:"
        
        # Call LLM
        response = llm_client.call_llm(prompt)
        
        return {
            "message": "LLM response generated successfully",
            "response": response,
            "goals_context": "Included 90-day and monthly goals in context"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating LLM response: {str(e)}")

# Health check endpoint
@app.get("/api/health")
def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "90day_goals_count": len(goal90_tracker.list_goals()),
        "monthly_goals_count": len(monthly_tracker.list_goals())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
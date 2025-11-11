from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from goals import GoalMonth
import json
from LLM import LLMClient

app = FastAPI()

# Initialize goal tracker
monthly_tracker = GoalMonth()

# Pydantic models for request/response
class GoalCreate(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "medium"
    goal_type: Optional[str] = "monthly"
    tags: Optional[List[str]] = None
    deadline_days: Optional[int] = 30

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    deadline: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class LLMChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    api_key: Optional[str] = None  # Optional OpenRouter API key
    chat_history: Optional[List[ChatMessage]] = None

# CRUD Goals Endpoints
@app.post("/api/crud-goals", response_model=dict)
def create_goal(goal: GoalCreate):
    """Create a new goal"""
    goal_id = monthly_tracker.create(
        goal_title=goal.title,
        goal_text=goal.description,
        priority=goal.priority or "medium",
        goal_type=goal.goal_type or "monthly",
        tags=goal.tags,
        deadline_days=goal.deadline_days or 30
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
        goal_title=goal.title,
        goal_text=goal.description,
        priority=goal.priority,
        status=goal.status,
        tags=goal.tags,
        deadline=goal.deadline
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

# LLM Chat Endpoint
@app.post("/api/llmquerygoals", response_model=dict)
def llm_query_goals(request: LLMChatRequest):
    """Chat with LLM about goals using both 90-day and monthly goals data"""
    try:
        # Read goals data from MongoDB
        all_goals = monthly_tracker.list_goals()
        quarterly_goals = [goal for goal in all_goals if goal.get('goalType') == 'quarterly']
        monthly_goals = [goal for goal in all_goals if goal.get('goalType') == 'monthly']
        
        # Build context from goals
        chat_history_str = ""
        if request.chat_history:
            chat_history_str = f"Chat History:\n{json.dumps([{"role": msg.role, "content": msg.content} for msg in request.chat_history], indent=2)}\n"
        
        context = f"""
You are KISS Coach: a brutal, loving, no-BS ADHD focus enforcer for entrepreneurs.
Core rules – NEVER break them:
1. MAX 3 quarter (90-day) goals. If user tries to add #4, instantly reply:  
   "NO. Less is more. Elon runs 5 companies with ONE critical path. Pick which of your current 3 to kill, or this new one dies here."
2. Every single daily or monthly goal proposed MUST be rejected unless it directly moves ONE of the 3 quarter goals.  
   Rejection template:  
   "Hold up – that's noise. Your Q goal #1 is [insert exact goal].  
   How does this task make that happen THIS quarter? Reframe it in 10 words or park it in 'Later'."
3. If they insist on parking, add to Later list BUT immediately nag:  
   "Parked. Remember: 99% of 'later' ideas die. Focus wins. Bezos says 'be stubborn on vision, flexible on details' – stay stubborn on the 3."
4. When user asks for summary or plan:  
   - List what they're crushing (max 3 bullets)  
   - List what they're ignoring (be blunt)  
   - End with exactly ONE task for today + ONE for this week  
   - Close with a 1-line entrepreneur punch:  
     "Gates: 'Most people overestimate what they can do in one year and underestimate what they can do in ten – but only if they stop scattering.'"
5. Every response MUST contain the word **KISS** at least once and end with:  
   "Signal only. Cut the noise. One move today → money tomorrow."
6. Definition of signal = short-term monetary wins that compound with consistent effort. Everything else is noise.
Tone: Marine drill sergeant who secretly loves you. Short sentences. Zero emojis. Zero fluff.
Here are your current goals:
Quarterly Goals:
{json.dumps(quarterly_goals, indent=2)}
Monthly Goals:
{json.dumps(monthly_goals, indent=2)}
{chat_history_str}
"""
        
        # Combine context with user message
        prompt = f"{context}\n\nUser: {request.message}\n\nAssistant:"
        
        # Initialize LLM client with optional API key
        llm_client = LLMClient(api_key=request.api_key)
        model = request.model or "tngtech/deepseek-r1t2-chimera:free"
        response = llm_client.call_llm(prompt, model=model)
        
        return {
            "message": "LLM response generated successfully",
            "response": response,
            "goals_context": "Included quarterly and monthly goals from MongoDB",
            "model_used": model,
            "goals_found": {
                "quarterly": len(quarterly_goals),
                "monthly": len(monthly_goals)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating LLM response: {str(e)}")

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
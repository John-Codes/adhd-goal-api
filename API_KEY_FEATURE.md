# Optional API Key Support for LLM Endpoint

## Overview

The LLM chat endpoint (`/api/llmquerygoals`) now supports optional API key authentication, providing flexibility for different usage scenarios.

## Key Features

### 1. Optional API Key Parameter

The `LLMChatRequest` model now includes an optional `api_key` field:

```python
class LLMChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    api_key: Optional[str] = None  # NEW: Optional OpenRouter API key
    chat_history: Optional[List[ChatMessage]] = None
```

### 2. Flexible Authentication

The LLM client now supports three authentication scenarios:

#### A. Environment Variable (Default)
```python
# Set in environment
export OPENROUTER_API_KEY="your-openrouter-key"

# Client uses environment variable automatically
client = LLMClient()  # Uses env var
```

#### B. Explicit API Key
```python
# Pass API key directly to client
client = LLMClient(api_key="your-openrouter-key")
```

#### C. Override Environment Variable
```python
# Set environment variable
export OPENROUTER_API_KEY="env-key"

# Override with explicit key
client = LLMClient(api_key="explicit-key")  # Uses explicit key, not env var
```

## API Usage

### Request Format

```json
POST /api/llmquerygoals
{
  "message": "Help me prioritize my goals for this week",
  "model": "tngtech/deepseek-r1t2-chimera:free",  // Optional, defaults to model above
  "api_key": "your-openrouter-api-key",           // Optional, falls back to env var
  "chat_history": [                               // Optional
    {
      "role": "user",
      "content": "I have 5 goals to complete"
    },
    {
      "role": "assistant", 
      "content": "Which 3 are most critical?"
    }
  ]
}
```

### Response Format

```json
{
  "message": "LLM response generated successfully",
  "response": "KISS Coach: Focus on your 3 most critical goals...",
  "goals_context": "Included quarterly and monthly goals from MongoDB",
  "model_used": "tngtech/deepseek-r1t2-chimera:free",
  "goals_found": {
    "quarterly": 2,
    "monthly": 5
  }
}
```

## Implementation Details

### LLMClient Changes

```python
class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client with optional API key.
        
        Args:
            api_key: Optional API key. If not provided, will use OPENROUTER_API_KEY from environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided and OPENROUTER_API_KEY not found in environment variables")
        
        # Initialize OpenAI client with API key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
```

### FastAPI Endpoint Changes

```python
@app.post("/api/llmquerygoals", response_model=dict)
def llm_query_goals(request: LLMChatRequest):
    """Chat with LLM about goals using both 90-day and monthly goals data"""
    try:
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
```

## Error Handling

### Missing API Key
```json
{
  "detail": "OpenRouter API key not provided and OPENROUTER_API_KEY not found in environment variables"
}
```

### Invalid API Key
```json
{
  "detail": "Error generating LLM response: Incorrect API key provided"
}
```

## Security Considerations

1. **Environment Variables**: When possible, use environment variables instead of passing API keys in requests
2. **Request Logging**: Be aware that API keys in requests may be logged by monitoring systems
3. **Key Rotation**: Implement proper key rotation practices in production
4. **Access Control**: Consider implementing user-specific API key validation in production

## Testing

Run the unit tests to verify the implementation:

```bash
# Unit tests for LLM functionality
python test_llm_simple.py

# Integration tests (requires running API server)
python test_llm_endpoint.py
```

## Migration Guide

### For Existing Users

No changes required! The API is backward compatible:

- If you currently use environment variables, nothing changes
- If you want to use per-request API keys, you can now pass them
- All existing requests continue to work as before

### For New Implementations

Choose the authentication method that best fits your use case:

1. **Multi-user SaaS**: Use per-request API keys for user-specific billing
2. **Single-instance deployment**: Use environment variables
3. **Testing/Development**: Use explicit API keys in test code

## Examples

### JavaScript/Node.js
```javascript
const response = await fetch('/api/llmquerygoals', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "Help me with my goals",
    api_key: "your-openrouter-key",  // Optional
    model: "tngtech/deepseek-r1t2-chimera:free"
  })
});
```

### Python
```python
import requests

response = requests.post('/api/llmquerygoals', json={
    "message": "Help me prioritize my goals",
    "api_key": "your-openrouter-key",  # Optional
    "model": "tngtech/deepseek-r1t2-chimera:free"
})

result = response.json()
print(result['response'])
```

### cURL
```bash
curl -X POST http://localhost:8000/api/llmquerygoals \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with my goals",
    "api_key": "your-openrouter-key",
    "model": "tngtech/deepseek-r1t2-chimera:free"
  }'
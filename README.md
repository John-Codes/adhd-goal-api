# Goals API - FastAPI Implementation with AI Coach

A powerful FastAPI application providing CRUD operations for goals with integrated AI coaching. Designed specifically for people with ADHD to stay focused on their most important objectives using the KISS (Keep It Simple, Stupid) methodology. Features JWT authentication, MongoDB storage, and AI-powered goal coaching through LLM integration.

## Features

✅ **Unified Goals CRUD System**
- Create, read, update, delete goals with JWT authentication
- Track quarterly (90-day) and monthly goals
- Automatic deadline calculations and expiration detection
- Soft delete functionality
- Retrieve expired goals

✅ **AI-Powered Goal Coaching**
- LLM integration with OpenRouter API
- Context-aware conversations about your goals
- ADHD-focused coaching using KISS methodology
- Chat history support for continuous conversations
- Optional API key support

✅ **JWT Authentication & Security**
- Secure token-based authentication
- Protected endpoints with proper authorization
- Test user support for development

✅ **MongoDB Integration**
- Persistent data storage
- Scalable database backend
- Automatic goal expiration tracking

✅ **Docker Support**
- Production-ready containerization
- Minimal dependencies for efficient deployment

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the server:**
   ```bash
   python run_api.py
   ```
   or
   ```bash
   uvicorn fastapi_goals:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t goals-api:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 8000:8000 --name goals-api goals-api:latest
   ```

3. **Test the deployment:**
   ```bash
   bash test_api.sh
   ```

## API Endpoints

### Authentication
All CRUD and LLM endpoints require JWT authentication except the health check.

### Goals CRUD
- `GET /api/health` - Health check (public)
- `GET /api/crud-goals` - List all goals (authenticated)
- `POST /api/crud-goals` - Create a new goal (authenticated)
- `GET /api/crud-goals/{goal_id}` - Get specific goal (authenticated)
- `PUT /api/crud-goals/{goal_id}` - Update goal (authenticated)
- `DELETE /api/crud-goals/{goal_id}` - Delete goal (authenticated)
- `GET /api/crud-goals/expired` - Get expired goals (authenticated)

### AI Coach
- `POST /api/llmquerygoals` - Chat with AI coach about goals (authenticated)

## Testing

### Comprehensive E2E Tests
```bash
# Test with authentication (JWT required)
python test_e2e_auth.py

# Test security (should show 403 for unauthenticated requests)
python test_e2e.py

# Quick API tests
bash test_api.sh
```

## Example Usage

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Create a Goal (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/crud-goals" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "title": "Launch MVP",
       "description": "Complete and launch the first version of my app",
       "priority": "high",
       "goal_type": "quarterly",
       "tags": ["product", "launch", "mvp"],
       "deadline_days": 90
     }'
```

### List All Goals (Authenticated)
```bash
curl -X GET "http://localhost:8000/api/crud-goals" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Chat with AI Coach (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/llmquerygoals" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "message": "Help me prioritize my goals for this week",
       "model": "tngtech/deepseek-r1t2-chimera:free"
     }'
```

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Test Token
For testing purposes, use the JWT token provided in the test files. In production, implement proper user registration and authentication.

## Environment Variables

Required environment variables:
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `MONGODB_URI` - MongoDB connection string
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM integration

## Data Storage

The API uses MongoDB for persistent data storage:
- **Collection**: `goals`
- **Automatic fields**: `_id`, `createdAt`, `updatedAt`, `days_remaining`, `is_expired`
- **Goal types**: Supports both quarterly and monthly goals
- **User isolation**: Goals are associated with user IDs

## KISS Coach AI

The AI coach follows the KISS (Keep It Simple, Stupid) methodology:
- **Maximum 3 quarterly goals**: Prevents goal sprawl
- **Monthly goals must support quarterly goals**: Ensures alignment
- **Focus on monetary wins**: Prioritizes revenue-generating activities
- **Brutal honesty**: Marine drill sergeant approach with caring intent
- **One task per day**: Daily actionable steps

Example AI coach response:
```
Hold up – that's noise. Your Q goal #1 is [goal].  
How does this task make that happen THIS quarter? 
Reframe it in 10 words or park it in 'Later'.
```

## Documentation

Once the server is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Health Monitoring

Monitor API health:
```bash
curl http://localhost:8000/api/health
```

Response includes:
```json
{
  "status": "healthy",
  "goals_count": 5
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors (403)**: Ensure JWT token is included in requests
2. **MongoDB Connection**: Verify `MONGODB_URI` environment variable
3. **LLM Errors**: Check `OPENROUTER_API_KEY` is set and valid
4. **Port Conflicts**: Ensure port 8000 is available

### Logs
Check application logs for detailed error information.

## Development

### Project Structure
```
├── fastapi_goals.py     # Main FastAPI application
├── goals.py            # Goal management logic
├── mongodb_handler.py  # MongoDB connection handler
├── LLM.py             # LLM client integration
├── run_api.py         # Server startup script
├── requirements.txt   # Python dependencies
├── requirements_minimal.txt  # Minimal Docker dependencies
├── Dockerfile         # Docker configuration
├── test_e2e.py       # Comprehensive tests
├── test_e2e_auth.py  # Authentication tests
└── test_api.sh       # Quick API tests
```

### Adding New Features
1. Add new endpoints in `fastapi_goals.py`
2. Update Pydantic models for request/response
3. Add corresponding tests
4. Update documentation

## License

This project is designed to help people with ADHD stay focused and achieve their goals through structured, AI-assisted goal management.
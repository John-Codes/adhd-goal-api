# Goals API - FastAPI Implementation

A simple FastAPI application providing CRUD operations for 90-day and monthly goals. Helps people with ADHD and autism stay on top of theyre life following the advice of the most succesful people in the world.Can be used while driving using STT TTS LLM endpoints.

## Features

✅ **90-Day Goals CRUD**
- Create 90-day goals
- Read individual goals with remaining days calculation
- List all active goals
- Update goal details
- Soft delete goals
- Get expired goals (90+ days old)

✅ **Monthly Goals CRUD**
- Create monthly goals with due dates
- Read individual goals with remaining days
- List all active goals
- Update goal details and due dates
- Soft delete goals
- Get expired goals (30+ days old)

✅ **File Download**
- Download 90-day goals data as JSON file
- Download monthly goals data as JSON file

✅ **Health Check**
- API health monitoring endpoint

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python run_api.py
```
or
```bash
uvicorn fastapi_goals:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### 90-Day Goals
- `POST /api/90day-goals` - Create a new 90-day goal
- `GET /api/90day-goals/{goal_id}` - Get a specific goal
- `GET /api/90day-goals` - List all active goals
- `PUT /api/90day-goals/{goal_id}` - Update a goal
- `DELETE /api/90day-goals/{goal_id}` - Delete a goal (soft delete)
- `GET /api/90day-goals/expired` - Get expired goals

### Monthly Goals
- `POST /api/monthly-goals` - Create a new monthly goal
- `GET /api/monthly-goals/{goal_id}` - Get a specific goal
- `GET /api/monthly-goals` - List all active goals
- `PUT /api/monthly-goals/{goal_id}` - Update a goal
- `DELETE /api/monthly-goals/{goal_id}` - Delete a goal (soft delete)
- `GET /api/monthly-goals/expired` - Get expired goals

### File Downloads
- `GET /api/download/90day-data` - Download 90-day goals data
- `GET /api/download/monthly-data` - Download monthly goals data

### Health
- `GET /api/health` - Health check

## Testing

Run the end-to-end test:
```bash
python test_goals_api.py
```

## Example Usage

### Create a 90-day goal
```bash
curl -X POST "http://localhost:8000/api/90day-goals" \
     -H "Content-Type: application/json" \
     -d '{"name": "Fitness Goal", "description": "Run 5k every day"}'
```

### List all 90-day goals
```bash
curl -X GET "http://localhost:8000/api/90day-goals"
```

### Create a monthly goal
```bash
curl -X POST "http://localhost:8000/api/monthly-goals" \
     -H "Content-Type: application/json" \
     -d '{"name": "Reading Goal", "description": "Read 2 books", "due_date": "2025-12-15"}'
```

## Data Storage

The API uses the same file-based storage as the original goal trackers:
- `goals_data.txt` - 90-day goals data
- `monthly_goals_data.txt` - Monthly goals data

## Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
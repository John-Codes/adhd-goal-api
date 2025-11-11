# Use Python 3.11 slim image - lightweight and fast
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only essential requirements first
COPY requirements_minimal.txt requirements.txt

# Install minimal dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY fastapi_goals.py .
COPY QuarterGoals.py .
COPY monthly_goals.py .
COPY LLM.py .
COPY goals_data.txt .
COPY monthly_goals_data.txt .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "fastapi_goals:app", "--host", "0.0.0.0", "--port", "8000"]
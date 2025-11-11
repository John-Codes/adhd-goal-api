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
COPY goals.py .
COPY LLM.py .
COPY mongodb_handler.py .
COPY run_api.py .
COPY .env .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "run_api.py"]
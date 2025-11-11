# Quick Docker Deployment Guide

## Build and Run
```bash
# Build the image
docker build -t goals-api:latest .

# Run the container
docker run -d -p 8000:8000 --name goals-api goals-api:latest
```

## Test the API
```bash
# Health check
curl http://localhost:8000/api/health

# API docs
open http://localhost:8000/docs
```

## Stop/Remove
```bash
docker stop goals-api
docker rm goals-api
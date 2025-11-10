#!/usr/bin/env python3
"""
Simple script to start the Goals API server
"""

import uvicorn
from fastapi_goals import app

if __name__ == "__main__":
    print("🚀 Starting Goals API server...")
    print("📖 API documentation will be available at: http://localhost:8000/docs")
    print("🔍 ReDoc documentation at: http://localhost:8000/redoc")
    print("❤️  Health check at: http://localhost:8000/api/health")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
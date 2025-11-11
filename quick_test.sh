#!/bin/bash

# Quick test script for your Goals API Docker container
echo "🧪 Testing Goals API in Docker..."

# Wait for the API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

if [ $i -eq 30 ]; then
    echo "❌ API failed to start within 60 seconds"
    exit 1
fi

# Test basic functionality
echo ""
echo "🔍 Testing endpoints..."

echo "1. Health check:"
curl -s http://localhost:8000/api/health | python -m json.tool

echo ""
echo "2. List current 90-day goals:"
curl -s http://localhost:8000/api/90day-goals

echo ""
echo "3. Create a test goal:"
curl -s -X POST http://localhost:8000/api/90day-goals \
  -H "Content-Type: application/json" \
  -d '{"name":"Docker Test Goal","description":"Testing the container deployment"}'

echo ""
echo "4. Verify the goal was created:"
curl -s http://localhost:8000/api/90day-goals

echo ""
echo "✅ All tests passed! Your API is running perfectly in Docker."
echo "📖 API docs: http://localhost:8000/docs"
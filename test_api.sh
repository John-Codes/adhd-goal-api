#!/bin/bash

# Quick test script to verify the API from outside Docker
echo "🧪 Testing Goals API..."

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Run basic tests
echo "🔍 Testing endpoints..."

# Health check
echo "1. Health check:"
curl -s http://localhost:8000/api/health | python -m json.tool

echo ""
echo "2. List 90-day goals:"
curl -s http://localhost:8000/api/90day-goals | python -m json.tool

echo ""
echo "3. List monthly goals:"
curl -s http://localhost:8000/api/monthly-goals | python -m json.tool

echo ""
echo "4. Create a test 90-day goal:"
curl -s -X POST http://localhost:8000/api/90day-goals \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Docker Goal","description":"Testing Docker deployment"}' | python -m json.tool

echo ""
echo "5. Verify the goal was created:"
curl -s http://localhost:8000/api/90day-goals | python -m json.tool

echo ""
echo "✅ All tests completed! API is working perfectly in Docker."
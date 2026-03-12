#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"
COURSE_ID="05859ba1-10a2-41b9-b341-c06de064b72c"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================"
echo "Test: Auto-Complete Lesson"
echo "======================================"
echo

# 1. Login
echo -e "${YELLOW}1. Login...${NC}"
curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c /tmp/test_complete.txt > /dev/null
echo "✓ Logged in"
echo

# 2. Get a lesson that is not completed (Decision Making)
LESSON_ID="028bd4df-61ee-43b0-aae3-15e0fee07114"

echo -e "${YELLOW}2. Check current lesson status...${NC}"
curl -s -b /tmp/test_complete.txt "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}" | python3 << 'EOF'
import json, sys

lesson = json.load(sys.stdin)
print(f"Lesson: {lesson['title']}")

if lesson['progress']:
    prog = lesson['progress']
    print(f"Current status: {prog['status']}")
    print(f"Current progress: {prog['progress_percent']}%")
    print(f"Completed at: {prog['completed_at']}")
    print(f"Last activity: {prog['last_activity_at']}")
else:
    print("Progress: null (not started)")
EOF
echo

# 3. Update progress to 50%
echo -e "${YELLOW}3. Update progress to 50% (in_progress)...${NC}"
curl -s -X PUT "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}/progress" \
  -H "Content-Type: application/json" \
  -b /tmp/test_complete.txt \
  -d '{
    "progress_percent": 50.0,
    "time_spent_seconds": 600,
    "status": "in_progress"
  }' | python3 << 'EOF'
import json, sys

data = json.load(sys.stdin)
print(f"Updated: {data['status']} - {data['progress_percent']}%")
print(f"Time spent: {data['time_spent_seconds']}s")
EOF
echo

# 4. Check lesson detail
echo -e "${YELLOW}4. Check lesson detail after 50% update...${NC}"
curl -s -b /tmp/test_complete.txt "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}" | python3 << 'EOF'
import json, sys

lesson = json.load(sys.stdin)
prog = lesson['progress']
print(f"Status: {prog['status']}")
print(f"Progress: {prog['progress_percent']}%")
print(f"Time spent: {prog['time_spent_seconds']}s")
print(f"Completed at: {prog['completed_at']}")
print(f"Last activity: {prog['last_activity_at']}")
EOF
echo

# 5. Update progress to 100%
echo -e "${YELLOW}5. Update progress to 100% (should auto-mark as completed)...${NC}"
curl -s -X PUT "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}/progress" \
  -H "Content-Type: application/json" \
  -b /tmp/test_complete.txt \
  -d '{
    "progress_percent": 100.0,
    "time_spent_seconds": 1200,
    "status": "in_progress"
  }' | python3 << 'EOF'
import json, sys

data = json.load(sys.stdin)
print(f"Updated: {data['status']} - {data['progress_percent']}%")
print(f"Time spent: {data['time_spent_seconds']}s")
EOF
echo

# 6. Check lesson detail with completed_at
echo -e "${YELLOW}6. Check lesson detail (should have completed_at now)...${NC}"
curl -s -b /tmp/test_complete.txt "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}" | python3 << 'EOF'
import json, sys

lesson = json.load(sys.stdin)
prog = lesson['progress']

print(f"✅ Status: {prog['status']}")
print(f"✅ Progress: {prog['progress_percent']}%")
print(f"✅ Time spent: {prog['time_spent_seconds']}s")
print(f"✅ Completed at: {prog['completed_at']}")
print(f"✅ Last activity: {prog['last_activity_at']}")

if prog['completed_at']:
    print()
    print("🎉 SUCCESS: completed_at is set!")
else:
    print()
    print("❌ FAILED: completed_at is still null")
EOF
echo

echo
echo -e "${GREEN}======================================"
echo "Test Complete!"
echo "======================================${NC}"

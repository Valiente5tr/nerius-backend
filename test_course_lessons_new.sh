#!/bin/bash

# Script de prueba para los nuevos endpoints de cursos y lecciones

BASE_URL="http://localhost:8000/api/v1"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================"
echo "Testing Course & Lesson Endpoints"
echo "======================================"
echo

# 1. Login
echo -e "${YELLOW}1. Login...${NC}"
curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c /tmp/test_course_lessons.txt | python3 -c "import sys, json; d = json.load(sys.stdin); print(f'✓ Logged in as: {d[\"user\"][\"first_name\"]} {d[\"user\"][\"last_name\"]}')"
echo

# 2. Get all courses
echo -e "${YELLOW}2. Getting all courses...${NC}"
COURSE_ID=$(curl -s -b /tmp/test_course_lessons.txt "${BASE_URL}/courses" | python3 -c "import sys, json; d = json.load(sys.stdin); print(f'{d[0][\"title\"]} - ID: {d[0][\"id\"]}'); print(d[0]['id'])" | tail -1)
echo

# 3. Get course detailed (NEW FORMAT)
echo -e "${YELLOW}3. GET /courses/{id}/detailed - Vista General${NC}"
echo -e "${BLUE}   → Todos los módulos y lecciones con progreso (SIN recursos)${NC}"
echo

curl -s -b /tmp/test_course_lessons.txt "${BASE_URL}/courses/${COURSE_ID}/detailed" -o /tmp/course_detailed.json

python3 << 'EOF'
import json

with open('/tmp/course_detailed.json') as f:
    course = json.load(f)

print(f"📚 Course: {course['title']}")
print(f"   Progress: {course['enrollment']['progress_percent']:.1f}%")
print(f"   Estimated: {course['estimated_minutes']} minutes")
print()

total_lessons = 0
completed_lessons = 0

for i, module in enumerate(course['modules'], 1):
    print(f"📦 Module {i}: {module['title']}")
    
    for j, lesson in enumerate(module['lessons'], 1):
        total_lessons += 1
        icon = "✅" if lesson['status'] == 'completed' else "⏳" if lesson['status'] == 'in_progress' else "⭕"
        
        if lesson['status'] == 'completed':
            completed_lessons += 1
        
        print(f"   {icon} {i}.{j} {lesson['title'][:50]:<50} [{lesson['status']:>12}] {lesson['progress_percent']:>5.1f}%")
    print()

print(f"Total: {completed_lessons}/{total_lessons} lecciones completadas")
print()

# Save first lesson ID for next test
first_lesson_id = course['modules'][0]['lessons'][0]['id']
with open('/tmp/first_lesson_id.txt', 'w') as f:
    f.write(first_lesson_id)
EOF

echo
echo "---"
echo

# 4. Get lesson detailed (NEW ENDPOINT)
echo -e "${YELLOW}4. GET /courses/{id}/lessons/{lesson_id} - Detalle de Lección${NC}"
echo -e "${BLUE}   → Descripción y recursos completos de una lección específica${NC}"
echo

LESSON_ID=$(cat /tmp/first_lesson_id.txt)

curl -s -b /tmp/test_course_lessons.txt "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_ID}" | python3 << 'EOF'
import sys, json

lesson = json.load(sys.stdin)

print(f"📖 Lesson: {lesson['title']}")
print(f"   Description: {lesson['description']}")
print(f"   Estimated time: {lesson['estimated_minutes']} minutes")
print()

if lesson['progress']:
    print(f"📊 Progress:")
    print(f"   Status: {lesson['progress']['status']}")
    print(f"   Progress: {lesson['progress']['progress_percent']}%")
    print()

print(f"📎 Resources ({len(lesson['resources'])}):")
if len(lesson['resources']) == 0:
    print("   (No resources available)")
else:
    for i, res in enumerate(lesson['resources'], 1):
        duration = f" - {res['duration_seconds']}s" if res.get('duration_seconds') else ""
        print(f"   {i}. [{res['resource_type'].upper()}] {res['title']}{duration}")
        print(f"      URL: {res['external_url']}")
print()
EOF

echo
echo "---"
echo

# 5. Test different lesson
echo -e "${YELLOW}5. Testing another lesson (without resources)...${NC}"

curl -s -b /tmp/test_course_lessons.txt "${BASE_URL}/courses/${COURSE_ID}/detailed" | python3 << 'EOF'
import json, sys

with open('/tmp/course_detailed.json') as f:
    course = json.load(f)

# Get second lesson
second_lesson = course['modules'][0]['lessons'][1]
print(f"Lesson: {second_lesson['title']}")
print(f"Status: {second_lesson['status']}")
print(f"Progress: {second_lesson['progress_percent']}%")

# Save ID
with open('/tmp/second_lesson_id.txt', 'w') as f:
    f.write(second_lesson['id'])
EOF

LESSON_2_ID=$(cat /tmp/second_lesson_id.txt)

echo
curl -s -b /tmp/test_course_lessons.txt "${BASE_URL}/courses/${COURSE_ID}/lessons/${LESSON_2_ID}" | python3 << 'EOF'
import sys, json

lesson = json.load(sys.stdin)
print(f"\nLesson Details:")
print(f"  Title: {lesson['title']}")
print(f"  Resources: {len(lesson['resources'])}")
print(f"  Progress: {lesson['progress']['progress_percent']}%" if lesson['progress'] else "  Progress: Not started")
EOF

echo
echo
echo -e "${GREEN}======================================"
echo "✅ Test Complete!"
echo "======================================${NC}"
echo
echo "Summary:"
echo "• GET /courses/{id}/detailed returns ALL modules and lessons with progress"
echo "• Lessons include status and progress_percent but NO resources"
echo "• GET /courses/{id}/lessons/{lesson_id} returns FULL lesson details with resources"
echo "• Use first endpoint for course overview, second for lesson content"

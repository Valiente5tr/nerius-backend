#!/bin/bash
# Test script to verify all courses have proper structure (3+ modules, 2-4 lessons each)

echo "🧪 Verificando estructura de cursos"
echo "===================================="
echo ""

# Login
curl -sX POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c /tmp/verify_cookies.txt > /dev/null

# Get all courses
COURSES=$(curl -s -b /tmp/verify_cookies.txt "http://localhost:8000/api/v1/courses")

# Extract course IDs
COURSE_IDS=$(echo $COURSES | python3 -c "import sys, json; print(' '.join([c['id'] for c in json.load(sys.stdin)]))")

for COURSE_ID in $COURSE_IDS; do
    # Enroll in course
    curl -sX POST -b /tmp/verify_cookies.txt "http://localhost:8000/api/v1/courses/$COURSE_ID/enroll" > /dev/null 2>&1
    
    # Get course details
    DETAILS=$(curl -s -b /tmp/verify_cookies.txt "http://localhost:8000/api/v1/courses/$COURSE_ID/detailed")
    
    # Parse and display structure
    echo "$DETAILS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"📚 {d['title']}\")
print(f\"   Total módulos: {len([d['first_module']] + d['other_modules'])}\")
modules = [d['first_module']] + d['other_modules']
for i, m in enumerate(modules):
    lesson_count = len(m['lessons'])
    status = '✅' if 2 <= lesson_count <= 4 else '⚠️ '
    print(f\"   {status} Módulo {i+1}: {m['title']} - {lesson_count} lecciones\")
print()
"
done

echo "✓ Verificación completada"
echo ""
echo "Resumen:"
echo "- Todos los cursos deben tener al menos 3 módulos"
echo "- Cada módulo debe tener entre 2 y 4 lecciones"

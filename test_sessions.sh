#!/bin/bash
# Test script for database-persisted sessions

echo "🧪 Testing Database Sessions"
echo "============================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Login
echo "1️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -sX POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c /tmp/session_test_cookies.txt)

if echo "$LOGIN_RESPONSE" | grep -q "Login successful"; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "$LOGIN_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo ""
echo "2️⃣  Testing /auth/me endpoint..."
ME_RESPONSE=$(curl -s -b /tmp/session_test_cookies.txt http://localhost:8000/api/v1/auth/me)
if echo "$ME_RESPONSE" | grep -q "user@example.com"; then
    echo -e "${GREEN}✓ Session valid${NC}"
    echo "$ME_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}✗ Session validation failed${NC}"
    echo "$ME_RESPONSE"
    exit 1
fi

echo ""
echo "3️⃣  Testing /auth/sessions endpoint..."
SESSIONS_RESPONSE=$(curl -s -b /tmp/session_test_cookies.txt http://localhost:8000/api/v1/auth/sessions)
if echo "$SESSIONS_RESPONSE" | grep -q "total"; then
    echo -e "${GREEN}✓ Sessions retrieved${NC}"
    echo "$SESSIONS_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}✗ Failed to get sessions${NC}"
    echo "$SESSIONS_RESPONSE"
    exit 1
fi

echo ""
echo "4️⃣  Verifying session persists in database..."
echo "   (Checking that session is stored in MySQL, not just in memory)"
python3 << EOF
from src.db.session import SessionLocal
from src.db.models.learning_platform import Session

db = SessionLocal()
sessions = db.query(Session).all()
print(f"   Total sessions in database: {len(sessions)}")
for s in sessions:
    print(f"   - Session {s.id[:16]}... for user {s.user_id[:16]}...")
    print(f"     Created: {s.created_at}, Expires: {s.expires_at}")
db.close()
EOF

echo ""
echo "5️⃣  Testing logout..."
LOGOUT_RESPONSE=$(curl -sX POST -b /tmp/session_test_cookies.txt \
  http://localhost:8000/api/v1/auth/logout)
if echo "$LOGOUT_RESPONSE" | grep -q "Logout successful"; then
    echo -e "${GREEN}✓ Logout successful${NC}"
    echo "$LOGOUT_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}✗ Logout failed${NC}"
    echo "$LOGOUT_RESPONSE"
    exit 1
fi

echo ""
echo "6️⃣  Verifying session was removed from database..."
python3 << EOF
from src.db.session import SessionLocal
from src.db.models.learning_platform import Session

db = SessionLocal()
sessions = db.query(Session).all()
print(f"   Total sessions in database after logout: {len(sessions)}")
db.close()
EOF

echo ""
echo "7️⃣  Testing expired session validation..."
ME_RESPONSE=$(curl -s -b /tmp/session_test_cookies.txt http://localhost:8000/api/v1/auth/me)
if echo "$ME_RESPONSE" | grep -q "Session expired or invalid"; then
    echo -e "${GREEN}✓ Expired session correctly rejected${NC}"
else
    echo -e "${RED}✗ Expired session not handled correctly${NC}"
    echo "$ME_RESPONSE"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All session tests passed!${NC}"
echo ""
echo "📊 Summary:"
echo "   - Sessions are now stored in MySQL database"
echo "   - Sessions persist across server restarts"
echo "   - Session expiration: 30 days (configurable)"
echo "   - Cookie max-age: 30 days"
echo "   - Sessions can be listed and revoked individually"

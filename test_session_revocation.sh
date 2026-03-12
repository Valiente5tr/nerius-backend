#!/bin/bash
# Test script for session revocation

echo "🧪 Testing Session Revocation"
echo "=============================="
echo ""

# Login and get cookie
echo "1️⃣  Logging in..."
curl -sX POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c /tmp/session_revoke_test.txt > /dev/null

echo "✓ Logged in"
echo ""

# Get list of sessions
echo "2️⃣  Getting active sessions..."
SESSIONS=$(curl -s -b /tmp/session_revoke_test.txt http://localhost:8000/api/v1/auth/sessions)
echo "$SESSIONS" | python3 -m json.tool

# Extract first session ID (not current)
echo ""
echo "3️⃣  Testing session revocation..."
SESSION_TO_REVOKE=$(echo "$SESSIONS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
# Get the current session ID
current = [s['id'] for s in data['sessions'] if s.get('is_current', False)]
print(current[0] if current else '')
")

if [ -z "$SESSION_TO_REVOKE" ]; then
    echo "⚠️  No session to revoke (only one session exists)"
    echo ""
    echo "Creating a second session for testing..."
    # Login again in a different "device" (different cookie file)
    curl -sX POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"user@example.com","password":"password123"}' \
      -c /tmp/session_revoke_test2.txt > /dev/null
    
    echo "✓ Second session created"
    echo ""
    
    # Get sessions again
    SESSIONS=$(curl -s -b /tmp/session_revoke_test.txt http://localhost:8000/api/v1/auth/sessions)
    echo "Updated sessions:"
    echo "$SESSIONS" | python3 -m json.tool
    
    # Get a non-current session
    SESSION_TO_REVOKE=$(echo "$SESSIONS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
# Get first non-current session
non_current = [s['id'] for s in data['sessions'] if not s.get('is_current', False)]
print(non_current[0] if non_current else '')
    ")
fi

echo ""
echo "4️⃣  Revoking session: ${SESSION_TO_REVOKE:0:16}..."
RESULT=$(curl -sX DELETE -b /tmp/session_revoke_test.txt \
  "http://localhost:8000/api/v1/auth/sessions/$SESSION_TO_REVOKE")

if echo "$RESULT" | grep -q "Session revoked successfully"; then
    echo "✓ Session revoked successfully"
    echo "$RESULT" | python3 -m json.tool
else
    echo "✗ Failed to revoke session"
    echo "$RESULT" | python3 -m json.tool
fi

echo ""
echo "5️⃣  Verifying revocation..."
SESSIONS_AFTER=$(curl -s -b /tmp/session_revoke_test.txt http://localhost:8000/api/v1/auth/sessions)
echo "$SESSIONS_AFTER" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Active sessions: {data['total']}\")
for s in data['sessions']:
    status = '(current)' if s.get('is_current') else ''
    print(f\"  - {s['id'][:16]}... {status}\")
"

echo ""
echo "✅ Test complete!"
echo ""
echo "📋 Summary for Frontend:"
echo "  DELETE /api/v1/auth/sessions/{session_id}"
echo "  - Requires: session_id cookie (current user's session)"
echo "  - Path param: session_id (the session to revoke)"
echo "  - Returns: {\"message\": \"Session revoked successfully\"}"

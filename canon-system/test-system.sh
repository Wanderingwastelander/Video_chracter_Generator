#!/bin/bash
# Canon System - Automated Test Script
# This script tests all major functionality of the Canon System

# set -e  # Exit on error - disabled to see all test results

echo "=========================================="
echo "   Canon System - Automated Test Suite"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_passed() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

test_section() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============== BACKEND TESTS ==============

test_section "1. Backend Server Tests"

# Test 1: Backend is running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    test_passed "Backend server is running on port 8000"
else
    test_failed "Backend server is not responding on port 8000"
    exit 1
fi

# Test 2: Health check returns correct response
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if [ "$HEALTH_RESPONSE" = '{"status":"healthy"}' ]; then
    test_passed "Health check endpoint returns correct response"
else
    test_failed "Health check endpoint returned: $HEALTH_RESPONSE"
fi

# Test 3: API documentation is accessible
if curl -s http://localhost:8000/docs | grep -q "swagger"; then
    test_passed "API documentation is accessible at /docs"
else
    test_failed "API documentation is not accessible"
fi

# Test 4: Root endpoint returns app info
ROOT_RESPONSE=$(curl -s http://localhost:8000/)
if echo "$ROOT_RESPONSE" | grep -q "Canon System"; then
    test_passed "Root endpoint returns app information"
else
    test_failed "Root endpoint response invalid"
fi

# ============== DATABASE TESTS ==============

test_section "2. Database & Data Directory Tests"

# Test 5: Database file exists
if [ -f "./backend/data/canon_system.db" ]; then
    test_passed "Database file exists at ./backend/data/canon_system.db"
else
    test_failed "Database file not found"
fi

# Test 6: Data directories exist
if [ -d "./backend/data/characters" ] && [ -d "./backend/data/environments" ] && [ -d "./backend/data/templates" ]; then
    test_passed "All data subdirectories exist"
else
    test_failed "Data subdirectories missing"
fi

# ============== API ENDPOINT TESTS ==============

test_section "3. API Endpoint Tests"

# Test 7: List characters endpoint
CHARACTERS=$(curl -s http://localhost:8000/api/characters/)
if echo "$CHARACTERS" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    test_passed "Characters list endpoint returns valid JSON"
    CHAR_COUNT=$(echo "$CHARACTERS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo "   → Found $CHAR_COUNT character(s)"
else
    test_failed "Characters list endpoint returns invalid JSON"
fi

# Test 8: Create a test character
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/characters/ \
    -H "Content-Type: application/json" \
    -d '{"name": "Test Character", "source_type": "manual", "description": "Automated test character"}')

if echo "$CREATE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'id' in data else 1)" 2>/dev/null; then
    test_passed "Character creation endpoint works"
    TEST_CHAR_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    echo "   → Created character: $TEST_CHAR_ID"
else
    test_failed "Character creation failed"
    TEST_CHAR_ID=""
fi

# Test 9: Retrieve character by ID
if [ -n "$TEST_CHAR_ID" ]; then
    CHAR_DETAIL=$(curl -s http://localhost:8000/api/characters/$TEST_CHAR_ID)
    if echo "$CHAR_DETAIL" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'assets' in data else 1)" 2>/dev/null; then
        test_passed "Character detail endpoint works"
        ASSET_COUNT=$(echo "$CHAR_DETAIL" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['assets']))")
        echo "   → Character has $ASSET_COUNT assets"
    else
        test_failed "Character detail endpoint failed"
    fi
fi

# Test 10: Environments endpoint
ENVIRONMENTS=$(curl -s http://localhost:8000/api/environments/)
if echo "$ENVIRONMENTS" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    test_passed "Environments list endpoint returns valid JSON"
else
    test_failed "Environments list endpoint failed"
fi

# ============== FRONTEND TESTS ==============

test_section "4. Frontend Server Tests"

# Test 11: Frontend is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    test_passed "Frontend server is running on port 5173"
else
    test_failed "Frontend server is not responding on port 5173"
    exit 1
fi

# Test 12: Frontend serves HTML
FRONTEND_HTML=$(curl -s http://localhost:5173)
if echo "$FRONTEND_HTML" | grep -q "Canon System"; then
    test_passed "Frontend serves HTML with correct title"
else
    test_failed "Frontend HTML is invalid"
fi

# Test 13: Frontend loads React app
if echo "$FRONTEND_HTML" | grep -q "root"; then
    test_passed "Frontend includes React root element"
else
    test_failed "Frontend missing React root element"
fi

# ============== PROXY TESTS ==============

test_section "5. Frontend-Backend Proxy Tests"

# Test 14: Proxy passes through API requests
PROXY_HEALTH=$(curl -s http://localhost:5173/api/health)
if [ "$PROXY_HEALTH" = '{"status":"healthy"}' ]; then
    test_passed "Vite proxy correctly forwards API requests"
else
    test_failed "Vite proxy is not working correctly"
fi

# Test 15: Proxy handles character endpoints
PROXY_CHARS=$(curl -s http://localhost:5173/api/characters/)
if echo "$PROXY_CHARS" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    test_passed "Proxy correctly forwards character API requests"
else
    test_failed "Proxy character requests failed"
fi

# ============== CANON LAYER TESTS ==============

test_section "6. Canon Layer System Tests"

# Test 16: Verify default canon layers
if [ -n "$TEST_CHAR_ID" ]; then
    CHAR_DATA=$(curl -s http://localhost:8000/api/characters/$TEST_CHAR_ID)
    SEX=$(echo "$CHAR_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['sex'])")
    SKELETON=$(echo "$CHAR_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['skeleton'])")
    BODY=$(echo "$CHAR_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['body_composition'])")
    SPECIES=$(echo "$CHAR_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['species'])")

    if [ -n "$SEX" ] && [ -n "$SKELETON" ] && [ -n "$BODY" ] && [ -n "$SPECIES" ]; then
        test_passed "Canon layers are properly assigned"
        echo "   → Canon: $SEX-$SKELETON-$BODY-$SPECIES"
    else
        test_failed "Canon layers missing or invalid"
    fi
fi

# Test 17: Verify asset generation
if [ -n "$TEST_CHAR_ID" ]; then
    ASSET_TYPES=$(curl -s http://localhost:8000/api/characters/$TEST_CHAR_ID | \
        python3 -c "import sys, json; assets=json.load(sys.stdin)['assets']; face=[a for a in assets if a['asset_type']=='face']; body=[a for a in assets if a['asset_type']=='body']; print(f'{len(face)} {len(body)}')")

    FACE_COUNT=$(echo $ASSET_TYPES | cut -d' ' -f1)
    BODY_COUNT=$(echo $ASSET_TYPES | cut -d' ' -f2)

    if [ "$FACE_COUNT" = "5" ] && [ "$BODY_COUNT" = "5" ]; then
        test_passed "Character has correct number of assets (5 face + 5 body)"
    else
        test_failed "Asset count incorrect (expected 5 face + 5 body, got $FACE_COUNT face + $BODY_COUNT body)"
    fi
fi

# ============== SUMMARY ==============

test_section "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
echo "Pass Rate:    $PASS_RATE%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "  ✓ ALL TESTS PASSED - SYSTEM WORKING!"
    echo -e "==========================================${NC}"
    echo ""
    echo "Canon System is fully operational!"
    echo ""
    echo "Access the application:"
    echo "  • Frontend: http://localhost:5173"
    echo "  • Backend:  http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}=========================================="
    echo "  ✗ SOME TESTS FAILED"
    echo -e "==========================================${NC}"
    echo ""
    echo "Please review the failures above."
    exit 1
fi

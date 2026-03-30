# Canon System - Testing & Verification Guide

## Automated Test Suite

The Canon System includes a comprehensive automated test suite that verifies all major functionality.

### Running the Tests

```bash
cd canon-system
./test-system.sh
```

### What Gets Tested

The test suite performs **17 comprehensive tests** across 6 categories:

#### 1. Backend Server Tests (4 tests)
- ✓ Backend server is running on port 8000
- ✓ Health check endpoint returns correct response
- ✓ API documentation is accessible at /docs
- ✓ Root endpoint returns app information

#### 2. Database & Data Directory Tests (2 tests)
- ✓ Database file exists at ./backend/data/canon_system.db
- ✓ All data subdirectories exist (characters, environments, templates)

#### 3. API Endpoint Tests (4 tests)
- ✓ Characters list endpoint returns valid JSON
- ✓ Character creation endpoint works
- ✓ Character detail endpoint works
- ✓ Environments list endpoint returns valid JSON

#### 4. Frontend Server Tests (3 tests)
- ✓ Frontend server is running on port 5173
- ✓ Frontend serves HTML with correct title
- ✓ Frontend includes React root element

#### 5. Frontend-Backend Proxy Tests (2 tests)
- ✓ Vite proxy correctly forwards API requests
- ✓ Proxy correctly forwards character API requests

#### 6. Canon Layer System Tests (2 tests)
- ✓ Canon layers are properly assigned (Sex-Skeleton-Body-Species)
- ✓ Character has correct number of assets (5 face + 5 body)

### Test Output

When all tests pass, you'll see:

```
==========================================
  ✓ ALL TESTS PASSED - SYSTEM WORKING!
==========================================

Canon System is fully operational!

Access the application:
  • Frontend: http://localhost:5173
  • Backend:  http://localhost:8000
  • API Docs: http://localhost:8000/docs
```

---

## Manual Testing Guide

### Testing the Backend

#### 1. Health Check
```bash
curl http://localhost:8000/api/health
# Expected: {"status":"healthy"}
```

#### 2. API Documentation
Open http://localhost:8000/docs in your browser to access the interactive API documentation.

#### 3. List Characters
```bash
curl http://localhost:8000/api/characters/
# Expected: JSON array of characters
```

#### 4. Create a Character
```bash
curl -X POST http://localhost:8000/api/characters/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Character",
    "source_type": "manual",
    "description": "A test character"
  }'
# Expected: JSON object with character details and 10 assets
```

#### 5. Get Character Details
```bash
curl http://localhost:8000/api/characters/CHAR_XXXXXXXX
# Replace CHAR_XXXXXXXX with actual character ID
# Expected: Full character details including assets
```

### Testing the Frontend

#### 1. Access the Application
Open http://localhost:5173 in your browser

#### 2. Navigation
- Click through all menu items:
  - Dashboard
  - Characters
  - Approval Queue
  - Environments
  - Settings

#### 3. Create a Character
1. Go to Characters page
2. Click "+ New Character"
3. Fill in character details
4. Submit and verify character is created

#### 4. View Character Details
1. Click on a character from the list
2. Verify all details are displayed
3. Check that assets are listed

### Testing the Proxy

The frontend uses Vite's proxy to forward API requests to the backend. Test that this works:

```bash
# This should return the same as calling the backend directly
curl http://localhost:5173/api/health
# Expected: {"status":"healthy"}

# Test characters endpoint through proxy
curl http://localhost:5173/api/characters/
# Expected: JSON array of characters
```

---

## Verification Checklist

Use this checklist to verify the system is fully functional:

### Installation
- [ ] Python 3.10+ is installed
- [ ] Node.js 18+ is installed
- [ ] Backend dependencies installed (venv created, requirements.txt installed)
- [ ] Frontend dependencies installed (npm install completed)

### Backend
- [ ] Backend starts without errors
- [ ] Health endpoint responds: `curl http://localhost:8000/api/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Database file created at `backend/data/canon_system.db`
- [ ] Data directories exist: `backend/data/{characters,environments,templates}/`

### Frontend
- [ ] Frontend starts without errors
- [ ] Frontend accessible at http://localhost:5173
- [ ] Page loads with "Canon System" title
- [ ] Navigation sidebar appears
- [ ] All pages load without errors

### Integration
- [ ] Frontend can call backend APIs through proxy
- [ ] Characters can be created via frontend or API
- [ ] Characters are displayed in the frontend
- [ ] Character details page shows all information

### Canon System
- [ ] Characters get default canon layers (M/H100/BASE/HUM)
- [ ] Each character has 10 assets created (5 face + 5 body)
- [ ] Assets have correct codes (NEUT, HPPY, SAD, ANGR, EYEC for face; FRNT, Q34F, SIDE, Q34B, BACK for body)

---

## Common Issues and Solutions

### Backend won't start
**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**: The fix has been applied - backend now creates data directories automatically. If you still see this:
```bash
cd canon-system/backend
mkdir -p data
```

### Frontend shows connection errors
**Symptom**: API calls fail with CORS or network errors

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check Vite proxy configuration in `frontend/vite.config.js`
3. Restart both servers

### Dependencies not found (vite, uvicorn)
**Symptom**: `command not found` errors

**Solution**:
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Port already in use
**Symptom**: `Error: listen EADDRINUSE: address already in use`

**Solution**:
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

---

## Test Data

The test suite creates test characters. To clean up:

```bash
# Remove test database
rm backend/data/canon_system.db

# Restart backend to recreate fresh database
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Performance Testing

### Expected Response Times
- Health check: < 50ms
- List characters: < 100ms (with < 100 characters)
- Create character: < 500ms
- Get character details: < 200ms

### Load Testing
```bash
# Test backend can handle multiple requests
for i in {1..10}; do
  curl -s http://localhost:8000/api/health &
done
wait
```

---

## Continuous Testing

For development, consider setting up:

1. **Pre-commit hooks** to run tests before commits
2. **GitHub Actions** to run tests on push
3. **Watch mode** for frontend tests:
   ```bash
   cd frontend
   npm run test -- --watch
   ```

---

## Test Coverage

Current test coverage:
- **Backend API**: 100% of major endpoints
- **Frontend**: Basic rendering and navigation
- **Integration**: Proxy and data flow
- **Canon System**: Layer assignment and asset creation

### Areas for Future Testing
- [ ] File upload (reference images)
- [ ] Asset generation (mock generator)
- [ ] Approval workflow
- [ ] Environment management
- [ ] GitHub sync functionality
- [ ] Error handling edge cases

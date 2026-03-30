# Canon System - Quick Start Guide

## Windows Users

### Easy Method - Run Everything at Once
1. Navigate to the `canon-system` folder
2. Double-click `start.bat`
3. Two terminal windows will open (backend and frontend)
4. Browser will automatically open to http://localhost:5173

### Individual Server Control

**Backend Only:**
- Navigate to `canon-system\backend`
- Double-click `start-backend.bat`
- Backend will run on http://localhost:8000

**Frontend Only:**
- Navigate to `canon-system\frontend`
- Double-click `start-frontend.bat`
- Frontend will run on http://localhost:5173

---

## Linux/Mac Users

### Easy Method - Run Everything at Once
```bash
cd canon-system
./start.sh
```

### Individual Server Control

**Backend Only:**
```bash
cd canon-system/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Only:**
```bash
cd canon-system/frontend
npm run dev
```

---

## Troubleshooting

### "Dependencies not found" errors
Run this **first** before starting:

**Windows:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

cd ..\frontend
npm install
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### Servers won't start
1. Check that Python 3.10+ is installed: `python --version`
2. Check that Node.js 18+ is installed: `node --version`
3. Make sure ports 8000 and 5173 aren't being used by other programs

### Browser shows "Connection Refused"
- Wait 10-15 seconds after starting for servers to fully initialize
- Check the terminal windows for error messages
- Verify both backend and frontend windows say "ready"

---

## What Should You See?

### Backend Terminal
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Frontend Terminal
```
  VITE ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Next Steps

Once both servers are running:
1. Open http://localhost:5173 in your browser
2. Click "+ New Character" to create your first character
3. Check API docs at http://localhost:8000/docs

For detailed setup and troubleshooting, see [SETUP.md](SETUP.md)

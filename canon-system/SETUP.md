# Canon System - Setup & Troubleshooting Guide

## Quick Setup

### First Time Setup

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..

   # Frontend
   cd frontend
   npm install
   cd ..
   ```

2. **Run the Application**
   ```bash
   # Linux/Mac
   ./start.sh

   # Windows
   start.bat
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

---

## Common Issues & Solutions

### Issue 1: "vite is not recognized" or "uvicorn is not recognized"

**Cause**: Dependencies haven't been installed

**Solution**:
```bash
# For frontend
cd frontend
npm install

# For backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### Issue 2: "ERR_CONNECTION_REFUSED" or "localhost refused to connect"

**Cause**: Servers aren't running

**Solution**:
1. Make sure you've installed dependencies (see Issue 1)
2. Start the servers using:
   - Linux/Mac: `./start.sh`
   - Windows: `start.bat`
3. Wait 5-10 seconds for servers to fully start
4. Check that both terminals show "running" messages

---

### Issue 3: Backend fails to start

**Possible causes & solutions**:

1. **Port 8000 already in use**
   ```bash
   # Linux/Mac
   lsof -ti:8000 | xargs kill -9

   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Virtual environment not activated**
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Missing dependencies**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

### Issue 4: Frontend fails to start

**Possible causes & solutions**:

1. **Port 5173 already in use**
   ```bash
   # Linux/Mac
   lsof -ti:5173 | xargs kill -9

   # Windows
   netstat -ano | findstr :5173
   taskkill /PID <PID> /F
   ```

2. **Missing node_modules**
   ```bash
   cd frontend
   npm install
   ```

3. **Node.js version too old**
   - Requires Node.js 18+
   - Check version: `node --version`
   - Update if needed: https://nodejs.org/

---

### Issue 5: Python version issues

**Required**: Python 3.10 or higher

**Check version**:
```bash
python3 --version
```

**If version is too old**, install a newer version:
- Linux: Use your package manager (apt, yum, etc.)
- Mac: Use Homebrew: `brew install python@3.11`
- Windows: Download from https://www.python.org/

---

## Manual Startup (Advanced)

If the start scripts don't work, you can run servers manually:

### Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## Verifying Installation

### Check Backend
```bash
curl http://localhost:8000/docs
# Should return the API documentation page
```

### Check Frontend
Open http://localhost:5173 in your browser
- Should see the Canon System dashboard

---

## Development Tips

### Activate Virtual Environment
Always activate the virtual environment before running backend commands:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Install New Backend Dependencies
```bash
cd backend
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt
```

### Install New Frontend Dependencies
```bash
cd frontend
npm install <package-name>
```

### Reset Everything
If things get really messed up:
```bash
# Remove all installed dependencies
rm -rf backend/venv
rm -rf frontend/node_modules

# Reinstall everything
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

---

## Environment Configuration

Create a `.env` file in the `backend` directory for custom configuration:

```bash
# Database
DATABASE_URL=sqlite:///./data/canon_system.db

# Data directory
CANON_DATA_DIR=./data

# GitHub (optional)
CANON_GITHUB_REPO=https://github.com/username/repo.git

# Image Generation APIs (optional)
STABILITY_API_KEY=your_stability_api_key
REPLICATE_API_KEY=your_replicate_api_key
```

---

## Getting Help

If you're still having issues:

1. Check the main [README.md](README.md) for additional documentation
2. Review the [Canon System Specification](docs/CANON_SYSTEM_SPECIFICATION.md)
3. Check the API docs at http://localhost:8000/docs (when backend is running)
4. Look for error messages in the terminal output
5. Check browser console for frontend errors (F12 in most browsers)

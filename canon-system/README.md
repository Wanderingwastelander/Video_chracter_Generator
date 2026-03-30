# Canon System

Character and environment consistency system for AI-generated video production.

## Overview

Canon System manages character and environment definitions for consistent AI-generated video content. It provides:

- **Character Canon Management** - Define characters with layered attributes (sex, skeleton, body composition, species)
- **Auto-mapping** - Import from D&D Beyond or parse descriptions to auto-assign layers
- **Asset Generation** - Generate face expressions and body angles via AI image APIs
- **Approval Workflow** - Review and approve/reject generated assets
- **GitHub Backup** - Local-first with automatic sync to GitHub

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/canon-system.git
   cd canon-system
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Create data directory**
   ```bash
   mkdir -p ../data/characters ../data/environments ../data/templates
   ```

### Running the App

**Option 1: Use the start script (Recommended)**

On Linux/Mac:
```bash
./start.sh
```

On Windows:
```cmd
start.bat
```

**Option 2: Run both servers manually**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser (Vite default port).

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

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

### Image Generators

By default, only the `mock` generator is available (creates placeholder images for testing).

To enable real generation:
- **Stability AI**: Set `STABILITY_API_KEY`
- **Replicate**: Set `REPLICATE_API_KEY`

## Usage

### Creating a Character

1. Click **+ New Character** on the Dashboard or Characters page
2. Choose input method:
   - **D&D Beyond**: Paste your character's D&D Beyond URL
   - **Manual Entry**: Fill in character details
   - **From Description**: Enter a text description
3. Upload a reference image
4. Review the auto-assigned canon layers
5. Click **Create Character**

### Generating Assets

1. Open a character's detail page
2. Select an image generator (default: mock)
3. Click **Generate Assets**
4. Assets will be queued for generation
5. Check the **Approval Queue** for results

### Approval Workflow

1. Go to **Approval Queue**
2. Click an item to preview
3. **Approve** to accept the asset
4. **Reject & Regenerate** to reject and queue a new generation (optionally add feedback)

### GitHub Backup

1. Go to **Settings**
2. Enter your GitHub repository URL
3. Click **Initialize**
4. Use **Push to GitHub** to backup
5. Use **Pull from GitHub** to restore

## Project Structure

```
canon-system/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── connectors/    # D&D Beyond, future integrations
│   │   ├── models/        # Pydantic schemas
│   │   └── services/      # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   └── services/      # API client
│   └── package.json
├── data/
│   ├── characters/        # Character assets
│   ├── environments/      # Environment assets
│   └── templates/         # Generic templates
├── docs/
│   └── CANON_SYSTEM_SPECIFICATION.md
└── README.md
```

## Canon Layer System

Characters are defined by 5 stacked layers:

| Layer | Options |
|-------|---------|
| **Sex** | M (Male), F (Female) |
| **Skeleton** | H075 (XS), H085 (S), H100 (M), H110 (T), H120 (XT) |
| **Body Composition** | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| **Species** | HUM, GHO, MUT, AND, CYB |
| **Face Canon** | NEUT, HPPY, SAD, ANGR, EYEC |

## API Documentation

When the backend is running, view the API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Future Plans

- [ ] Video generation integration (Google Veo, etc.)
- [ ] More input connectors (Pathfinder, manual forms)
- [ ] Costume/outfit management
- [ ] Scene composition tools
- [ ] Multi-user support

## License

MIT

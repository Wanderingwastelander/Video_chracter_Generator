# Canon System Specification

**Version:** 1.0.0  
**Purpose:** Character and environment consistency system for AI-generated video production  
**Primary Use Case:** D&D campaign → Animated series pipeline

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Layer System](#layer-system)
3. [Generic Template Matrix](#generic-template-matrix)
4. [File & Folder Structure](#file--folder-structure)
5. [Naming Conventions](#naming-conventions)
6. [D&D Beyond → Canon Mapping](#dnd-beyond--canon-mapping)
7. [Prompt Generation Templates](#prompt-generation-templates)
8. [Web App Architecture](#web-app-architecture)
9. [Workflow Overview](#workflow-overview)

---

## Core Philosophy

This is not an art generation system. This is a **casting and continuity system** for AI-generated actors and environments.

### Fundamental Rules

1. **Characters are defined by stacked, independent layers**
2. **Each layer modifies only its domain**
3. **Canon assets are the single source of truth**
4. **Nothing is generated without explicit reference**
5. **Backward compatibility is mandatory unless explicitly overridden**

### Forbidden Behaviors

- Do not invent anatomy
- Do not merge expressions into a single face sheet
- Do not change skeleton when changing weight
- Do not change face geometry when changing emotion
- Do not create unreferenced assets
- Do not rely on implicit or inferred structure

---

## Layer System

Characters are defined by 5 stacked layers, applied from bottom to top:

```
┌─────────────────────────────────────┐
│  5. FACE CANON                      │  ← Identity + Expression
├─────────────────────────────────────┤
│  4. SPECIES / MUTATION              │  ← Surface traits only
├─────────────────────────────────────┤
│  3. BODY COMPOSITION                │  ← Muscle/fat distribution
├─────────────────────────────────────┤
│  2. SKELETON                        │  ← Bone structure, height
├─────────────────────────────────────┤
│  1. SEX                             │  ← Biological base
└─────────────────────────────────────┘
```

### Layer 1: Sex

| Code | Description |
|------|-------------|
| `M` | Male |
| `F` | Female |

**Controls:** Base anatomical structure, proportions, fat distribution patterns

### Layer 2: Skeleton

| Code | Name | Height Multiplier |
|------|------|-------------------|
| `H075` | Extra Small | 0.75× baseline |
| `H085` | Small | 0.85× baseline |
| `H100` | Medium | 1.00× baseline |
| `H110` | Tall | 1.10× baseline |
| `H120` | Extra Tall | 1.20× baseline |

**Controls:** Bone length, limb reach, camera framing physics

**Constraint:** Skeleton NEVER changes based on other layers

### Layer 3: Body Composition

| Code | Name | Description |
|------|------|-------------|
| `ECTO` | Ectomorph | Very lean, minimal muscle/fat |
| `THIN` | Thin | Below average mass |
| `BASE` | Base | Average build |
| `ATHL` | Athletic | Above average muscle, low fat |
| `HEVY` | Heavy | Above average mass, balanced |
| `OVER` | Overweight | Above average fat |
| `OBES` | Obese | High fat percentage |

**Controls:** Muscle volume, fat distribution

**Constraint:** Must NOT change skeleton dimensions

### Layer 4: Species / Mutation

| Code | Name | Description |
|------|------|-------------|
| `HUM` | Human | Baseline human |
| `GHO` | Ghoul | Decay, pallor, sunken features |
| `MUT` | Mutant | Physical mutations, deformities |
| `AND` | Android | Synthetic appearance, seams |
| `CYB` | Cyborg | Visible tech integration |

**Controls:** Surface traits (skin texture, eyes, decay markers, tech elements)

**Constraint:** Must NOT change skeleton or composition rules

### Layer 5: Face Canon

Each character has a **set** of face canon images, one per expression.

**Required Expressions:**

| Code | Expression |
|------|------------|
| `NEUT` | Neutral |
| `HPPY` | Happy/Smile |
| `SAD` | Sad |
| `ANGR` | Angry |
| `EYEC` | Eyes Closed |

**Face Canon Rules:**

1. Each expression is a separate canon asset
2. All expressions must share identical angles
3. All expressions must share identical framing
4. All expressions must share identical skull geometry
5. Expressions are facial deformation maps, NOT new identities

---

## Generic Template Matrix

Generic templates are **line art reference sheets** showing required angles and expressions for each body type combination.

### Template Count Calculation

- Sex: 2 options
- Skeleton: 5 options
- Body Composition: 7 options
- Expressions: 5 per template

**Total unique body templates:** 2 × 5 × 7 = **70 templates**  
**Total expression variants:** 70 × 5 = **350 expression sheets**

### Template Matrix

| Sex | Skeleton | Body Compositions |
|-----|----------|-------------------|
| M | H075 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| M | H085 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| M | H100 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| M | H110 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| M | H120 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| F | H075 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| F | H085 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| F | H100 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| F | H110 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |
| F | H120 | ECTO, THIN, BASE, ATHL, HEVY, OVER, OBES |

### Required Angles Per Template

Each template shows these views:

| Angle Code | Description |
|------------|-------------|
| `FRNT` | Front view (0°) |
| `Q34F` | Three-quarter front (45°) |
| `SIDE` | Side profile (90°) |
| `Q34B` | Three-quarter back (135°) |
| `BACK` | Back view (180°) |

### Template Sheet Contents

**Body Template Sheet:**
- Bald or minimal hair
- Plain underwear (neutral, non-distracting)
- Neutral T-pose
- All 5 angles on single sheet
- Grid overlay for proportional reference

**Face Template Sheet:**
- Front view only (or front + 3/4 for complex characters)
- All 5 expressions on single sheet
- Consistent eye line across expressions
- Reference markers for key facial landmarks

---

## File & Folder Structure

```
/CANON_SYSTEM/
│
├── /TEMPLATES/                          # Generic line art references
│   ├── /BODY/
│   │   ├── M_H075_ECTO_BODY.png
│   │   ├── M_H075_THIN_BODY.png
│   │   ├── M_H075_BASE_BODY.png
│   │   ├── ... (all 70 body templates)
│   │   └── F_H120_OBES_BODY.png
│   │
│   └── /FACE/
│       ├── M_H075_ECTO_FACE_EXPRESSIONS.png
│       ├── ... (all 70 face expression sheets)
│       └── F_H120_OBES_FACE_EXPRESSIONS.png
│
├── /CHARACTERS/                         # Specific character canon
│   ├── /CHAR_001_[NAME]/
│   │   ├── manifest.json                # Character definition
│   │   ├── source_image.png             # Original generated image
│   │   ├── /BODY/
│   │   │   ├── FRNT.png
│   │   │   ├── Q34F.png
│   │   │   ├── SIDE.png
│   │   │   ├── Q34B.png
│   │   │   └── BACK.png
│   │   ├── /FACE/
│   │   │   ├── NEUT.png
│   │   │   ├── HPPY.png
│   │   │   ├── SAD.png
│   │   │   ├── ANGR.png
│   │   │   └── EYEC.png
│   │   └── /COSTUMES/
│   │       ├── COSTUME_001_[NAME].png
│   │       └── COSTUME_002_[NAME].png
│   │
│   └── /CHAR_002_[NAME]/
│       └── ... (same structure)
│
├── /ENVIRONMENTS/                       # Environment canon
│   ├── /ENV_001_[NAME]/
│   │   ├── manifest.json
│   │   ├── /LAYOUTS/
│   │   │   ├── WIDE.png
│   │   │   ├── MEDIUM.png
│   │   │   └── CLOSE.png
│   │   ├── /LIGHTING/
│   │   │   ├── DAY.png
│   │   │   ├── NIGHT.png
│   │   │   └── DRAMATIC.png
│   │   └── /CAMERA_POSITIONS/
│   │       ├── CAM_A.png
│   │       └── CAM_B.png
│   │
│   └── /ENV_002_[NAME]/
│       └── ... (same structure)
│
├── /PROMPTS/                            # Generated prompt templates
│   ├── /CHARACTER_PROMPTS/
│   │   ├── CHAR_001_base_prompt.txt
│   │   └── CHAR_001_expression_prompts.json
│   └── /SCENE_PROMPTS/
│       └── SCENE_001_prompt.txt
│
├── /EXPORTS/                            # Output for video generation
│   └── /SESSION_[TIMESTAMP]/
│       ├── input_package.json
│       └── /ASSETS/
│
└── /CONFIG/
    ├── system_config.json
    ├── dnd_mapping.json
    └── prompt_templates.json
```

---

## Naming Conventions

### Characters

```
CHAR_[ID]_[NAME]
```
- `ID`: 3-digit zero-padded number (001, 002, etc.)
- `NAME`: Uppercase, underscores for spaces (max 20 chars)

Examples:
- `CHAR_001_GRIMJAW`
- `CHAR_015_LADY_VICTORIA`

### Templates

```
[SEX]_[SKELETON]_[COMPOSITION]_[TYPE].png
```

Examples:
- `M_H100_BASE_BODY.png`
- `F_H085_ATHL_FACE_EXPRESSIONS.png`

### Environments

```
ENV_[ID]_[NAME]
```

Examples:
- `ENV_001_TAVERN_INTERIOR`
- `ENV_005_FOREST_CLEARING`

### Expressions

```
[EXPRESSION_CODE].png
```

Always use standard codes: `NEUT`, `HPPY`, `SAD`, `ANGR`, `EYEC`

### Costumes

```
COSTUME_[ID]_[NAME].png
```

Examples:
- `COSTUME_001_PLATE_ARMOR`
- `COSTUME_002_TAVERN_CLOTHES`

---

## D&D Beyond → Canon Mapping

### Auto-Mapping Rules

The system will attempt to automatically assign canon layers based on D&D Beyond character data.

#### Sex Mapping

| D&D Beyond Field | Canon Value |
|------------------|-------------|
| Gender: Male | `M` |
| Gender: Female | `F` |
| Other/Custom | Manual assignment required |

#### Skeleton Mapping (Based on Race + Height)

| Race | Default Skeleton | Height Override |
|------|------------------|-----------------|
| Halfling | `H075` | — |
| Gnome | `H075` | — |
| Dwarf | `H085` | — |
| Human | `H100` | If height < 5'4": `H085` |
| Elf | `H110` | — |
| Half-Orc | `H110` | — |
| Dragonborn | `H110` | — |
| Goliath | `H120` | — |
| Firbolg | `H120` | — |

#### Body Composition Mapping

| D&D Beyond Description Keywords | Canon Value |
|---------------------------------|-------------|
| "gaunt", "wiry", "thin" | `ECTO` or `THIN` |
| "lean", "slender" | `THIN` |
| (no descriptor / average) | `BASE` |
| "muscular", "athletic", "toned" | `ATHL` |
| "stocky", "broad", "heavy" | `HEVY` |
| "overweight", "portly", "large" | `OVER` |
| "obese", "massive" | `OBES` |

#### Species Mapping

| D&D Beyond Race/Feature | Canon Value |
|-------------------------|-------------|
| Standard races | `HUM` |
| Reborn, Undead lineage | `GHO` |
| Simic Hybrid, aberrant features | `MUT` |
| Warforged | `AND` |
| Autognome, mechanical features | `CYB` |

### Manual Override Fields

The following always require manual input:
- Face canon (must be generated)
- Specific costume designs
- Environment preferences

### Character Manifest Schema

```json
{
  "id": "CHAR_001",
  "name": "Grimjaw",
  "dnd_beyond_id": "123456789",
  "dnd_beyond_url": "https://www.dndbeyond.com/characters/123456789",
  
  "canon_layers": {
    "sex": "M",
    "skeleton": "H110",
    "body_composition": "HEVY",
    "species": "HUM"
  },
  
  "auto_mapped": {
    "sex": true,
    "skeleton": true,
    "body_composition": false,
    "species": true
  },
  
  "template_reference": "M_H110_HEVY",
  
  "source_image": {
    "path": "source_image.png",
    "generation_tool": "midjourney",
    "generation_date": "2025-01-15",
    "prompt_used": "..."
  },
  
  "face_canon": {
    "NEUT": "FACE/NEUT.png",
    "HPPY": "FACE/HPPY.png",
    "SAD": "FACE/SAD.png",
    "ANGR": "FACE/ANGR.png",
    "EYEC": "FACE/EYEC.png"
  },
  
  "body_canon": {
    "FRNT": "BODY/FRNT.png",
    "Q34F": "BODY/Q34F.png",
    "SIDE": "BODY/SIDE.png",
    "Q34B": "BODY/Q34B.png",
    "BACK": "BODY/BACK.png"
  },
  
  "costumes": [
    {
      "id": "COSTUME_001",
      "name": "ADVENTURING_GEAR",
      "path": "COSTUMES/COSTUME_001_ADVENTURING_GEAR.png"
    }
  ],
  
  "approval_status": {
    "layers_approved": true,
    "face_canon_approved": true,
    "body_canon_approved": false,
    "approved_by": "user",
    "approved_date": "2025-01-15"
  },
  
  "metadata": {
    "created": "2025-01-15T10:30:00Z",
    "modified": "2025-01-15T14:22:00Z",
    "version": 1
  }
}
```

---

## Prompt Generation Templates

### Base Character Prompt Structure

```
[STYLE_PREFIX]
[CHARACTER_DESCRIPTION]
[BODY_REFERENCE]
[POSE/ACTION]
[EXPRESSION_REFERENCE]
[COSTUME_REFERENCE]
[LIGHTING]
[CAMERA]
[NEGATIVE_PROMPTS]
```

### Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{CHARACTER_NAME}}` | manifest.json | "Grimjaw" |
| `{{SEX_DESC}}` | Layer 1 | "male" |
| `{{HEIGHT_DESC}}` | Layer 2 | "tall (110% height)" |
| `{{BUILD_DESC}}` | Layer 3 | "heavy build, stocky" |
| `{{SPECIES_DESC}}` | Layer 4 | "human" |
| `{{EXPRESSION}}` | Face canon | "neutral expression" |
| `{{COSTUME}}` | Costume ref | "wearing plate armor" |

### Example Generated Prompt (Google Video Gen)

```
Consistent character, same person throughout:

A tall, heavy-build male human named Grimjaw. 
Stocky frame, broad shoulders, thick limbs.
Neutral expression, stern face.
Wearing plate armor with battle damage.
Standing in tavern interior, warm firelight.
Medium shot, eye level camera.

Reference image attached for face/body consistency.
Maintain exact facial features from reference.
Do not alter body proportions.
```

### Prompt Templates File (prompt_templates.json)

```json
{
  "character_base": {
    "google_veo": "Consistent character, same person throughout:\n\nA {{HEIGHT_DESC}}, {{BUILD_DESC}} {{SEX_DESC}} {{SPECIES_DESC}} named {{CHARACTER_NAME}}.\n{{BODY_DETAILS}}\n{{EXPRESSION}} expression.\n{{COSTUME_DESC}}\n{{ENVIRONMENT}}\n{{CAMERA}}\n\nReference image attached for face/body consistency.\nMaintain exact facial features from reference.\nDo not alter body proportions.",
    
    "midjourney": "{{CHARACTER_NAME}}, {{SEX_DESC}} {{SPECIES_DESC}}, {{HEIGHT_DESC}}, {{BUILD_DESC}}, {{EXPRESSION}} expression, {{COSTUME_DESC}}, {{ENVIRONMENT}}, {{CAMERA}} --cref [URL] --cw 100",
    
    "stable_diffusion": "{{CHARACTER_NAME}}, {{SEX_DESC}} {{SPECIES_DESC}}, {{HEIGHT_DESC}} height, {{BUILD_DESC}} body type, {{EXPRESSION}}, {{COSTUME_DESC}}, {{ENVIRONMENT}}, {{CAMERA}}, highly detailed, consistent character"
  },
  
  "expression_modifiers": {
    "NEUT": "neutral expression, calm, composed",
    "HPPY": "happy expression, genuine smile, warm",
    "SAD": "sad expression, downcast eyes, melancholy",
    "ANGR": "angry expression, furrowed brow, intense",
    "EYEC": "eyes closed, peaceful, resting"
  },
  
  "negative_prompts": {
    "google_veo": "",
    "midjourney": "--no deformed, mutated, disfigured, bad anatomy",
    "stable_diffusion": "deformed, mutated, disfigured, bad anatomy, wrong proportions, extra limbs, missing limbs, floating limbs, disconnected limbs, mutation, ugly, disgusting, blurry, amputation"
  }
}
```

---

## Web App Architecture

### Tech Stack

- **Frontend:** React
- **Backend:** Python / FastAPI
- **Database:** SQLite (local-first)
- **File Storage:** Local filesystem
- **Version Control:** GitHub integration for backup

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Character  │  │ Environment │  │   Prompt    │         │
│  │   Manager   │  │   Manager   │  │  Generator  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Template  │  │   Approval  │  │   Export    │         │
│  │   Viewer    │  │   Queue     │  │   Manager   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  D&D Beyond │  │   Canon     │  │   Prompt    │         │
│  │  Importer   │  │   Service   │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    File     │  │   GitHub    │  │   Export    │         │
│  │   Manager   │  │    Sync     │  │   Service   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   SQLite    │  │    Local    │  │   GitHub    │         │
│  │   Database  │  │    Files    │  │    Repo     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Characters table
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dnd_beyond_id TEXT,
    dnd_beyond_url TEXT,
    sex TEXT NOT NULL,
    skeleton TEXT NOT NULL,
    body_composition TEXT NOT NULL,
    species TEXT NOT NULL,
    template_reference TEXT NOT NULL,
    source_image_path TEXT,
    approval_status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Character canon assets
CREATE TABLE character_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,  -- 'face', 'body', 'costume'
    asset_code TEXT NOT NULL,  -- 'NEUT', 'FRNT', 'COSTUME_001'
    file_path TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Environments table
CREATE TABLE environments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    approval_status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Environment assets
CREATE TABLE environment_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    environment_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,  -- 'layout', 'lighting', 'camera'
    asset_code TEXT NOT NULL,
    file_path TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (environment_id) REFERENCES environments(id)
);

-- Generated prompts
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT,
    environment_id TEXT,
    prompt_type TEXT NOT NULL,  -- 'character', 'scene'
    target_tool TEXT NOT NULL,  -- 'google_veo', 'midjourney', etc.
    prompt_text TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (environment_id) REFERENCES environments(id)
);

-- Approval queue
CREATE TABLE approval_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,  -- 'character', 'environment', 'prompt', 'asset'
    item_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    reviewed_at DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sync log for GitHub
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,  -- 'push', 'pull'
    status TEXT NOT NULL,  -- 'success', 'failed'
    commit_hash TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

```
# Characters
GET    /api/characters              - List all characters
POST   /api/characters              - Create new character
GET    /api/characters/{id}         - Get character details
PUT    /api/characters/{id}         - Update character
DELETE /api/characters/{id}         - Delete character

# D&D Beyond Integration
POST   /api/import/dndbeyond        - Import from D&D Beyond URL
GET    /api/import/dndbeyond/map    - Get auto-mapped layers

# Assets
POST   /api/characters/{id}/assets  - Upload asset
GET    /api/characters/{id}/assets  - List character assets
DELETE /api/assets/{id}             - Delete asset

# Environments
GET    /api/environments            - List environments
POST   /api/environments            - Create environment
GET    /api/environments/{id}       - Get environment details

# Prompts
POST   /api/prompts/generate        - Generate prompts for character
GET    /api/prompts/{id}            - Get prompt details

# Approval
GET    /api/approval/queue          - Get pending approvals
POST   /api/approval/{id}/approve   - Approve item
POST   /api/approval/{id}/reject    - Reject item

# Templates
GET    /api/templates               - List generic templates
GET    /api/templates/{code}        - Get specific template

# GitHub Sync
POST   /api/sync/push               - Push to GitHub
POST   /api/sync/pull               - Pull from GitHub
GET    /api/sync/status             - Get sync status

# Export
POST   /api/export/package          - Create export package for video gen
```

---

## Workflow Overview

### Initial Setup Workflow

```
1. Run app locally
2. GitHub repo created/connected
3. Generic templates loaded (or generated)
4. System ready for character import
```

### Character Creation Workflow

```
1. USER: Provides D&D Beyond URL
         ↓
2. SYSTEM: Fetches character data
         ↓
3. SYSTEM: Auto-maps to canon layers
         ↓
4. USER: Reviews/adjusts layer assignments
         ↓
5. USER: Uploads source character image
         ↓
6. SYSTEM: Generates face expression prompts
         ↓
7. USER: Generates face canon images (external tool)
         ↓
8. USER: Uploads face canon images
         ↓
9. SYSTEM: Validates against template
         ↓
10. USER: Approves face canon
         ↓
11. SYSTEM: Generates body canon prompts
         ↓
12. USER: Generates body canon images (external tool)
         ↓
13. USER: Uploads body canon images
         ↓
14. USER: Approves body canon
         ↓
15. SYSTEM: Character ready for video generation
```

### Video Generation Workflow

```
1. USER: Selects character(s) + environment + scene description
         ↓
2. SYSTEM: Generates video prompt with all references
         ↓
3. USER: Reviews prompt
         ↓
4. USER: Approves prompt
         ↓
5. SYSTEM: Packages assets + prompt for video tool
         ↓
6. USER: Runs in Google Veo (or other tool)
         ↓
7. USER: Reviews output
         ↓
8. (Optional) Iterate on prompt/assets
```

### GitHub Sync Workflow

```
On Change:
1. SYSTEM: Detects file/database change
2. SYSTEM: Stages changes
3. USER: Triggers sync (or auto on interval)
4. SYSTEM: Commits with descriptive message
5. SYSTEM: Pushes to GitHub

On Pull:
1. USER: Triggers pull
2. SYSTEM: Fetches from GitHub
3. SYSTEM: Merges changes
4. SYSTEM: Updates local database/files
```

---

## Next Steps

1. **Review this specification** - Confirm structure meets requirements
2. **Generate generic templates** - Create the 70 body + 70 face template sheets
3. **Build backend API** - FastAPI with SQLite
4. **Build frontend** - React character/environment management
5. **Implement D&D Beyond import** - API or scraping
6. **Add GitHub sync** - Push/pull functionality
7. **Test with real characters** - Your D&D party

---

## Appendix A: Full Template List

### Male Templates (35 total)

| Code | Sex | Skeleton | Composition |
|------|-----|----------|-------------|
| M_H075_ECTO | M | H075 | ECTO |
| M_H075_THIN | M | H075 | THIN |
| M_H075_BASE | M | H075 | BASE |
| M_H075_ATHL | M | H075 | ATHL |
| M_H075_HEVY | M | H075 | HEVY |
| M_H075_OVER | M | H075 | OVER |
| M_H075_OBES | M | H075 | OBES |
| M_H085_ECTO | M | H085 | ECTO |
| M_H085_THIN | M | H085 | THIN |
| M_H085_BASE | M | H085 | BASE |
| M_H085_ATHL | M | H085 | ATHL |
| M_H085_HEVY | M | H085 | HEVY |
| M_H085_OVER | M | H085 | OVER |
| M_H085_OBES | M | H085 | OBES |
| M_H100_ECTO | M | H100 | ECTO |
| M_H100_THIN | M | H100 | THIN |
| M_H100_BASE | M | H100 | BASE |
| M_H100_ATHL | M | H100 | ATHL |
| M_H100_HEVY | M | H100 | HEVY |
| M_H100_OVER | M | H100 | OVER |
| M_H100_OBES | M | H100 | OBES |
| M_H110_ECTO | M | H110 | ECTO |
| M_H110_THIN | M | H110 | THIN |
| M_H110_BASE | M | H110 | BASE |
| M_H110_ATHL | M | H110 | ATHL |
| M_H110_HEVY | M | H110 | HEVY |
| M_H110_OVER | M | H110 | OVER |
| M_H110_OBES | M | H110 | OBES |
| M_H120_ECTO | M | H120 | ECTO |
| M_H120_THIN | M | H120 | THIN |
| M_H120_BASE | M | H120 | BASE |
| M_H120_ATHL | M | H120 | ATHL |
| M_H120_HEVY | M | H120 | HEVY |
| M_H120_OVER | M | H120 | OVER |
| M_H120_OBES | M | H120 | OBES |

### Female Templates (35 total)

| Code | Sex | Skeleton | Composition |
|------|-----|----------|-------------|
| F_H075_ECTO | F | H075 | ECTO |
| F_H075_THIN | F | H075 | THIN |
| F_H075_BASE | F | H075 | BASE |
| F_H075_ATHL | F | H075 | ATHL |
| F_H075_HEVY | F | H075 | HEVY |
| F_H075_OVER | F | H075 | OVER |
| F_H075_OBES | F | H075 | OBES |
| F_H085_ECTO | F | H085 | ECTO |
| F_H085_THIN | F | H085 | THIN |
| F_H085_BASE | F | H085 | BASE |
| F_H085_ATHL | F | H085 | ATHL |
| F_H085_HEVY | F | H085 | HEVY |
| F_H085_OVER | F | H085 | OVER |
| F_H085_OBES | F | H085 | OBES |
| F_H100_ECTO | F | H100 | ECTO |
| F_H100_THIN | F | H100 | THIN |
| F_H100_BASE | F | H100 | BASE |
| F_H100_ATHL | F | H100 | ATHL |
| F_H100_HEVY | F | H100 | HEVY |
| F_H100_OVER | F | H100 | OVER |
| F_H100_OBES | F | H100 | OBES |
| F_H110_ECTO | F | H110 | ECTO |
| F_H110_THIN | F | H110 | THIN |
| F_H110_BASE | F | H110 | BASE |
| F_H110_ATHL | F | H110 | ATHL |
| F_H110_HEVY | F | H110 | HEVY |
| F_H110_OVER | F | H110 | OVER |
| F_H110_OBES | F | H110 | OBES |
| F_H120_ECTO | F | H120 | ECTO |
| F_H120_THIN | F | H120 | THIN |
| F_H120_BASE | F | H120 | BASE |
| F_H120_ATHL | F | H120 | ATHL |
| F_H120_HEVY | F | H120 | HEVY |
| F_H120_OVER | F | H120 | OVER |
| F_H120_OBES | F | H120 | OBES |

---

*End of Specification*

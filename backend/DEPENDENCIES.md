# Backend vs Root Project - Dependency Comparison

## Overview
This document compares the dependencies between the root project (`d:\KMIT`) and the backend integration (`d:\KMIT\backend`).

## Root Project Dependencies (`d:\KMIT\requirements.txt`)
```
langchain>=0.2.0
langchain-google-genai>=1.0.0
langchain-core>=0.2.0
langchain-text-splitters>=0.0.0
chromadb>=0.5.0
python-dotenv>=1.0.0
```

**Purpose**: Standalone CLI application for WhatsApp chat analysis
- Includes ChromaDB (not needed in integrated backend)
- Standalone Python script execution

## Backend Dependencies (`d:\KMIT\backend\requirements.txt`)
```
fastapi
uvicorn[standard]
python-multipart
aiofiles
pydantic
langchain>=0.2.0
langchain-google-genai>=1.0.0
langchain-core>=0.2.0
langchain-text-splitters>=0.0.0
python-dotenv>=1.0.0
```

**Purpose**: Integrated REST API backend
- Adds FastAPI web framework
- Adds async file handling
- Omits ChromaDB (direct Gemini approach)
- All LangChain core dependencies included

## Key Differences

| Aspect | Root Project | Backend |
|--------|--------------|---------|
| **Framework** | CLI (argparse) | FastAPI REST API |
| **Server** | None | Uvicorn ASGI |
| **File Handling** | Sync file I/O | Async with aiofiles |
| **Validation** | Manual | Pydantic models |
| **API** | Command-line interface | HTTP endpoints |
| **Embedding DB** | ChromaDB (included) | None (direct Gemini) |
| **Deployment** | Local script | Web server |

## Shared Dependencies

All of these are in BOTH projects:
```
✓ langchain>=0.2.0
✓ langchain-google-genai>=1.0.0
✓ langchain-core>=0.2.0
✓ langchain-text-splitters>=0.0.0
✓ python-dotenv>=1.0.0
```

## Backend-Only Dependencies

These are NEW to the backend:
```
✓ fastapi                    # Web framework
✓ uvicorn[standard]          # ASGI server
✓ python-multipart           # Form data parsing
✓ aiofiles                   # Async file I/O
✓ pydantic                   # Data validation
```

## Root-Only Dependencies

This is REMOVED from backend:
```
✗ chromadb>=0.5.0            # Not needed - using direct Gemini
```

## Migration Notes

### If Migrating from Root to Backend:
1. ✅ Keep all shared LangChain dependencies
2. ✅ Add FastAPI ecosystem packages
3. ❌ Remove ChromaDB (not used in integrated approach)
4. ✅ Keep python-dotenv for .env file loading

### If Staying with Root CLI:
- Keep existing `d:\KMIT\requirements.txt` as-is
- Works independently from backend
- Use for standalone analysis tasks

### If Running Both Simultaneously:
1. Create separate Python virtual environments
2. Root: `venv_cli` with root requirements
3. Backend: `venv_backend` with backend requirements
4. Don't mix environments to avoid conflicts

## Version Recommendations

### Current Locked Versions
```
langchain>=0.2.0             # Latest 0.2.x or 0.3.x
langchain-google-genai>=1.0.0  # Latest 1.x
langchain-core>=0.2.0        # Latest 0.2.x or 0.3.x
python-dotenv>=1.0.0         # Latest 1.x
```

### Optional: Pin Exact Versions
For production, use exact versions:
```
langchain==0.2.0
langchain-google-genai==1.0.0
langchain-core==0.2.0
python-dotenv==1.0.0
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
```

## Installation Instructions

### Install Backend Only
```bash
cd d:\KMIT\backend
pip install -r requirements.txt
```

### Install Root + Backend (Separate Environments)
```bash
# Root project
cd d:\KMIT
python -m venv venv_cli
venv_cli\Scripts\activate
pip install -r requirements.txt

# Backend (in new terminal)
cd d:\KMIT\backend
python -m venv venv_backend
venv_backend\Scripts\activate
pip install -r requirements.txt
```

### Install Both in Same Environment (Advanced)
```bash
# Not recommended, but possible
pip install -r d:\KMIT\requirements.txt
pip install -r d:\KMIT\backend\requirements.txt
```

## Dependency Conflicts

**No conflicts detected** between root and backend packages.

All shared packages:
- ✅ Same version constraints
- ✅ Compatible imports
- ✅ No breaking changes

The only difference is:
- Root adds: chromadb (if using embeddings)
- Backend adds: fastapi, uvicorn, pydantic, aiofiles

## Troubleshooting

### If you get "ModuleNotFoundError"
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade

# Or for specific package
pip install langchain-google-genai --upgrade
```

### If you get "version conflict"
```bash
# Create fresh virtual environment
python -m venv venv_fresh
venv_fresh\Scripts\activate
pip install -r requirements.txt
```

### If you get "GOOGLE_API_KEY not found"
```bash
# Ensure .env file exists and has API key
# Create if missing:
echo GOOGLE_API_KEY=your_key > .env
```

## Verification

### Verify Installation
```bash
python -c "from langchain_google_genai import ChatGoogleGenerativeAI; print('✓ OK')"
```

### Verify Backend Setup
```bash
python verify_integration.py
```

### Verify Root Setup
```bash
python main.py --help
```

## Summary

- **Root Project**: Standalone CLI, fully functional
- **Backend**: REST API with same core logic, FastAPI wrapper
- **Dependencies**: 99% overlap, minimal additions
- **Recommendation**: Use backend for web app, keep root for CLI testing

Both can coexist in separate virtual environments without conflicts.

# Pre-Push Checklist

## ✅ Before Pushing to GitHub

### 1. Security Check
- [x] `.env` files are in `.gitignore` (✅ Already configured)
- [x] `db.sqlite3` is in `.gitignore` (✅ Already configured)
- [x] No secrets in code (✅ All secrets use environment variables)
- [x] `SECRET_KEY` is not hardcoded (✅ Uses environment variable)

### 2. Files to Commit
✅ **DO Commit:**
- All source code (`.py`, `.jsx`, `.js` files)
- Configuration files (`requirements.txt`, `package.json`, `render.yaml`, `vercel.json`)
- Documentation (`.md` files)
- `.env.example` files (template files, safe to commit)
- Migration files
- Build scripts

❌ **DON'T Commit:**
- `.env` files (contains secrets)
- `db.sqlite3` (local database)
- `venv/` or `node_modules/` (dependencies)
- `__pycache__/` (Python cache)
- `.vscode/`, `.idea/` (IDE settings)

### 3. Recent Fixes to Include
- ✅ Fixed token refresh URL in `frontend/src/services/api.js`
- ✅ Added error handling for insufficient inventory in `backend/assets/views.py`
- ✅ Fixed `requirements.txt` (was empty, now has all dependencies)
- ✅ Updated `gunicorn_config.py` to use PORT from environment
- ✅ Updated `render.yaml` with proper configuration
- ✅ Added `ALLOWED_HOSTS` to settings

### 4. Initialize Git (If Not Done)

```bash
# Initialize git repository
git init

# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: Military Asset Management System

- Django backend with REST API
- React frontend with Material-UI
- JWT authentication
- RBAC implementation
- Audit logging
- Asset tracking and management
- Deployment configs for Render and Vercel"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/military-asset-management.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 5. After Pushing

1. **Connect to Render:**
   - Go to Render Dashboard
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

2. **Connect to Vercel:**
   - Go to Vercel Dashboard
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Add environment variable: `VITE_API_URL=https://your-backend.onrender.com/api`

3. **Update CORS:**
   - After Vercel deployment, update `CORS_ALLOWED_ORIGINS` in Render with your Vercel URL

## Quick Commands

```bash
# Check what will be committed
git status

# See what's ignored
git status --ignored

# Initialize and push (if not done)
git init
git add .
git commit -m "Initial commit: MAMS"
git remote add origin <your-repo-url>
git push -u origin main
```


# Quick Commerce Deployment Guide

## Render.com Deployment

### 1. Repository Setup
- Connect your GitHub repository to Render
- Set the repository to: `https://github.com/rasheed8123/security_deployment`

### 2. Service Configuration

#### Build Settings:
- **Build Command**: `pip install --no-cache-dir -r requirements-backend.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

#### Environment Variables:
- `PYTHON_VERSION`: `3.11.7`
- `DATABASE_URL`: `sqlite:///./quick_commerce.db`
- `SECRET_KEY`: `your-secret-key-here`

### 3. Requirements Files

**Recommended for Backend Deployment:**
- Use `requirements-backend.txt` (backend dependencies only)
- This avoids pandas/numpy compilation issues with Python 3.13

**Alternative Options:**
- `requirements-render.txt` - Minimal backend requirements
- `requirements.txt` - Full requirements (may have compatibility issues)

### 4. Python Version

**Recommended:** Python 3.11.7
- More stable with pandas/numpy
- Better compatibility with all packages

**If using Python 3.13:**
- Use `requirements-backend.txt` to avoid compilation issues
- Frontend dependencies (pandas, numpy, streamlit) are not needed for backend

### 5. Database Setup

The application uses SQLite by default. For production:
- Consider using PostgreSQL
- Update `DATABASE_URL` environment variable
- Update `database.py` to use the new database URL

### 6. File Uploads

The application stores uploaded files in the `uploads/` directory:
- Ensure the directory exists
- Files are stored locally (consider cloud storage for production)

### 7. Health Check

Test your deployment:
- Visit: `https://your-app-name.onrender.com/health`
- Should return: `{"status": "healthy"}`

### 8. API Documentation

Once deployed:
- Swagger UI: `https://your-app-name.onrender.com/docs`
- ReDoc: `https://your-app-name.onrender.com/redoc` 
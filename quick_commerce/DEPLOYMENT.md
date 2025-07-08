# Quick Commerce Deployment Guide

## Render.com Deployment

### 1. Repository Setup
- Connect your GitHub repository to Render
- Set the repository to: `https://github.com/rasheed8123/security_deployment`

### 2. Service Configuration

#### Build Settings:
- **Build Command**: `pip install --no-cache-dir -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

#### Environment Variables:
- `PYTHON_VERSION`: `3.11.7`
- `DATABASE_URL`: `sqlite:///./quick_commerce.db`
- `SECRET_KEY`: `your-secret-key-here`

### 3. Alternative Requirements (if needed)

If you encounter Pillow installation issues, use `requirements-render.txt`:
- Rename `requirements-render.txt` to `requirements.txt`
- This version excludes Pillow (only needed for frontend)

### 4. Database Setup

The application uses SQLite by default. For production:
- Consider using PostgreSQL
- Update `DATABASE_URL` environment variable
- Update `database.py` to use the new database URL

### 5. File Uploads

The application stores uploaded files in the `uploads/` directory:
- Ensure the directory exists
- Files are stored locally (consider cloud storage for production)

### 6. Health Check

Test your deployment:
- Visit: `https://your-app-name.onrender.com/health`
- Should return: `{"status": "healthy"}`

### 7. API Documentation

Once deployed:
- Swagger UI: `https://your-app-name.onrender.com/docs`
- ReDoc: `https://your-app-name.onrender.com/redoc` 
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas, crud, utils, auth, dependencies, database, security, exceptions

app = FastAPI(
    title="Secure User Authentication API",
    description="A secure authentication system with JWT tokens and role-based access control",
    version="1.0.0"
)

# Setup security middleware
security.setup_security_middleware(app)

# Exception handlers
app.add_exception_handler(exceptions.RequestValidationError, exceptions.validation_exception_handler)
app.add_exception_handler(exceptions.StarletteHTTPException, exceptions.http_exception_handler)
app.add_exception_handler(Exception, exceptions.general_exception_handler)

# Create DB tables
@app.on_event("startup")
def on_startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.on_event("shutdown")
def on_shutdown():
    # Cleanup expired tokens on shutdown
    db = database.SessionLocal()
    try:
        crud.cleanup_expired_tokens(db)
    finally:
        db.close()

@app.get("/health", response_model=schemas.HealthCheck)
def health_check():
    return schemas.HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@app.post("/auth/register", response_model=schemas.UserOut)
@security.registration_rate_limit()
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    if not utils.validate_password_strength(user.password):
        raise exceptions.ValidationError("Password too weak (min 8 chars, 1 special char)")
    
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except ValueError as e:
        raise exceptions.ValidationError(str(e))

@app.post("/auth/login")
@security.login_rate_limit()
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise exceptions.AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        raise exceptions.AuthenticationError("Account is deactivated")
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/auth/refresh")
@security.login_rate_limit()
def refresh_token(refresh_data: schemas.TokenRefresh, db: Session = Depends(dependencies.get_db)):
    payload = auth.verify_refresh_token(refresh_data.refresh_token, db)
    if not payload:
        raise exceptions.AuthenticationError("Invalid refresh token")
    
    username = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    if not user or not user.is_active:
        raise exceptions.AuthenticationError("User not found or inactive")
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
def logout(logout_data: schemas.LogoutRequest, db: Session = Depends(dependencies.get_db)):
    # Blacklist the token
    crud.blacklist_token(db, logout_data.token)
    return {"detail": "Successfully logged out"}

@app.post("/auth/forgot-password")
@security.password_reset_rate_limit()
def forgot_password(reset_request: schemas.PasswordResetRequest, db: Session = Depends(dependencies.get_db)):
    reset_token = crud.create_password_reset_token(db, reset_request.email)
    if reset_token:
        # In a real application, send email with reset token
        return {"detail": "Password reset token sent to email"}
    else:
        # Don't reveal if email exists or not
        return {"detail": "If email exists, password reset token sent"}

@app.post("/auth/reset-password")
@security.password_reset_rate_limit()
def reset_password(reset_data: schemas.PasswordReset, db: Session = Depends(dependencies.get_db)):
    if not utils.validate_password_strength(reset_data.new_password):
        raise exceptions.ValidationError("Password too weak (min 8 chars, 1 special char)")
    
    user = crud.reset_password(db, reset_data.token, reset_data.new_password)
    if not user:
        raise exceptions.ValidationError("Invalid or expired reset token")
    
    return {"detail": "Password successfully reset"}

@app.get("/auth/me", response_model=schemas.UserOut)
@security.general_rate_limit()
def get_me(current_user: models.User = Depends(dependencies.get_current_active_user)):
    return current_user

@app.get("/users", response_model=list[schemas.UserOut])
@security.general_rate_limit()
def get_users(db: Session = Depends(dependencies.get_db), admin: models.User = Depends(dependencies.require_admin)):
    return crud.get_users(db)

@app.put("/users/{user_id}/role", response_model=schemas.UserOut)
@security.general_rate_limit()
def update_role(user_id: int, role_update: schemas.RoleUpdate, db: Session = Depends(dependencies.get_db), admin: models.User = Depends(dependencies.require_admin)):
    user = crud.update_user_role(db, user_id, role_update.role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
@security.general_rate_limit()
def delete_user(user_id: int, db: Session = Depends(dependencies.get_db), admin: models.User = Depends(dependencies.require_admin)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response 
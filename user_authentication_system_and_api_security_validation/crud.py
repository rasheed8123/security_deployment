from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, utils, security

# Get user by username

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Sanitize inputs
    username = security.sanitize_input(user.username)
    email = security.sanitize_input(user.email)
    
    # Validate inputs
    if not security.validate_username(username):
        raise ValueError("Invalid username format")
    if not security.validate_email(email):
        raise ValueError("Invalid email format")
    
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, role: str):
    user = get_user(db, user_id)
    if user:
        user.role = security.sanitize_input(role)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

def create_password_reset_token(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    reset_token = security.generate_secure_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    return reset_token

def reset_password(db: Session, token: str, new_password: str):
    user = db.query(models.User).filter(
        models.User.reset_token == token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return None
    
    user.hashed_password = utils.hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return user

def blacklist_token(db: Session, token: str):
    # Decode token to get expiration
    try:
        from jose import jwt
        payload = jwt.decode(token, "your_secret_key_here", algorithms=["HS256"])
        expires_at = datetime.fromtimestamp(payload["exp"])
    except:
        expires_at = datetime.utcnow() + timedelta(hours=1)
    
    blacklisted_token = models.TokenBlacklist(
        token=token,
        expires_at=expires_at
    )
    db.add(blacklisted_token)
    db.commit()
    return blacklisted_token

def is_token_blacklisted(db: Session, token: str):
    blacklisted = db.query(models.TokenBlacklist).filter(
        models.TokenBlacklist.token == token
    ).first()
    return blacklisted is not None

def cleanup_expired_tokens(db: Session):
    """Clean up expired blacklisted tokens"""
    expired_tokens = db.query(models.TokenBlacklist).filter(
        models.TokenBlacklist.expires_at < datetime.utcnow()
    ).all()
    
    for token in expired_tokens:
        db.delete(token)
    db.commit()
    return len(expired_tokens) 
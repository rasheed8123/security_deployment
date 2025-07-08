from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class RoleUpdate(BaseModel):
    role: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: constr(min_length=8)

class TokenRefresh(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    token: str

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0" 
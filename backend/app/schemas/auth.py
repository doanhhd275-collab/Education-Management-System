"""
Schemas cho Authentication: Login request và Token response.
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int = 3600        # giây — 1 tiếng


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"

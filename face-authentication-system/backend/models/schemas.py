"""
Pydantic request/response schemas used by the FastAPI routes.
"""
from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    full_name: str = Field(..., min_length=1, max_length=64)
    image: str = Field(..., description="Base64 data-URL of the captured face image")


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_uuid: Optional[str] = None
    username: Optional[str] = None


class AuthenticateRequest(BaseModel):
    image: str = Field(..., description="Base64 data-URL of the captured face image")


class AuthenticateResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    confidence: Optional[float] = None


class FaceCheckResponse(BaseModel):
    face_detected: bool
    box: Optional[list] = None


class UserResponse(BaseModel):
    user_uuid: str
    username: str
    full_name: str
    created_at: str


class DeleteResponse(BaseModel):
    success: bool
    message: str

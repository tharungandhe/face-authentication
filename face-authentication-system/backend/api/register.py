from fastapi import APIRouter, HTTPException

from models.schemas import RegisterRequest, RegisterResponse
from services.authentication import RegistrationError, register_user
from utils.image_utils import base64_to_image

router = APIRouter(prefix="/api", tags=["registration"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    try:
        image_bgr = base64_to_image(payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = register_user(payload.username, payload.full_name, image_bgr)
    except RegistrationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RegisterResponse(
        success=True,
        message=f"User '{result['username']}' registered successfully.",
        user_uuid=result["user_uuid"],
        username=result["username"],
    )

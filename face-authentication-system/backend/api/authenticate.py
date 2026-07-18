from fastapi import APIRouter, HTTPException

from models.schemas import AuthenticateRequest, AuthenticateResponse, FaceCheckResponse
from services.authentication import authenticate_user
from services.face_detector import has_face
from utils.image_utils import base64_to_image

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/authenticate", response_model=AuthenticateResponse)
def authenticate(payload: AuthenticateRequest):
    try:
        image_bgr = base64_to_image(payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = authenticate_user(image_bgr)

    return AuthenticateResponse(
        success=result.success,
        message=result.message,
        username=result.username,
        full_name=result.full_name,
        confidence=result.confidence,
    )


@router.post("/face-check", response_model=FaceCheckResponse)
def face_check(payload: AuthenticateRequest):
    """Lightweight endpoint the UI polls to show the
    'Face detected. Ready to authenticate.' status live."""
    try:
        image_bgr = base64_to_image(payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    box = has_face(image_bgr)
    return FaceCheckResponse(face_detected=box is not None, box=list(box) if box else None)

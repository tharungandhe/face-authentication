"""
Orchestrates the register / authenticate flows by wiring together face
detection, embedding extraction, the vector store, and the SQLite user
table.
"""
import uuid

import numpy as np

from database import sqlite_db
from services import vector_store
from services.face_detector import FaceDetectionError, detect_single_face
from services.face_embedding import get_embedding
from utils.config import MATCH_DISTANCE_THRESHOLD
from utils.image_utils import save_face_snapshot


class RegistrationError(Exception):
    pass


class AuthenticationResult:
    def __init__(self, success: bool, username: str = None, full_name: str = None,
                 confidence: float = None, message: str = ""):
        self.success = success
        self.username = username
        self.full_name = full_name
        self.confidence = confidence
        self.message = message


def register_user(username: str, full_name: str, image_bgr: np.ndarray) -> dict:
    username = username.strip()
    full_name = full_name.strip()

    if not username or not full_name:
        raise RegistrationError("Username and full name are required.")

    if sqlite_db.username_exists(username):
        raise RegistrationError(f"Username '{username}' is already registered.")

    try:
        detected = detect_single_face(image_bgr)
    except FaceDetectionError as exc:
        raise RegistrationError(str(exc)) from exc

    embedding = get_embedding(detected.crop_bgr)

    # Guard against re-registering an already-enrolled face under a new name.
    existing = vector_store.find_closest_match(embedding)
    if existing and existing["distance"] <= MATCH_DISTANCE_THRESHOLD:
        raise RegistrationError(
            f"This face already appears to be registered as '{existing['username']}'."
        )

    user_uuid = str(uuid.uuid4())
    face_image_path = save_face_snapshot(detected.crop_bgr, username)

    sqlite_db.create_user(user_uuid, username, full_name, face_image_path)
    vector_store.add_embedding(user_uuid, username, full_name, embedding)

    return {"user_uuid": user_uuid, "username": username, "full_name": full_name}


def authenticate_user(image_bgr: np.ndarray) -> AuthenticationResult:
    try:
        detected = detect_single_face(image_bgr)
    except FaceDetectionError as exc:
        return AuthenticationResult(success=False, message=str(exc))

    embedding = get_embedding(detected.crop_bgr)
    match = vector_store.find_closest_match(embedding)

    if match is None:
        return AuthenticationResult(success=False, message="No registered faces to compare against.")

    confidence = max(0.0, 1.0 - match["distance"])

    if match["distance"] <= MATCH_DISTANCE_THRESHOLD:
        return AuthenticationResult(
            success=True,
            username=match["username"],
            full_name=match["full_name"],
            confidence=round(confidence * 100, 1),
            message="Face recognized.",
        )

    return AuthenticationResult(
        success=False,
        confidence=round(confidence * 100, 1),
        message="Face not recognized. Access denied.",
    )

"""
Helpers for converting between base64 data-URLs (sent from the browser
webcam capture) and OpenCV/numpy image arrays.
"""
import base64
import re
import uuid
from pathlib import Path

import cv2
import numpy as np

from utils.config import REGISTERED_FACES_DIR

_DATA_URL_RE = re.compile(r"^data:image/\w+;base64,")


def base64_to_image(data_url: str) -> np.ndarray:
    """Decode a base64 data-URL (e.g. from <canvas>.toDataURL()) into a BGR
    numpy image, ready for OpenCV processing."""
    if not data_url:
        raise ValueError("No image data provided.")

    cleaned = _DATA_URL_RE.sub("", data_url)
    try:
        raw_bytes = base64.b64decode(cleaned)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Could not decode base64 image data.") from exc

    np_arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Uploaded data is not a valid image.")
    return image


def save_face_snapshot(image: np.ndarray, username: str) -> str:
    """Persist a copy of the captured face image to disk for auditing /
    debugging and return the saved file path."""
    Path(REGISTERED_FACES_DIR).mkdir(parents=True, exist_ok=True)
    filename = f"{username}_{uuid.uuid4().hex[:8]}.jpg"
    full_path = Path(REGISTERED_FACES_DIR) / filename
    cv2.imwrite(str(full_path), image)
    return str(full_path)

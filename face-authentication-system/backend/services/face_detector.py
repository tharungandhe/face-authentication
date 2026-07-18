"""
Face detection service.

Uses OpenCV's built-in Haar Cascade classifier. This ships with
opencv-python so no external model download is required, which keeps the
service self-contained and fast to boot.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

from utils.config import MIN_FACE_SIZE

_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)


@dataclass
class DetectedFace:
    box: Tuple[int, int, int, int]  # x, y, w, h
    crop_bgr: np.ndarray


class FaceDetectionError(Exception):
    """Raised when no face (or more than one face) is found in an image."""


def _detect_boxes(image_bgr: np.ndarray) -> List[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = _face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=MIN_FACE_SIZE,
    )
    return [tuple(map(int, box)) for box in faces]


def detect_single_face(image_bgr: np.ndarray) -> DetectedFace:
    """Detect exactly one face in the given image.

    Raises FaceDetectionError if zero or multiple faces are found, since
    both cases make registration / authentication ambiguous.
    """
    boxes = _detect_boxes(image_bgr)

    if len(boxes) == 0:
        raise FaceDetectionError("No face detected. Please align your face in the frame.")
    if len(boxes) > 1:
        raise FaceDetectionError("Multiple faces detected. Please ensure only one face is visible.")

    x, y, w, h = boxes[0]
    crop = image_bgr[y : y + h, x : x + w]
    return DetectedFace(box=(x, y, w, h), crop_bgr=crop)


def has_face(image_bgr: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Lightweight check used by a 'liveness ping' style endpoint - returns
    the first bounding box found, or None."""
    boxes = _detect_boxes(image_bgr)
    return boxes[0] if boxes else None

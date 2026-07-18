"""
Face embedding service.

Converts a cropped face image into a fixed-length numeric vector ("face
embedding") that can be stored and compared in the vector database.

We use a Histogram of Oriented Gradients (HOG) descriptor over a
normalized grayscale crop. This needs no pretrained neural network /
external download, is deterministic, and is fast enough to run on CPU in
real time - a good fit for a self-contained demo/reference system.
"""
import cv2
import numpy as np
from skimage.feature import hog

from utils.config import (
    FACE_IMAGE_SIZE,
    HOG_CELLS_PER_BLOCK,
    HOG_ORIENTATIONS,
    HOG_PIXELS_PER_CELL,
)


def _preprocess(face_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, FACE_IMAGE_SIZE, interpolation=cv2.INTER_AREA)
    equalized = cv2.equalizeHist(resized)
    normalized = equalized.astype("float32") / 255.0
    return normalized


def get_embedding(face_bgr: np.ndarray) -> np.ndarray:
    """Return a normalized 1-D float32 embedding vector for a face crop."""
    processed = _preprocess(face_bgr)

    features = hog(
        processed,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        block_norm="L2-Hys",
        feature_vector=True,
    ).astype("float32")

    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm

    return features

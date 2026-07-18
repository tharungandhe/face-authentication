"""
Basic tests for the face detection -> embedding -> vector-store pipeline.

Run from the backend/ directory so the `services`/`database`/`utils`
packages resolve:

    cd backend && pytest ../tests -v
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from services.face_detector import FaceDetectionError, detect_single_face  # noqa: E402
from services.face_embedding import get_embedding  # noqa: E402


def _blank_image():
    return np.zeros((300, 300, 3), dtype=np.uint8)


def test_no_face_raises():
    with pytest.raises(FaceDetectionError):
        detect_single_face(_blank_image())


def test_embedding_is_normalized_and_fixed_length():
    # A synthetic 128x128 "face-ish" crop just to exercise the embedding math.
    crop = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    emb = get_embedding(crop)
    assert emb.ndim == 1
    assert emb.dtype == np.float32
    norm = np.linalg.norm(emb)
    assert 0.99 <= norm <= 1.01  # unit-normalized


def test_embedding_is_deterministic():
    crop = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    emb1 = get_embedding(crop)
    emb2 = get_embedding(crop)
    assert np.allclose(emb1, emb2)

"""
Central configuration for the Face Authentication System.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Storage locations -------------------------------------------------
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "backend" / "users.db"))
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "vector_db" / "chroma_storage"))
REGISTERED_FACES_DIR = os.getenv("REGISTERED_FACES_DIR", str(BASE_DIR / "registered_faces"))

# --- Face detection / embedding -----------------------------------------
# Fixed size the detected face crop is normalized to before feature extraction.
FACE_IMAGE_SIZE = (128, 128)

# HOG descriptor parameters (scikit-image). These are tuned to produce a
# fixed-length feature vector that behaves as our face "embedding".
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (16, 16)
HOG_CELLS_PER_BLOCK = (2, 2)

# Minimum face size (in pixels) the Haar cascade will accept as a real face.
MIN_FACE_SIZE = (80, 80)

# --- Authentication -------------------------------------------------------
# Cosine-distance threshold. Chroma returns distance = 1 - cosine_similarity,
# so smaller is "more similar". Empirically tuned for the HOG embedding.
MATCH_DISTANCE_THRESHOLD = float(os.getenv("MATCH_DISTANCE_THRESHOLD", "0.35"))

# --- API -------------------------------------------------------------------
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = ["*"]

# Chroma collection name
FACE_COLLECTION_NAME = "faces"

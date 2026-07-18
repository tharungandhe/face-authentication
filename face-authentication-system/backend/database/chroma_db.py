"""
ChromaDB client bootstrap. A single persistent client/collection is shared
across the app for storing face embeddings.
"""
import chromadb

from utils.config import CHROMA_DB_PATH, FACE_COLLECTION_NAME

_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

_collection = _client.get_or_create_collection(
    name=FACE_COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


def get_face_collection():
    return _collection

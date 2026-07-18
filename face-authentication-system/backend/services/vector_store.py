"""
Thin service layer over the ChromaDB collection: add, query, and delete
face embedding vectors.
"""
from typing import List, Optional

import numpy as np

from database.chroma_db import get_face_collection


def add_embedding(user_uuid: str, username: str, full_name: str, embedding: np.ndarray) -> None:
    collection = get_face_collection()
    collection.add(
        ids=[user_uuid],
        embeddings=[embedding.tolist()],
        metadatas=[{"username": username, "full_name": full_name}],
    )


def find_closest_match(embedding: np.ndarray, n_results: int = 1) -> Optional[dict]:
    """Return the single closest match as
    {"user_uuid", "username", "full_name", "distance"} or None if the
    collection is empty."""
    collection = get_face_collection()
    if collection.count() == 0:
        return None

    result = collection.query(
        query_embeddings=[embedding.tolist()],
        n_results=min(n_results, collection.count()),
    )

    if not result["ids"] or not result["ids"][0]:
        return None

    best_id = result["ids"][0][0]
    best_meta = result["metadatas"][0][0]
    best_distance = result["distances"][0][0]

    return {
        "user_uuid": best_id,
        "username": best_meta.get("username"),
        "full_name": best_meta.get("full_name"),
        "distance": float(best_distance),
    }


def delete_embedding(user_uuid: str) -> None:
    collection = get_face_collection()
    try:
        collection.delete(ids=[user_uuid])
    except Exception:
        # Nothing to delete / id not present - safe to ignore.
        pass

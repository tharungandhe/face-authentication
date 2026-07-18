"""
Domain model representing a registered user (non-biometric metadata only -
the face embedding itself lives in the vector store).
"""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    user_uuid: str
    username: str
    full_name: str
    face_image_path: str
    created_at: str

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            id=row["id"],
            user_uuid=row["user_uuid"],
            username=row["username"],
            full_name=row["full_name"],
            face_image_path=row["face_image_path"],
            created_at=row["created_at"],
        )

from typing import List

from fastapi import APIRouter, HTTPException

from database import sqlite_db
from models.schemas import DeleteResponse, UserResponse
from services import vector_store

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users", response_model=List[UserResponse])
def list_users():
    rows = sqlite_db.list_users()
    return [
        UserResponse(
            user_uuid=row["user_uuid"],
            username=row["username"],
            full_name=row["full_name"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.delete("/users/{user_uuid}", response_model=DeleteResponse)
def delete_user(user_uuid: str):
    deleted = sqlite_db.delete_user(user_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")

    vector_store.delete_embedding(user_uuid)
    return DeleteResponse(success=True, message="User deleted successfully.")

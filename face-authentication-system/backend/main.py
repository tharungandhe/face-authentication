"""
Face Authentication System - FastAPI entrypoint.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Serves the JSON API under /api/* and the static frontend (the mockup UI)
at the root path.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import authenticate, register, users
from utils.config import CORS_ORIGINS

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Face Authentication System",
    description="Secure. Reliable. Seamless. Face-based login and registration API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(register.router)
app.include_router(authenticate.router)
app.include_router(users.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "face-authentication-system"}


# Serve the frontend (index.html, css, js) as static files.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

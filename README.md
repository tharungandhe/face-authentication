Face Authentication System

Secure. Reliable. Seamless. A browser-based face login and registration
system: capture a face via webcam, register it, and log back in with your
face instead of a password.

## How it works

```
Browser (camera capture)
        │  base64 JPEG frame
        ▼
FastAPI backend  ── face_detector.py   (OpenCV Haar Cascade: locate the face)
                 ── face_embedding.py  (HOG descriptor: turn the face into a vector)
                 ── vector_store.py    (ChromaDB: store / search vectors by similarity)
                 ── sqlite_db.py       (SQLite: username, full name, metadata)
```

- **Detection**: OpenCV's Haar Cascade classifier finds the face bounding box.
- **Embedding**: the cropped, normalized face is converted into a fixed-length
  Histogram-of-Oriented-Gradients (HOG) feature vector — a lightweight,
  dependency-free stand-in for a deep face-recognition embedding.
- **Matching**: on login, the new vector is compared against every stored
  vector in ChromaDB using cosine distance. The closest match under
  `MATCH_DISTANCE_THRESHOLD` is accepted.
- **Storage split**: biometric vectors live only in the vector DB;
  human-readable profile data (username, full name) lives in SQLite, linked
  by a UUID.

> This project is a clear, fully self-contained reference implementation
> (no external model downloads, no GPU needed). For production-grade
> accuracy, swap `face_embedding.py` for a deep embedding model (e.g. a
> pretrained FaceNet/ArcFace ONNX model) — the rest of the pipeline
> (detection → embedding → vector store → auth) stays the same.

## Project structure

```
face-authentication-system/
├── backend/
│   ├── main.py                 FastAPI app entrypoint
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/                    HTTP route handlers
│   │   ├── register.py
│   │   ├── authenticate.py
│   │   └── users.py
│   ├── services/                Core logic
│   │   ├── face_detector.py
│   │   ├── face_embedding.py
│   │   ├── vector_store.py
│   │   └── authentication.py
│   ├── database/
│   │   ├── chroma_db.py
│   │   └── sqlite_db.py
│   ├── models/
│   │   ├── user.py
│   │   └── schemas.py
│   └── utils/
│       ├── image_utils.py
│       └── config.py
├── frontend/
│   ├── index.html               Combined login + registration page
│   ├── login.html
│   ├── register.html
│   ├── css/style.css
│   └── js/
│       ├── api.js
│       ├── login.js
│       └── register.js
├── vector_db/chroma_storage/     ChromaDB persistent storage
├── registered_faces/             Saved face-crop snapshots
├── tests/
├── .env
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Running locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in a browser that has webcam access. The
FastAPI app serves the frontend directly, so the API and UI share one origin
(no CORS setup needed for local dev).

## Running with Docker

```bash
docker compose up --build
```

Then visit **http://localhost:8000**.

## API reference

| Method | Endpoint             | Description                                   |
|--------|-----------------------|------------------------------------------------|
| POST   | `/api/register`       | Register a new user (`username`, `full_name`, `image`) |
| POST   | `/api/authenticate`   | Authenticate a face (`image`) → matched user or denial |
| POST   | `/api/face-check`     | Lightweight "is a face visible right now" check, used for the live UI status |
| GET    | `/api/users`          | List all registered users                      |
| DELETE | `/api/users/{uuid}`   | Remove a user and their stored face vector      |
| GET    | `/api/health`         | Health check                                    |

All image payloads are base64 data-URLs, e.g. the output of
`<canvas>.toDataURL("image/jpeg")` in the browser.

## Configuration

Environment variables (see `.env`):

| Variable                    | Default                       | Meaning                                  |
|------------------------------|--------------------------------|-------------------------------------------|
| `MATCH_DISTANCE_THRESHOLD`  | `0.35`                         | Max cosine distance accepted as a match  |
| `SQLITE_DB_PATH`            | `backend/users.db`             | SQLite file location                     |
| `CHROMA_DB_PATH`            | `vector_db/chroma_storage`     | ChromaDB persistent storage directory    |
| `REGISTERED_FACES_DIR`      | `registered_faces`             | Where face-crop snapshots are saved      |

## Notes on privacy

Registered face images and vectors are stored locally under `registered_faces/`
and `vector_db/`. Nothing is sent to a third party. Delete a user via
`DELETE /api/users/{uuid}` to remove both their profile and biometric vector.

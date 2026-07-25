# CartoonVerse

CartoonVerse is a fullstack app for classical cartoonization of images and video, plus rule-based emoji suggestions for facial expressions. The backend is modular so the image pipeline, video queue, and emoji matcher can be worked on independently.

## Implemented API

- `GET /` and `GET /health`
- `POST /cartoonize/image`
- `POST /cartoonize/video`
- `GET /cartoonize/video/status/{job_id}`
- `POST /suggest-emoji`

## Local setup

1. Create and activate the Conda environment:

   ```bash
   conda create -n cartoonizer python=3.11 -y
   conda activate cartoonizer
   ```

2. Install backend dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Create your local environment file:

   ```bash
   copy .env.example .env
   ```

5. Run the backend API:

   ```bash
   uvicorn app.main:app --app-dir backend --reload
   ```

6. Run the frontend dev server:

   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```

7. Run the backend tests:

   ```bash
   cd backend
   python -m pytest
   ```

## Docker Compose

Use Docker Compose for the full stack once Docker is installed:

```bash
docker compose up --build
```

Services started by compose:

- `backend` FastAPI app on port `8000`
- `worker` Celery worker for video jobs
- `redis` queue backend for Celery
- `frontend` Vite dev server on port `5173`

## Environment variables

Copy `.env.example` to `.env` and adjust values as needed.

- `REDIS_URL` controls the Celery broker/backend
- `MAX_UPLOAD_SIZE_MB` controls API upload limits
- `TEMP_DIR` controls the temporary job directory
- `VITE_API_BASE_URL` controls where the frontend sends requests

## Development notes

- The image cartoonization core lives under `backend/app/services/cartoonize/`.
- The emoji matcher lives under `backend/app/services/emoji/`.
- Video jobs are dispatched through Celery so the API stays responsive.
- The video pipeline cleans up temporary inputs and intermediates even when jobs fail.

# CartoonVerse

CartoonVerse is a fullstack app for classical cartoonization of images and video, plus rule-based emoji suggestions for facial expressions. The repo is organized so the backend, frontend, and worker pipeline can be built independently.

## Current scaffold

- FastAPI backend with `GET /` and `GET /health`
- Vite + React frontend shell
- Docker Compose wiring for backend, Redis, worker, and frontend

## Local setup

1. Create the Conda environment:

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

5. Run the backend:

   ```bash
   uvicorn app.main:app --app-dir backend --reload
   ```

6. Run the frontend:

   ```bash
   cd frontend
   npm run dev
   ```

## Docker Compose

Use Docker Compose for the full stack once you have Docker installed:

```bash
docker compose up --build
```

## Notes for the next stages

- The image cartoonization core will live under `backend/app/services/cartoonize/`.
- The emoji matching pipeline will live under `backend/app/services/emoji/`.
- Video processing will be added as Celery jobs so the API stays responsive.
# Cartoonization
Fullstack app that cartoonizes images/video using bilateral filtering, k-means color quantization, and optical-flow-based temporal smoothing — plus rule-based facial expression → emoji matching. No CNNs, no pretrained models.

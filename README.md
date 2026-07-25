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
Local FFmpeg requirement
------------------------
Video processing requires the `ffmpeg` system binary. The Docker images install `ffmpeg` automatically, but
if you run the backend on your host machine you must install `ffmpeg` yourself. Choose one of the options below
for your platform:

- Linux (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install ffmpeg -y
```

- macOS (Homebrew):

```bash
brew install ffmpeg
```

- Windows (winget):

```powershell
winget install --id=Gyan.FFmpeg -e
# or if you have Chocolatey
choco install ffmpeg -y
```

- Manual: download a release from https://ffmpeg.org/download.html and add the `ffmpeg` executable to your `PATH`.

After installing `ffmpeg`, verify it's available with:

```bash
ffmpeg -version
```

If `ffmpeg` is not present on the host, the Docker-based workflow will still work because the backend Dockerfile
installs `ffmpeg` inside the container.

Automated installer scripts
---------------------------
Two helper scripts are included to simplify installing `ffmpeg` for development.

- Windows PowerShell script: `scripts/install_ffmpeg_windows.ps1`
   - Usage (download+extract only):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_ffmpeg_windows.ps1
```

   - Usage (download+extract and add to user PATH):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_ffmpeg_windows.ps1 -AddToPath
```

- Unix shell script: `scripts/install_ffmpeg_unix.sh`
   - Usage:

```bash
bash scripts/install_ffmpeg_unix.sh
```

These scripts attempt a best-effort installation. Review the scripts before running them and ensure you trust the
network source for the download on Windows. If you prefer not to run install scripts, follow the manual instructions
above for your OS.
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

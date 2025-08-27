from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, uuid, os, traceback

app = FastAPI()

# CORS setup
frontend_url = os.environ.get("FRONTEND_URL", "*")  # Replace with your frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Request model
class ConvertRequest(BaseModel):
    url: str

# Root endpoint to test backend
@app.get("/")
async def root():
    return {"message": "Backend is alive"}

# Conversion endpoint (no trimming, enhanced error reporting)
@app.post("/convert")
async def convert(req: ConvertRequest):
    os.makedirs("temp", exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    temp_path = f"temp/{filename}"

    try:
        # Run yt-dlp and capture stdout/stderr
        result = subprocess.run(
            ["python3", "-m", "yt_dlp", "-x", "--audio-format", "mp3", "-o", temp_path, req.url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Optional: log stdout/stderr for debugging
        print("yt-dlp stdout:", result.stdout)
        print("yt-dlp stderr:", result.stderr)

        return {"filename": filename, "path": f"/{temp_path}"}

    except subprocess.CalledProcessError as e:
        # Return yt-dlp error output to frontend for debugging
        error_msg = f"yt-dlp failed with code {e.returncode}.\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=error_msg)

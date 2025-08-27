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
    start_time: float = 0
    end_time: float = 0

# Optional root endpoint to test backend
@app.get("/")
async def root():
    return {"message": "Backend is alive"}

# Conversion endpoint
@app.post("/convert")
async def convert(req: ConvertRequest):
    os.makedirs("temp", exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    temp_path = f"temp/{filename}"

    try:
        # Run yt-dlp via Python module to avoid PATH issues
        subprocess.run([
            "python3", "-m", "yt_dlp", "-x", "--audio-format", "mp3", "-o", temp_path, req.url
        ], check=True)

        # Optional trimming
        if req.end_time > req.start_time:
            trimmed_file = f"temp/trimmed_{filename}"
            subprocess.run([
                "ffmpeg", "-i", temp_path, "-ss", str(req.start_time),
                "-to", str(req.end_time), "-c", "copy", trimmed_file
            ], check=True)
            temp_path = trimmed_file

        return {"filename": filename, "path": f"/{temp_path}"}

    except subprocess.CalledProcessError as e:
        print("Conversion error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Conversion failed")

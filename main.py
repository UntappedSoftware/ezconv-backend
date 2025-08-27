from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, uuid, os

app = FastAPI()  # ← No extra arguments here

# CORS setup
frontend_url = os.environ.get("FRONTEND_URL", "*")  # Use "*" for testing, or your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # List of allowed origins
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConvertRequest(BaseModel):
    url: str
    start_time: float = 0
    end_time: float = 0

@app.post("/convert")
async def convert(req: ConvertRequest):
    os.makedirs("backend/temp", exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    temp_path = f"backend/temp/{filename}"
    try:
        subprocess.run([
            "yt-dlp", "-x", "--audio-format", "mp3", "-o", temp_path, req.url
        ], check=True)
        if req.end_time > req.start_time:
            trimmed_file = f"backend/temp/trimmed_{filename}"
            subprocess.run([
                "ffmpeg", "-i", temp_path, "-ss", str(req.start_time), "-to", str(req.end_time), "-c", "copy", trimmed_file
            ], check=True)
            temp_path = trimmed_file
        return {"filename": filename, "path": temp_path}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=400, detail="Conversion failed")

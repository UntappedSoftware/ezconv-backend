from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, uuid, os, traceback

app = FastAPI()

# CORS setup
frontend_url = os.environ.get("FRONTEND_URL", "*")  # set this in Render env vars
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
        # Run yt-dlp and capture output
        result = subprocess.run(
            ["python3", "-m", "yt_dlp", "-x", "--audio-format", "mp3", "-o", temp_path, req.url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("yt-dlp stdout:", result.stdout)
        print("yt-dlp stderr:", result.stderr)

        return {"filename": filename, "path": f"/{temp_path}"}

    except subprocess.CalledProcessError as e:
        error_msg = f"yt-dlp failed with code {e.returncode}.\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=error_msg)

# Temporary endpoint to check yt-dlp installation
@app.get("/yt-dlp-version")
async def yt_dlp_version():
    try:
        result = subprocess.run(
            ["python3", "-m", "yt_dlp", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return {"yt-dlp_version": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr.strip()}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import io
import json
from typing import Optional

from regions import REGIONS, DROPDOWNS
from sheets import append_record, get_all_records
from drive import upload_photo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


def compress_image(data: bytes, max_px: int = 800, quality: int = 70) -> bytes:
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_px:
        ratio = max_px / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


@app.get("/api/dropdowns")
def get_dropdowns():
    return DROPDOWNS


@app.get("/api/regions")
def get_regions():
    return REGIONS


@app.get("/api/records")
def get_records():
    return get_all_records()


@app.post("/api/records")
async def create_record(
    record_json: str = Form(...),
    photo1: Optional[UploadFile] = File(None),
    photo2: Optional[UploadFile] = File(None),
):
    record = json.loads(record_json)
    photo_urls = []

    for i, photo in enumerate([photo1, photo2], 1):
        if photo and photo.filename:
            raw = await photo.read()
            compressed = compress_image(raw)
            no = record.get("No.", "0000")
            url = upload_photo(compressed, f"photo_{no}_{i}.jpg")
            photo_urls.append(url)

    no = append_record(record, photo_urls)
    return {"status": "ok", "no": no}


@app.get("/")
def index():
    return FileResponse("../frontend/index.html")


@app.get("/record")
def record_page():
    return FileResponse("../frontend/record.html")

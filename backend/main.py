import sys
import os
import traceback

# Renderではリポジトリルートから起動するためパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")


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
    photo3: Optional[UploadFile] = File(None),
    photo4: Optional[UploadFile] = File(None),
):
    record = json.loads(record_json)
    # 写真は順番を保持した4要素リスト（Noneは空文字）
    photo_urls = []
    for i, photo in enumerate([photo1, photo2, photo3, photo4], 1):
        if photo and photo.filename:
            try:
                raw = await photo.read()
                compressed = compress_image(raw)
                rec_no = record.get("No.", "0000")
                url = upload_photo(compressed, f"photo_{rec_no}_{i}.jpg")
                photo_urls.append(url)
            except Exception as upload_err:
                traceback.print_exc()
                photo_urls.append("")  # アップロード失敗時は空文字で継続
        else:
            photo_urls.append("")  # 写真なしも空文字で位置を保持

    try:
        no = append_record(record, photo_urls)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "no": no}


@app.get("/record")
def record_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "record.html"))


@app.get("/list")
def list_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "list.html"))


@app.get("/manual")
def manual_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "manual.html"))


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

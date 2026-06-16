from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from auth import get_credentials
import io
import os

DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _service():
    return build("drive", "v3", credentials=get_credentials(SCOPES))


def upload_photo(image_bytes: bytes, filename: str) -> str:
    service = _service()
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype="image/jpeg")
    meta = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    f = service.files().create(body=meta, media_body=media, fields="id").execute()
    file_id = f["id"]
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()
    return f"https://drive.google.com/uc?id={file_id}"

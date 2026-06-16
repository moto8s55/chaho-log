from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "service_account.json")
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


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

# utils.py
import os
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads" / "music"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save an UploadFile to uploads/music and return the public path used by the API.
    Example return: "/uploads/music/abcd1234.jpg"
    """
    filename = upload_file.filename or ""
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    unique_name = f"{uuid4().hex}.{ext}"
    dest = UPLOAD_DIR / unique_name

    # read file bytes asynchronously from UploadFile
    contents = await upload_file.read()
    # write to disk (sync write is fine here; if you want fully async use aiofiles)
    with open(dest, "wb") as f:
        f.write(contents)

    # return a path that matches the StaticFiles mount in main.py
    return f"/uploads/music/{unique_name}"

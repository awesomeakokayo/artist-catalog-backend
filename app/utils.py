import io
from uuid import uuid4
from fastapi import UploadFile
from PIL import Image

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

async def save_upload_file_to_db(upload_file: UploadFile) -> tuple:
    """
    Process an uploaded file and return (bytes, mime, unique_name).
    You can then insert these into Neon DB.
    """
    filename = upload_file.filename or ""
    ext = filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    unique_name = f"{uuid4().hex}.{ext}"

    contents = await upload_file.read()

    img = Image.open(io.BytesIO(contents)).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=80)
    buf.seek(0)
    contents = buf.read()

    return contents, "image/webp", unique_name

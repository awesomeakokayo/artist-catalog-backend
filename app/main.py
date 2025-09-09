from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth, utils
from dotenv import load_dotenv
import os

load_dotenv()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Artist Music Platform API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ambitionsmiler.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads and static dirs
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "music")
os.makedirs(UPLOAD_DIR, exist_ok=True)

STATIC_DIR = os.path.join(BASE_DIR, "static")
LOGO_DIR = os.path.join(STATIC_DIR, "logos")
os.makedirs(LOGO_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

get_db = database.get_db
bearer_scheme = HTTPBearer()


def verify_token_header(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Verify Bearer JWT token in Authorization header."""
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


@app.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...)):
    """Admin login endpoint."""
    if not auth.authenticate_admin(username, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = auth.create_access_token({"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


# Public Endpoints

@app.get("/catalogs/")
def read_catalogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    objs = crud.get_catalogs(db, skip=skip, limit=limit)
    results = []
    for obj in objs:
        results.append({
            "id": obj.id,
            "title": obj.title,
            "cover_image": obj.cover_image or "/static/placeholder.png",
            "links": {
                "Spotify": {"url": obj.spotify_url, "logo": "/static/images/spotify.png"},
                "AppleMusic": {"url": obj.apple_music_url, "logo": "/static/images/apple.png"},
                "SoundCloud": {"url": obj.soundcloud_url, "logo": "/static/images/soundcloud.png"},
                "Boomplay": {"url": obj.boomplay_url, "logo": "/static/images/boomplay.png"},
                "Audiomack": {"url": obj.audiomack_url, "logo": "/static/images/audiomack.png"},
                "YouTubeMusic": {"url": obj.youtubemusic_url, "logo": "/static/images/youtubemusic.png"} if obj.youtubemusic_url else None,
            }
        })
    for r in results:
        r["links"] = {k: v for k, v in r["links"].items() if v and v["url"]}
    return results


@app.get("/catalogs/{catalog_id}")
def read_catalog(catalog_id: int, db: Session = Depends(get_db)):
    obj = crud.get_catalog(db, catalog_id=catalog_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Catalog not found")
    track = {
        "id": obj.id,
        "title": obj.title,
        "cover_image": obj.cover_image or "/static/placeholder.png",
        "description": obj.description,
        "links": {
            "Spotify": {"url": obj.spotify_url, "logo": "/static/images/spotify.png"},
            "AppleMusic": {"url": obj.apple_music_url, "logo": "/static/images/apple.png"},
            "Boomplay": {"url": obj.boomplay_url, "logo": "/static/images/boomplay.png"},
            "Audiomack": {"url": obj.audiomack_url, "logo": "/static/images/audiomack.png"},
            "YouTubeMusic": {"url": obj.youtubemusic_url, "logo": "/static/images/youtubemusic.png"},

        }
    }
    track["links"] = {k: v for k, v in track["links"].items() if v and v["url"]}
    return track


# Admin Endpoints

@app.post("/protected/catalogs/", response_model=schemas.CatalogOut)
async def protected_create_catalog(
    title: str = Form(...),
    description: str | None = Form(None),
    spotify_url: str | None = Form(None),
    apple_music_url: str | None = Form(None),
    audiomack_url: str | None = Form(None),
    boomplay_url: str | None = Form(None),
    youtubemusic_url: str | None = Form(None),
    soundcloud_url: str | None = Form(None),
    cover_image: UploadFile = File(None),
    payload=Depends(verify_token_header),
    db: Session = Depends(get_db)
):
    cover_path = None
    if cover_image:
        cover_path = await utils.save_upload_file(cover_image)
    catalog_in = schemas.CatalogCreate(
        title=title,
        description=description,
        spotify_url=spotify_url,
        apple_music_url=apple_music_url,
        audiomack_url=audiomack_url,
        boomplay_url=boomplay_url,
        youtubemusic_url=youtubemusic_url,
        soundcloud_url=soundcloud_url
    )
    return crud.create_catalog(db, catalog=catalog_in, cover_path=cover_path)


@app.put("/protected/catalogs/{catalog_id}", response_model=schemas.CatalogOut)
async def protected_update_catalog(
    catalog_id: int,
    title: str | None = Form(None),
    description: str | None = Form(None),
    spotify_url: str | None = Form(None),
    apple_music_url: str | None = Form(None),
    audiomack_url: str | None = Form(None),
    boomplay_url: str | None = Form(None),
    youtubemusic_url: str | None = Form(None),
    soundcloud_url: str | None = Form(None),
    cover_image: UploadFile = File(None),
    payload=Depends(verify_token_header),
    db: Session = Depends(get_db)
):
    db_obj = crud.get_catalog(db, catalog_id=catalog_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Catalog not found")
    cover_path = None
    if cover_image:
        cover_path = await utils.save_upload_file(cover_image)
    updates = {}
    if title is not None: updates["title"] = title
    if description is not None: updates["description"] = description
    if spotify_url is not None: updates["spotify_url"] = spotify_url
    if apple_music_url is not None: updates["apple_music_url"] = apple_music_url
    if audiomack_url is not None: updates["audiomack_url"] = audiomack_url
    if boomplay_url is not None: updates["boomplay_url"] = boomplay_url
    if youtubemusic_url is not None: updates["youtubemusic_url"] = youtubemusic_url
    if soundcloud_url is not None: updates["soundcloud_url"] = soundcloud_url

    update_schema = schemas.CatalogUpdate(**{**{k: getattr(db_obj, k) for k in updates.keys()}, **updates})
    return crud.update_catalog(db, db_obj, update_schema, cover_path=cover_path)


@app.delete("/protected/catalogs/{catalog_id}")
async def protected_delete_catalog(
    catalog_id: int,
    payload=Depends(verify_token_header),
    db: Session = Depends(get_db)
):
    db_obj = crud.get_catalog(db, catalog_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Catalog not found")
    crud.delete_catalog(db, catalog_id=catalog_id)
    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud, database, auth, utils

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Artist Music Platform API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ambitionsmiler.netlify.app", "https://ambitionsmiler.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

get_db = database.get_db

@app.get("/catalogs/")
def read_catalogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    objs = crud.get_catalogs(db, skip=skip, limit=limit)
    results = []
    for obj in objs:
        results.append({
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "cover_image": f"/catalogs/{obj.id}/image" if obj.cover_image_data else None,
            "links": {
                "Spotify": obj.spotify_url,
                "AppleMusic": obj.apple_music_url,
                "SoundCloud": obj.soundcloud_url,
                "Boomplay": obj.boomplay_url,
                "Audiomack": obj.audiomack_url,
                "YouTubeMusic": obj.youtubemusic_url,
            }
        })
    return results

@app.get("/catalogs/{catalog_id}")
def read_catalog(catalog_id: int, db: Session = Depends(get_db)):
    obj = crud.get_catalog(db, catalog_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return {
        "id": obj.id,
        "title": obj.title,
        "description": obj.description,
        "cover_image": f"/catalogs/{obj.id}/image" if obj.cover_image_data else None,
        "links": {
            "Spotify": obj.spotify_url,
            "AppleMusic": obj.apple_music_url,
            "SoundCloud": obj.soundcloud_url,
            "Boomplay": obj.boomplay_url,
            "Audiomack": obj.audiomack_url,
            "YouTubeMusic": obj.youtubemusic_url,
        }
    }

@app.get("/catalogs/{catalog_id}/image")
def get_catalog_image(catalog_id: int, db: Session = Depends(get_db)):
    catalog = crud.get_catalog(db, catalog_id)
    if not catalog or not catalog.cover_image_data:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=catalog.cover_image_data,
        media_type=catalog.cover_image_mime,
        headers={"Cache-Control": "public, max-age=86400"}  # 1-day cache
    )


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
    db: Session = Depends(get_db)
):
    img_bytes, mime = (None, None)
    if cover_image:
        img_bytes, mime = await utils.process_image(cover_image)

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
    return crud.create_catalog(db, catalog_in, img_bytes, mime)

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
    db: Session = Depends(get_db)
):
    db_obj = crud.get_catalog(db, catalog_id=catalog_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Catalog not found")

    img_bytes, mime = (None, None)
    if cover_image:
        img_bytes, mime = await utils.process_image(cover_image)

    updates = schemas.CatalogUpdate(
        title=title,
        description=description,
        spotify_url=spotify_url,
        apple_music_url=apple_music_url,
        audiomack_url=audiomack_url,
        boomplay_url=boomplay_url,
        youtubemusic_url=youtubemusic_url,
        soundcloud_url=soundcloud_url
    )
    return crud.update_catalog(db, db_obj, updates, img_bytes, mime)

@app.delete("/protected/catalogs/{catalog_id}")
async def protected_delete_catalog(catalog_id: int, db: Session = Depends(get_db)):
    db_obj = crud.get_catalog(db, catalog_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Catalog not found")
    crud.delete_catalog(db, catalog_id)
    return {"ok": True}

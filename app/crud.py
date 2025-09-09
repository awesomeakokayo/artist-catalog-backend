from sqlalchemy.orm import Session
from . import models, schemas   

def get_catalogs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Catalog).order_by(models.Catalog.created_at.desc()).offset(skip).limit(limit).all()

def get_catalog(db: Session, catalog_id: int):
    return db.query(models.Catalog).filter(models.Catalog.id == catalog_id).first()

def create_catalog(db: Session, catalog: schemas.CatalogCreate, cover_path: str = None):
    db_item = models.Catalog(
        title=catalog.title,
        description=catalog.description,
        cover_image=cover_path,
        spotify_url=catalog.spotify_url,
        apple_music_url=catalog.apple_music_url,
        audiomack_url=catalog.audiomack_url,
        boomplay_url=catalog.boomplay_url,
        youtubemusic_url=catalog.youtubemusic_url,
        soundcloud_url=catalog.soundcloud_url
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_catalog(db: Session, db_obj: models.Catalog, updates: schemas.CatalogUpdate, cover_path: str = None):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    if cover_path:
        db_obj.cover_image = cover_path
    db.commit()
    db.refresh(db_obj)
    return db_obj   

def delete_catalog(db: Session, catalog_id: int):
    db_obj = db.query(models.Catalog).filter(models.Catalog.id == catalog_id).first()
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True
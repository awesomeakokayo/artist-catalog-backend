from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class CatalogBase(BaseModel):
    title: str
    description: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    audiomack_url: Optional[str] = None
    boomplay_url: Optional[str] = None
    youtubemusic_url: Optional[str] = None
    soundcloud_url: Optional[str] = None

class CatalogCreate(CatalogBase):
    pass

class CatalogUpdate(CatalogBase):
    pass

class CatalogOut(CatalogBase):
    id: int
    cover_image_mime: Optional[str] = None

    class Config:
        from_attributes = True

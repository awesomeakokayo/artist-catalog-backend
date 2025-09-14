from sqlalchemy import Column, Integer, LargeBinary, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Catalog(Base):
    __tablename__ = "catalog"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), index=True, nullable=False)
    description = Column(Text, nullable=True)
    cover_image_data = Column(LargeBinary, nullable=True)
    cover_image_mime = Column(String, nullable=True)
    spotify_url = Column(String(512), nullable=True)
    apple_music_url = Column(String(512), nullable=True)
    audiomack_url = Column(String(512), nullable=True)
    boomplay_url = Column(String(512), nullable=True)
    youtubemusic_url = Column(String(512), nullable=True)
    soundcloud_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
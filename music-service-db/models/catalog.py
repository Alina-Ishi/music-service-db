from datetime import datetime
from typing import Optional, List

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship


class Artist(SQLModel, table=True):
    __tablename__ = "artists"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    country: Optional[str] = Field(default=None, max_length=2)
    bio: Optional[str] = None

    albums: List["Album"] = Relationship(back_populates="artist")
    track_links: List["TrackArtist"] = Relationship(back_populates="artist")


class Album(SQLModel, table=True):
    __tablename__ = "albums"

    id: Optional[int] = Field(default=None, primary_key=True)
    artist_id: int = Field(foreign_key="artists.id", index=True)
    title: str = Field(max_length=255)
    release_date: Optional[datetime] = None
    type: str = Field(default="album", max_length=20)   # album / single / compilation

    artist: Optional[Artist] = Relationship(back_populates="albums")
    tracks: List["Track"] = Relationship(back_populates="album")


class Genre(SQLModel, table=True):
    __tablename__ = "genres"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)

    track_links: List["TrackGenre"] = Relationship(back_populates="genre")


class Mood(SQLModel, table=True):
    __tablename__ = "moods"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    description: Optional[str] = None

    track_links: List["TrackMood"] = Relationship(back_populates="mood")


class Track(SQLModel, table=True):
    __tablename__ = "tracks"

    id: Optional[int] = Field(default=None, primary_key=True)
    album_id: Optional[int] = Field(default=None, foreign_key="albums.id", index=True)
    title: str = Field(max_length=255, index=True)
    duration_ms: int = Field(gt=0)
    track_number: Optional[int] = None
    year: Optional[int] = None
    explicit: bool = Field(default=False)

    # Ссылка на S3/MinIO; файл в БД не хранится
    audio_url: Optional[str] = Field(default=None, max_length=500)
    audio_mime: Optional[str] = Field(default=None, max_length=100)
    audio_size: Optional[int] = None
    audio_checksum: Optional[str] = Field(default=None, max_length=128)

    # Денормализованный счётчик для быстрого показа популярных треков
    play_count: int = Field(default=0, index=True)

    album: Optional[Album] = Relationship(back_populates="tracks")
    artist_links: List["TrackArtist"] = Relationship(back_populates="track")
    genre_links: List["TrackGenre"] = Relationship(back_populates="track")
    mood_links: List["TrackMood"] = Relationship(back_populates="track")
    # 1:M — у трека может быть несколько текстов (языки / форматы)
    lyrics: List["Lyrics"] = Relationship(back_populates="track")


class TrackArtist(SQLModel, table=True):
    __tablename__ = "track_artists"

    track_id: int = Field(foreign_key="tracks.id", primary_key=True)
    artist_id: int = Field(foreign_key="artists.id", primary_key=True)
    role: str = Field(default="main", primary_key=True, max_length=50)

    track: Optional[Track] = Relationship(back_populates="artist_links")
    artist: Optional[Artist] = Relationship(back_populates="track_links")


class TrackGenre(SQLModel, table=True):
    __tablename__ = "track_genres"

    track_id: int = Field(foreign_key="tracks.id", primary_key=True)
    genre_id: int = Field(foreign_key="genres.id", primary_key=True)

    track: Optional[Track] = Relationship(back_populates="genre_links")
    genre: Optional[Genre] = Relationship(back_populates="track_links")


class TrackMood(SQLModel, table=True):
    __tablename__ = "track_moods"

    track_id: int = Field(foreign_key="tracks.id", primary_key=True)
    mood_id: int = Field(foreign_key="moods.id", primary_key=True)
    weight: int = Field(default=100, ge=0, le=100)

    track: Optional[Track] = Relationship(back_populates="mood_links")
    mood: Optional[Mood] = Relationship(back_populates="track_links")


class Lyrics(SQLModel, table=True):
    __tablename__ = "lyrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    track_id: int = Field(foreign_key="tracks.id", index=True)
    language: str = Field(default="en", max_length=8)
    format: str = Field(default="LRC", max_length=16)
    lrc_url: Optional[str] = Field(default=None, max_length=500)
    lrc_text: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    track: Optional[Track] = Relationship(back_populates="lyrics")

    __table_args__ = (
        UniqueConstraint("track_id", "language", "format", name="uq_lyrics_track_lang_fmt"),
    )
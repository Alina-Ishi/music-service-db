from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .catalog import Track


class Playlist(SQLModel, table=True):
    __tablename__ = "playlists"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="playlists")
    track_links: List["PlaylistTrack"] = Relationship(back_populates="playlist")


class PlaylistTrack(SQLModel, table=True):
    __tablename__ = "playlist_tracks"

    playlist_id: int = Field(foreign_key="playlists.id", primary_key=True)
    track_id: int = Field(foreign_key="tracks.id", primary_key=True)
    position: int = Field(default=1, ge=1)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    playlist: Optional[Playlist] = Relationship(back_populates="track_links")
    track: Optional["Track"] = Relationship()


class Favorite(SQLModel, table=True):
    __tablename__ = "favorites"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    track_id: int = Field(foreign_key="tracks.id", primary_key=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="favorites")
    track: Optional["Track"] = Relationship()
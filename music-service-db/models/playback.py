from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .catalog import Track


class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    type: str = Field(max_length=20)       # phone / desktop / speaker / tablet
    os: Optional[str] = Field(default=None, max_length=50)
    name: str = Field(max_length=150)
    push_token: Optional[str] = Field(default=None, max_length=255)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="devices")
    sync_states: List["SyncState"] = Relationship(back_populates="device")
    playback_events: List["PlaybackEvent"] = Relationship(back_populates="device")


class SyncState(SQLModel, table=True):
    __tablename__ = "sync_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    track_id: int = Field(foreign_key="tracks.id", index=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    position_ms: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="sync_states")
    track: Optional["Track"] = Relationship()
    device: Optional[Device] = Relationship(back_populates="sync_states")

    __table_args__ = (
        UniqueConstraint("user_id", "track_id", name="uq_sync_user_track"),
    )


class PlaybackEvent(SQLModel, table=True):
    __tablename__ = "playback_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    track_id: int = Field(foreign_key="tracks.id", index=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    played_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    position_ms: int = Field(default=0, ge=0)
    duration_played_ms: int = Field(default=0, ge=0)
    source_type: Optional[str] = Field(default=None, max_length=20)  # playlist/album/recommendation
    source_id: Optional[int] = None

    user: Optional["User"] = Relationship(back_populates="playback_events")
    track: Optional["Track"] = Relationship()
    device: Optional[Device] = Relationship(back_populates="playback_events")

    __table_args__ = (
        Index("ix_playback_events_track_played", "track_id", "played_at"),
        Index("ix_playback_events_user_played", "user_id", "played_at"),
    )
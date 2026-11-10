from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .playlist import Playlist, Favorite
    from .playback import Device, PlaybackEvent, SyncState


class Tariff(SQLModel, table=True):
    __tablename__ = "tariffs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    price: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    duration_days: int = Field(default=30)
    quality: str = Field(default="standard")   # standard / hi-fi / lossless
    has_ads: bool = Field(default=False)

    subscriptions: List["Subscription"] = Relationship(back_populates="tariff")


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tariff_id: int = Field(foreign_key="tariffs.id", index=True)
    start_date: date
    end_date: date
    status: str = Field(default="active", max_length=20)
    auto_renew: bool = Field(default=True)

    user: Optional["User"] = Relationship(back_populates="subscriptions")
    tariff: Optional[Tariff] = Relationship(back_populates="subscriptions")
    payments: List["Payment"] = Relationship(back_populates="subscription")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    subscription_id: Optional[int] = Field(default=None, foreign_key="subscriptions.id")
    amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    paid_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    status: str = Field(default="completed", max_length=20)
    method: str = Field(default="card", max_length=20)

    user: Optional["User"] = Relationship(back_populates="payments")
    subscription: Optional[Subscription] = Relationship(back_populates="payments")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=150)
    country: Optional[str] = Field(default=None, max_length=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active", max_length=20)

    subscriptions: List[Subscription] = Relationship(back_populates="user")
    payments: List[Payment] = Relationship(back_populates="user")
    playlists: List["Playlist"] = Relationship(back_populates="user")
    favorites: List["Favorite"] = Relationship(back_populates="user")
    devices: List["Device"] = Relationship(back_populates="user")
    playback_events: List["PlaybackEvent"] = Relationship(back_populates="user")
    sync_states: List["SyncState"] = Relationship(back_populates="user")
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select, func

from models import Device, SyncState, PlaybackEvent, Track


def get_user_devices(session: Session, user_id: int) -> List[Device]:
    return list(session.exec(
        select(Device)
        .where(Device.user_id == user_id)
        .order_by(Device.last_seen_at.desc())
    ))


def get_sync_state(session: Session, user_id: int, track_id: int) -> Optional[SyncState]:
    stmt = (
        select(SyncState)
        .where(SyncState.user_id == user_id)
        .where(SyncState.track_id == track_id)
    )
    return session.exec(stmt).first()


def upsert_sync_state(
    session: Session, user_id: int, track_id: int,
    device_id: Optional[int], position_ms: int,
) -> SyncState:
    state = get_sync_state(session, user_id, track_id)
    if state is None:
        state = SyncState(
            user_id=user_id, track_id=track_id,
            device_id=device_id, position_ms=position_ms,
            updated_at=datetime.utcnow(),
        )
        session.add(state)
    else:
        state.device_id = device_id
        state.position_ms = position_ms
        state.updated_at = datetime.utcnow()
        session.add(state)
    session.commit()
    session.refresh(state)
    return state


def record_playback(
    session: Session, user_id: int, track_id: int,
    device_id: Optional[int], position_ms: int,
    duration_played_ms: int,
    source_type: Optional[str] = None,
    source_id: Optional[int] = None,
) -> PlaybackEvent:
    event = PlaybackEvent(
        user_id=user_id, track_id=track_id, device_id=device_id,
        position_ms=position_ms, duration_played_ms=duration_played_ms,
        source_type=source_type, source_id=source_id,
    )
    session.add(event)

    # Денормализованный счётчик (в продакшене — атомарный UPDATE или триггер)
    track = session.get(Track, track_id)
    if track:
        track.play_count += 1
        session.add(track)

    session.commit()
    session.refresh(event)
    return event


def get_user_history(session: Session, user_id: int, limit: int = 50) -> List[PlaybackEvent]:
    stmt = (
        select(PlaybackEvent)
        .where(PlaybackEvent.user_id == user_id)
        .order_by(PlaybackEvent.played_at.desc())
        .limit(limit)
    )
    return list(session.exec(stmt))


def get_recently_played_tracks(
    session: Session, user_id: int, days: int = 7, limit: int = 20
) -> List[Track]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Track, func.max(PlaybackEvent.played_at).label("last_played"))
        .join(PlaybackEvent, PlaybackEvent.track_id == Track.id)
        .where(PlaybackEvent.user_id == user_id)
        .where(PlaybackEvent.played_at >= since)
        .group_by(Track.id)
        .order_by(func.max(PlaybackEvent.played_at).desc())
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    return [row[0] for row in rows]
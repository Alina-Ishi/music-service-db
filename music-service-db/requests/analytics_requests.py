from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
from sqlmodel import Session, select, func

from models import Track, PlaybackEvent, Artist, TrackArtist


def get_top_tracks(session: Session, limit: int = 10) -> List[Tuple[Track, int]]:
    stmt = (
        select(Track, func.count(PlaybackEvent.id).label("plays"))
        .join(PlaybackEvent, PlaybackEvent.track_id == Track.id)
        .group_by(Track.id)
        .order_by(func.count(PlaybackEvent.id).desc())
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    return [(row[0], row[1]) for row in rows]


def get_top_tracks_denormalized(session: Session, limit: int = 10) -> List[Track]:
    stmt = select(Track).order_by(Track.play_count.desc()).limit(limit)
    return list(session.exec(stmt))


def get_top_artists(session: Session, limit: int = 10) -> List[Tuple[Artist, int]]:
    stmt = (
        select(Artist, func.count(PlaybackEvent.id).label("plays"))
        .join(TrackArtist, TrackArtist.artist_id == Artist.id)
        .join(Track, Track.id == TrackArtist.track_id)
        .join(PlaybackEvent, PlaybackEvent.track_id == Track.id)
        .group_by(Artist.id)
        .order_by(func.count(PlaybackEvent.id).desc())
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    return [(row[0], row[1]) for row in rows]


def get_user_listening_stats(session: Session, user_id: int) -> Dict[str, Any]:
    total_plays = session.exec(
        select(func.count(PlaybackEvent.id)).where(PlaybackEvent.user_id == user_id)
    ).one()

    total_ms = session.exec(
        select(func.coalesce(func.sum(PlaybackEvent.duration_played_ms), 0))
        .where(PlaybackEvent.user_id == user_id)
    ).one()

    top_rows = session.execute(
        select(Track.title, func.count(PlaybackEvent.id).label("plays"))
        .join(PlaybackEvent, PlaybackEvent.track_id == Track.id)
        .where(PlaybackEvent.user_id == user_id)
        .group_by(Track.id)
        .order_by(func.count(PlaybackEvent.id).desc())
        .limit(5)
    ).all()

    return {
        "user_id": user_id,
        "total_plays": total_plays,
        "total_listened_ms": total_ms,
        "total_listened_hours": round(total_ms / 3_600_000, 2),
        "top_tracks": [(r[0], r[1]) for r in top_rows],
    }


def get_daily_play_counts(session: Session, days: int = 14) -> List[Tuple[str, int]]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(
            func.date(PlaybackEvent.played_at).label("day"),
            func.count(PlaybackEvent.id).label("plays"),
        )
        .where(PlaybackEvent.played_at >= since)
        .group_by(func.date(PlaybackEvent.played_at))
        .order_by(func.date(PlaybackEvent.played_at))
    )
    rows = session.execute(stmt).all()
    return [(str(r[0]), r[1]) for r in rows]
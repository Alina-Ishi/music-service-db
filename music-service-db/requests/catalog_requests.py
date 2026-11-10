from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from models import (
    Artist, Album, Track, Genre, TrackGenre, TrackArtist,
    Mood, TrackMood, Lyrics,
)


def get_track_by_id(session: Session, track_id: int) -> Optional[Track]:
    return session.get(Track, track_id)


def get_track_details(
    session: Session, track_id: int, language: str = "en"
) -> Optional[Dict[str, Any]]:
    track = session.get(Track, track_id)
    if not track:
        return None

    # session.execute() — для многостолбцовых выборок
    artists = session.execute(
        select(Artist.name, TrackArtist.role)
        .join(TrackArtist, TrackArtist.artist_id == Artist.id)
        .where(TrackArtist.track_id == track_id)
    ).all()

    genres = session.exec(
        select(Genre.name)
        .join(TrackGenre, TrackGenre.genre_id == Genre.id)
        .where(TrackGenre.track_id == track_id)
    ).all()

    moods = session.execute(
        select(Mood.name, TrackMood.weight)
        .join(TrackMood, TrackMood.mood_id == Mood.id)
        .where(TrackMood.track_id == track_id)
    ).all()

    lyrics = session.exec(
        select(Lyrics)
        .where(Lyrics.track_id == track_id)
        .where(Lyrics.language == language)
    ).first()

    return {
        "track": track,
        "artists": [(r[0], r[1]) for r in artists],
        "genres": list(genres),
        "moods": [(r[0], r[1]) for r in moods],
        "lyrics": lyrics,
    }


def get_album_tracks(session: Session, album_id: int) -> List[Track]:
    stmt = (
        select(Track)
        .where(Track.album_id == album_id)
        .order_by(Track.track_number)
    )
    return list(session.exec(stmt))


def get_artist_albums(session: Session, artist_id: int) -> List[Album]:
    stmt = (
        select(Album)
        .where(Album.artist_id == artist_id)
        .order_by(Album.release_date.desc())
    )
    return list(session.exec(stmt))


def search_tracks(session: Session, query: str, limit: int = 20) -> List[Track]:
    stmt = (
        select(Track)
        .where(Track.title.ilike(f"%{query}%"))
        .order_by(Track.play_count.desc())
        .limit(limit)
    )
    return list(session.exec(stmt))


def get_tracks_by_genre(session: Session, genre_name: str, limit: int = 50) -> List[Track]:
    stmt = (
        select(Track)
        .join(TrackGenre, TrackGenre.track_id == Track.id)
        .join(Genre, Genre.id == TrackGenre.genre_id)
        .where(Genre.name == genre_name)
        .order_by(Track.play_count.desc())
        .limit(limit)
    )
    return list(session.exec(stmt))


def get_tracks_by_mood(
    session: Session, mood_name: str, min_weight: int = 50, limit: int = 50
) -> List[Track]:
    stmt = (
        select(Track)
        .join(TrackMood, TrackMood.track_id == Track.id)
        .join(Mood, Mood.id == TrackMood.mood_id)
        .where(Mood.name == mood_name)
        .where(TrackMood.weight >= min_weight)
        .order_by(TrackMood.weight.desc(), Track.play_count.desc())
        .limit(limit)
    )
    return list(session.exec(stmt))


def get_lyrics(session: Session, track_id: int, language: str = "en") -> Optional[Lyrics]:
    stmt = (
        select(Lyrics)
        .where(Lyrics.track_id == track_id)
        .where(Lyrics.language == language)
    )
    return session.exec(stmt).first()
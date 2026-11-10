from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from models import Playlist, PlaylistTrack, Track, Favorite


def get_user_playlists(session: Session, user_id: int) -> List[Playlist]:
    stmt = (
        select(Playlist)
        .where(Playlist.user_id == user_id)
        .order_by(Playlist.created_at.desc())
    )
    return list(session.exec(stmt))


def get_playlist_with_tracks(session: Session, playlist_id: int) -> Optional[Dict[str, Any]]:
    playlist = session.get(Playlist, playlist_id)
    if not playlist:
        return None

    rows = session.execute(
        select(Track, PlaylistTrack.position)
        .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
        .where(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.position)
    ).all()

    return {"playlist": playlist, "tracks": [(r[0], r[1]) for r in rows]}


def create_playlist(
    session: Session, user_id: int, title: str,
    description: Optional[str] = None, is_public: bool = False,
) -> Playlist:
    playlist = Playlist(
        user_id=user_id, title=title, description=description, is_public=is_public
    )
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


def add_track_to_playlist(
    session: Session, playlist_id: int, track_id: int,
    position: Optional[int] = None,
) -> PlaylistTrack:
    # Идемпотентность: если трек уже есть в плейлисте — возвращаем существующую связь
    existing = session.get(PlaylistTrack, (playlist_id, track_id))
    if existing:
        return existing

    if position is None:
        last = session.exec(
            select(PlaylistTrack)
            .where(PlaylistTrack.playlist_id == playlist_id)
            .order_by(PlaylistTrack.position.desc())
        ).first()
        position = (last.position + 1) if last else 1

    link = PlaylistTrack(playlist_id=playlist_id, track_id=track_id, position=position)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def get_favorites(session: Session, user_id: int) -> List[Track]:
    stmt = (
        select(Track)
        .join(Favorite, Favorite.track_id == Track.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.added_at.desc())
    )
    return list(session.exec(stmt))


def add_favorite(session: Session, user_id: int, track_id: int) -> Favorite:
    # Идемпотентность: повторный лайк не падает
    existing = session.get(Favorite, (user_id, track_id))
    if existing:
        return existing

    fav = Favorite(user_id=user_id, track_id=track_id)
    session.add(fav)
    session.commit()
    session.refresh(fav)
    return fav
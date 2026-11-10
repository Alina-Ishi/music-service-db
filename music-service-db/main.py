from sqlmodel import select

from database import get_session
from models import Track
from requests import (
    get_user_by_email, get_active_subscription, get_user_payments,
    get_track_details, get_tracks_by_mood, search_tracks,
    get_user_playlists, get_playlist_with_tracks,
    get_user_devices, get_sync_state, get_recently_played_tracks,
    get_top_tracks_denormalized, get_user_listening_stats, get_daily_play_counts,
)


def main() -> None:
    with get_session() as s:
        user = get_user_by_email(s, "alice@example.com")
        if not user:
            print("User not found. Run `python seed.py` first.")
            return

        print("User:", user.name, user.email)

        sub = get_active_subscription(s, user.id)
        print("Active subscription:", sub.id if sub else None)

        print("Payments:", [(str(p.amount), p.status) for p in get_user_payments(s, user.id)])

        first_track = s.exec(select(Track).limit(1)).first()
        if not first_track:
            print("No tracks in DB. Run `python seed.py` first.")
            return

        details = get_track_details(s, first_track.id)
        if not details:
            print("Track details not found.")
            return

        print("Track:", details["track"].title)
        print("Artists:", details["artists"])
        print("Genres:", details["genres"])
        print("Moods:", details["moods"])
        print("Lyrics:", bool(details["lyrics"]))

        print("Happy tracks:", [t.title for t in get_tracks_by_mood(s, "Happy")])
        print("Search 'love':", [t.title for t in search_tracks(s, "love")])

        playlists = get_user_playlists(s, user.id)
        print("Playlists:", [p.title for p in playlists])
        if playlists:
            data = get_playlist_with_tracks(s, playlists[0].id)
            if data:
                print("Playlist tracks:", [row[0].title for row in data["tracks"]])

        devices = get_user_devices(s, user.id)
        print("Devices:", [(d.type, d.name) for d in devices])

        state = get_sync_state(s, user.id, first_track.id)
        print("Sync position:", state.position_ms if state else None)

        print("Recent:", [t.title for t in get_recently_played_tracks(s, user.id)])
        print("Top (denorm):", [t.title for t in get_top_tracks_denormalized(s, 5)])
        print("User stats:", get_user_listening_stats(s, user.id))
        print("Daily plays:", get_daily_play_counts(s))


if __name__ == "__main__":
    main()
from .user_requests import (
    get_user_by_email,
    get_user_by_id,
    get_active_subscription,
    get_user_payments,
    get_all_tariffs,
    create_user,
)
from .catalog_requests import (
    get_track_by_id,
    get_track_details,
    get_album_tracks,
    get_artist_albums,
    search_tracks,
    get_tracks_by_genre,
    get_tracks_by_mood,
    get_lyrics,
)
from .playlist_requests import (
    get_user_playlists,
    get_playlist_with_tracks,
    create_playlist,
    add_track_to_playlist,
    get_favorites,
    add_favorite,
)
from .playback_requests import (
    get_user_devices,
    get_sync_state,
    upsert_sync_state,
    record_playback,
    get_user_history,
    get_recently_played_tracks,
)
from .analytics_requests import (
    get_top_tracks,
    get_top_tracks_denormalized,
    get_top_artists,
    get_user_listening_stats,
    get_daily_play_counts,
)
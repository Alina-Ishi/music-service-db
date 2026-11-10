from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlmodel import Session
from database import engine, create_db_and_tables
from models import (
    User, Tariff, Subscription, Payment,
    Artist, Album, Track, Genre, TrackGenre, TrackArtist,
    Mood, TrackMood, Lyrics,
    Playlist, PlaylistTrack, Favorite,
    Device, SyncState, PlaybackEvent,
)

def seed() -> None:
    create_db_and_tables()
    with Session(engine) as s:
        # Пользователи
        users = [
            User(email="alice@example.com", password_hash="hash1", name="Alice", country="US"),
            User(email="bob@example.com", password_hash="hash2", name="Bob", country="DE"),
            User(email="carol@example.com", password_hash="hash3", name="Carol", country="RU"),
        ]
        s.add_all(users)
        s.commit()

        # Тарифы
        tariffs = [
            Tariff(name="Free", price=Decimal("0.00"), duration_days=0,
                   quality="standard", has_ads=True),
            Tariff(name="Premium", price=Decimal("9.99"), duration_days=30,
                   quality="lossless", has_ads=False),
        ]
        s.add_all(tariffs)
        s.commit()

        # Подписки и платежи
        sub = Subscription(user_id=users[0].id, tariff_id=tariffs[1].id,
                           start_date=date.today(),
                           end_date=date.today() + timedelta(days=30),
                           status="active", auto_renew=True)
        s.add(sub)
        s.commit()

        s.add(Payment(user_id=users[0].id, subscription_id=sub.id,
                      amount=Decimal("9.99"), status="completed", method="card"))
        s.commit()

        # Артисты
        artists = [
            Artist(name="The Weeknd", country="CA", bio="Canadian singer"),
            Artist(name="Daft Punk", country="FR", bio="French electronic duo"),
            Artist(name="Queen", country="GB", bio="British rock band"),
            Artist(name="Billie Eilish", country="US", bio="American singer"),
        ]
        s.add_all(artists)
        s.commit()

        # Альбомы
        albums = [
            Album(artist_id=artists[0].id, title="After Hours", type="album"),
            Album(artist_id=artists[1].id, title="Random Access Memories", type="album"),
            Album(artist_id=artists[2].id, title="A Night at the Opera", type="album"),
            Album(artist_id=artists[3].id, title="Happier Than Ever", type="album"),
        ]
        s.add_all(albums)
        s.commit()

        # Жанры
        genres = [
            Genre(name="Pop"), Genre(name="Electronic"),
            Genre(name="Rock"), Genre(name="Alternative"),
        ]
        s.add_all(genres)
        s.commit()

        # Настроения
        moods = [
            Mood(name="Happy", description="Upbeat and positive"),
            Mood(name="Sad", description="Melancholic"),
            Mood(name="Energetic", description="High energy"),
            Mood(name="Chill", description="Relaxed"),
        ]
        s.add_all(moods)
        s.commit()

        # Треки
        tracks = [
            Track(album_id=albums[0].id, title="Blinding Lights",
                  duration_ms=200000, track_number=1, year=2019,
                  audio_url="s3://music/audio/blinding_lights.mp3",
                  audio_mime="audio/mpeg", audio_size=5_000_000),
            Track(album_id=albums[0].id, title="Save Your Tears",
                  duration_ms=215000, track_number=2, year=2020,
                  audio_url="s3://music/audio/save_your_tears.mp3",
                  audio_mime="audio/mpeg", audio_size=5_400_000),
            Track(album_id=albums[1].id, title="Get Lucky",
                  duration_ms=369000, track_number=1, year=2013,
                  audio_url="s3://music/audio/get_lucky.mp3",
                  audio_mime="audio/mpeg", audio_size=9_200_000),
            Track(album_id=albums[2].id, title="Bohemian Rhapsody",
                  duration_ms=354000, track_number=1, year=1975,
                  audio_url="s3://music/audio/bohemian_rhapsody.mp3",
                  audio_mime="audio/mpeg", audio_size=8_800_000),
            Track(album_id=albums[3].id, title="bad guy",
                  duration_ms=194000, track_number=1, year=2019,
                  audio_url="s3://music/audio/bad_guy.mp3",
                  audio_mime="audio/mpeg", audio_size=4_800_000),
        ]
        s.add_all(tracks)
        s.commit()

        # Связи трек–артист
        s.add_all([
            TrackArtist(track_id=tracks[0].id, artist_id=artists[0].id, role="main"),
            TrackArtist(track_id=tracks[1].id, artist_id=artists[0].id, role="main"),
            TrackArtist(track_id=tracks[2].id, artist_id=artists[1].id, role="main"),
            TrackArtist(track_id=tracks[3].id, artist_id=artists[2].id, role="main"),
            TrackArtist(track_id=tracks[4].id, artist_id=artists[3].id, role="main"),
        ])

        # Связи трек–жанр
        s.add_all([
            TrackGenre(track_id=tracks[0].id, genre_id=genres[0].id),
            TrackGenre(track_id=tracks[0].id, genre_id=genres[1].id),
            TrackGenre(track_id=tracks[1].id, genre_id=genres[0].id),
            TrackGenre(track_id=tracks[2].id, genre_id=genres[1].id),
            TrackGenre(track_id=tracks[3].id, genre_id=genres[2].id),
            TrackGenre(track_id=tracks[4].id, genre_id=genres[3].id),
        ])

        # Связи трек–настроение
        s.add_all([
            TrackMood(track_id=tracks[0].id, mood_id=moods[2].id, weight=95),
            TrackMood(track_id=tracks[1].id, mood_id=moods[1].id, weight=80),
            TrackMood(track_id=tracks[2].id, mood_id=moods[0].id, weight=90),
            TrackMood(track_id=tracks[3].id, mood_id=moods[1].id, weight=70),
            TrackMood(track_id=tracks[4].id, mood_id=moods[3].id, weight=85),
        ])

        # Текст песни (LRC)
        s.add(Lyrics(
            track_id=tracks[0].id, language="en", format="LRC",
            lrc_url="s3://music/lyrics/blinding_lights.lrc",
            lrc_text="[00:12.00] I've been on my own for long enough\n[00:15.00] Maybe you can show me how to love",
        ))
        s.add(Lyrics(
            track_id=tracks[3].id, language="en", format="LRC",
            lrc_text="[00:00.00] Is this the real life?\n[00:03.00] Is this just fantasy?",
        ))
        s.commit()

        # Плейлисты
        pl1 = Playlist(user_id=users[0].id, title="Workout Mix", is_public=True)
        pl2 = Playlist(user_id=users[1].id, title="Chill Evening", is_public=False)
        s.add_all([pl1, pl2])
        s.commit()

        s.add_all([
            PlaylistTrack(playlist_id=pl1.id, track_id=tracks[0].id, position=1),
            PlaylistTrack(playlist_id=pl1.id, track_id=tracks[2].id, position=2),
            PlaylistTrack(playlist_id=pl2.id, track_id=tracks[1].id, position=1),
            PlaylistTrack(playlist_id=pl2.id, track_id=tracks[4].id, position=2),
        ])

        # Избранное
        s.add_all([
            Favorite(user_id=users[0].id, track_id=tracks[0].id),
            Favorite(user_id=users[0].id, track_id=tracks[3].id),
            Favorite(user_id=users[1].id, track_id=tracks[4].id),
        ])

        # Устройства
        devices = [
            Device(user_id=users[0].id, type="phone", os="iOS", name="iPhone 14"),
            Device(user_id=users[0].id, type="desktop", os="macOS", name="MacBook Pro"),
            Device(user_id=users[1].id, type="speaker", os="Embedded", name="Home Speaker"),
        ]
        s.add_all(devices)
        s.commit()

        # Состояние синхронизации
        s.add(SyncState(user_id=users[0].id, track_id=tracks[0].id,
                        device_id=devices[0].id, position_ms=65000))

        # События прослушивания
        now = datetime.utcnow()
        events = [
            PlaybackEvent(user_id=users[0].id, track_id=tracks[0].id,
                          device_id=devices[0].id, played_at=now - timedelta(hours=2),
                          position_ms=0, duration_played_ms=200000,
                          source_type="playlist", source_id=pl1.id),
            PlaybackEvent(user_id=users[0].id, track_id=tracks[2].id,
                          device_id=devices[1].id, played_at=now - timedelta(hours=1),
                          position_ms=0, duration_played_ms=369000,
                          source_type="album", source_id=albums[1].id),
            PlaybackEvent(user_id=users[1].id, track_id=tracks[1].id,
                          device_id=devices[2].id, played_at=now - timedelta(minutes=30),
                          position_ms=0, duration_played_ms=215000,
                          source_type="recommendation"),
            PlaybackEvent(user_id=users[1].id, track_id=tracks[3].id,
                          device_id=devices[2].id, played_at=now - timedelta(minutes=10),
                          position_ms=0, duration_played_ms=354000,
                          source_type="album", source_id=albums[2].id),
        ]
        s.add_all(events)

        # Обновим денормализованный play_count
        for ev in events:
            tr = s.get(Track, ev.track_id)
            if tr:
                tr.play_count += 1
                s.add(tr)

        s.commit()
        print("Seed data inserted.")

if __name__ == "__main__":
    seed()
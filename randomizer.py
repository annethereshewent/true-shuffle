import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import time
import hashlib


def get_current_playlist_id(playback):
    context = playback.get('context') or {}

    uri = context.get('uri')

    if not uri:
        return None

    parts = uri.split(":")

    if parts[1] == "playlist":
        pid = parts[-1]

        return pid

    print("[WARN] only playlists supported")

    return None

def get_current_tracks(playlist_id):
    result = sp.playlist_tracks(playlist_id, fields="items.track.uri,total,next")

    uris = []

    while True:
        uris += [item["track"]["uri"] for item in result["items"]]

        if not result.get("Next"):
            break

        result = result.next()

    return uris

def get_rng(user_id, playlist_id):
    current_time = time.time_ns()

    hash = int(hashlib.sha256(f"{user_id}-{playlist_id}-{current_time}".encode()).hexdigest(), 16)

    rng = random.Random(hash)

    return rng

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state user-read-playback-state"))

user_id = sp.current_user()["id"]

tracks = []
remaining = []
current_playlist_id = None

skip_enqueuing_for_song = None

while True:
    playback = sp.current_playback()

    if playback is not None:
        playlist_id = get_current_playlist_id(playback)

        if playlist_id != current_playlist_id and playlist_id is not None:
            current_playlist_id = playlist_id
            tracks = get_current_tracks(playlist_id)
            remaining = tracks[:]

        now = time.time()

        current_song = playback["item"]["uri"]
        current_pos = playback["progress_ms"]

        duration = playback["item"]["duration_ms"]

        percentage = min(current_pos / duration, 1.0) if duration > 0 else 0

        if percentage > 0.99:
            if not tracks:
                time.sleep(1.0)
                continue

            if not remaining:
                remaining = tracks[:]

            rng = get_rng(user_id, current_playlist_id)

            next_song = rng.choice(remaining)

            print("current song finished, picking next song")
            remaining.remove(next_song)

            sp.start_playback(
                uris=[next_song],
                position_ms=0,
                device_id=playback["device"]["id"],
            )

        previous_pos = current_pos
    else:
        time.sleep(1.0)

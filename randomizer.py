import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import time
import hashlib


def get_current_playlist_id(playback):
    context = playback.get('context') or {}

    uri = context.get('uri')

    if not uri:
        print("[WARN]No playback URI found")
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

def is_skip(previous_pos, diff, duration):
    pct = min(previous_pos / duration, 1.0) if duration else 0
    return pct < 0.95 or diff < 3

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state user-read-playback-state"))

user_id = sp.current_user()["id"]

tracks = []
remaining = []
current_playlist_id = None

next_song = None

last_change_time = time.time()
last_song = None
previous_pos = 0

skip_enqueuing_for_song = None

while True:
    playback = sp.current_playback()

    if playback is not None:
        playlist_id = get_current_playlist_id(playback)

        if playlist_id is not None:
            now = time.time()

            current_song = playback["item"]["uri"]
            current_pos = playback["progress_ms"]

            if playlist_id != current_playlist_id:
                next_song = None
                current_playlist_id = playlist_id

                tracks = get_current_tracks(playlist_id)

                remaining = tracks[:]

                sp.start_playback(
                    uris=[current_song],
                    position_ms=playback["progress_ms"],
                    device_id=playback["device"]["id"],
                )

            duration = playback["item"]["duration_ms"]

            if current_song != last_song:
                diff = now - last_change_time
                if is_skip(previous_pos, diff, duration):
                    skip_enqueuing_for_song = current_song

                last_song = current_song
                last_change_time = now

            if (next_song == current_song or (next_song is None and current_song is not None)) and skip_enqueuing_for_song != current_song:
                if not remaining:
                    remaining = tracks[:]

                rng = get_rng(user_id, current_playlist_id)

                next_song = rng.choice(remaining)

                print("adding a new song to the queue!")

                print(next_song)

                sp.add_to_queue(next_song)
                remaining.remove(next_song)

    previous_pos = current_pos
    time.sleep(0.5)

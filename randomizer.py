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



sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state user-read-playback-state"))

user_id = sp.current_user()["id"]

tracks = []
remaining = []
current_playlist_id = None

song_chosen = False

next_song = None

while True:
    playback = sp.current_playback()

    if playback is not None:
        current_song = playback["item"]["uri"]

        if next_song == current_song:
            song_chosen = False

        playlist_id = get_current_playlist_id(playback)

        if playlist_id != current_playlist_id:
            current_playlist_id = playlist_id

            tracks = get_current_tracks(playlist_id)

            remaining = tracks[:]

        duration = playback["item"]["duration_ms"]
        current_time = playback["progress_ms"]

        diff = duration - current_time

        if current_playlist_id != None and diff <= 5000 and not song_chosen:
            if not remaining:
                remaining = tracks[:]

            rng = get_rng(user_id, current_playlist_id)

            next_song = rng.choice(remaining)

            print("adding a new song to the queue!")

            print(next_song)

            song_chosen = True

            sp.add_to_queue(next_song)
            remaining.remove(next_song)

    time.sleep(0.5)

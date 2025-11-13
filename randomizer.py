import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from dotenv import load_dotenv
from collections import deque

def get_current_playlist_id(playback):
    context = playback.get('context') or {}

    uri = context.get('uri')

    if not uri:
        return None

    parts = uri.split(":")

    if parts[1] == "playlist":
        pid = parts[-1]

        return pid

    return None

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state user-read-playback-state"))

playing_song = None
current_song = None

rolling_history = deque(maxlen=10)
while True:
    playback = sp.current_playback()

    if playback is not None:
        playlist_id = get_current_playlist_id(playback)

        # only use this randomizer for playlists
        if playlist_id is not None:
            playing_song = playback["item"]["uri"]

            if playing_song != current_song:
                print("the song changed! randomizing!")

                device_id = playback["device"]["id"]
                current_song = playing_song
                next_song = current_song

                rolling_history.append(playing_song)

                num_attempts = 0
                max_attempts = 10

                while next_song in rolling_history and num_attempts < max_attempts:
                    sp.shuffle(False, device_id=device_id)
                    sp.shuffle(True, device_id=device_id)

                    queue = sp.queue()
                    if not queue["queue"]:
                        break

                    next_song = queue["queue"][0]["uri"]

                    time.sleep(0.3)
                    num_attempts += 1

    time.sleep(0.5)

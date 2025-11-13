# True Shuffle

Ever noticed that sometimes Spotify's shuffle isn't really random? This daemon aims to fix that!

This is a Spotify daemon that will randomize songs in a playlist every time you play a song! Currently, Spotify "shuffle" generates a shuffled queue of songs that it plays through in order, which isn't truly random. This will actually bring a truly random, nondeterministic playback of playlist songs.

This will run in the background of your computer and will work for any device you're using as long as you keep the daemon running.

Note that currently only playlists are supported, albums and the like will not be shuffled.

## Setup

### Python3 Setup

You will need python3 for this application. Make sure you install it if it isn't already. You can get a version of it [here](https://www.python.org/downloads/) if you need it.

Once it's installed, run the following command to install all necessary python packages:

`pip3 install spotipy dotenv`

### Credentials

To get the credentials, simply sign up [here](https://developer.spotify.com/documentation/web-api/tutorials/getting-started). Once you've created an application, create a .env file in the root directory of the cloned repository with the following:
```
SPOTIPY_CLIENT_ID=(Your client id)
SPOTIPY_CLIENT_SECRET=(Your client secret)
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

Note that SPOTIFY_REDIRECT_URI should be **exactly** as written above. Make sure that the redirect URI in the WebAPI app you created above matches this as well.

### Running

The easiest part! From the command line, simply type `python3 randomizer.py`. The daemon will run indefinitely unless you terminate the process.

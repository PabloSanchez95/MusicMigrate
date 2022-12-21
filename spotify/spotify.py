import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


def get_spotipy_client():
    load_dotenv()
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    scopes = [
        "playlist-read-private",
        "user-library-read",
        "playlist-read-collaborative",
    ]
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id, client_secret=client_secret, scope=scopes
        )
    )


def get_spotify_complete_library() -> list:
    print("\033[1;36mGetting Spotify library \033[0m")
    spotipy = get_spotipy_client()

    offset = 0
    limit = 50
    library_items = []

    complete_library = []

    while not offset or library_items:
        if library_items:
            complete_library += library_items

        library = spotipy.current_user_saved_tracks(limit=limit, offset=offset)
        library_items = library.get("items")
        offset += limit

    return complete_library


def get_spotify_playlists():
    print("\033[1;36mGetting Spotify playlists \033[0m")
    spotipy = get_spotipy_client()

    offset = 0
    limit = 50
    curr_playlist_offset = []

    all_playlists = []

    while not offset or curr_playlist_offset:
        if curr_playlist_offset:
            all_playlists += curr_playlist_offset

        playlist_response = spotipy.current_user_playlists(limit=limit, offset=offset)
        curr_playlist_offset = playlist_response.get("items")
        offset += limit

    return all_playlists


def get_spotify_playlist_tracks(playlist_id: str, name: str):
    print(f"\033[1;36mGetting {name} tracks \033[0m")
    spotipy = get_spotipy_client()

    offset = 0
    limit = 50
    curr_track_offset = []

    all_tracks = []

    while not offset or curr_track_offset:
        if curr_track_offset:
            all_tracks += curr_track_offset

        playlist_tracks = spotipy.playlist_items(
            playlist_id=playlist_id, limit=limit, offset=offset
        )
        curr_track_offset = playlist_tracks.get("items")
        offset += limit

    return all_tracks

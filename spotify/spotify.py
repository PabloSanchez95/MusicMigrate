import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


def get_spotipy_client():
    load_dotenv()
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    scope = "user-library-read"

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id, client_secret=client_secret, scope=scope
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
        print(f"offset: {offset}")
        if library_items:
            complete_library += library_items
        library = spotipy.current_user_saved_tracks(limit=limit, offset=offset)
        library_items = library.get("items")
        offset += limit

    return complete_library

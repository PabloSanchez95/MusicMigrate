from difflib import SequenceMatcher
from re import compile
from typing import List, Optional

from ytmusicapi import YTMusic


def clean_ytmusic_library():
    print("\033[1;36mCleaning existing library \033[0m")
    ytmusic = YTMusic("youtube_music/headers_auth.json")
    library = ytmusic.get_library_songs(limit=3000)  # TODO: Make this dynamic
    remove_tokens = [song.get("feedbackTokens", []).get("remove") for song in library]
    song_titles = [song.get("title", "") for song in library]

    song_ptr = 0
    while song_ptr < len(remove_tokens):
        token = remove_tokens[song_ptr]

        remove_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = remove_response["feedbackResponses"][0]["isProcessed"]
        print(song_titles[song_ptr])
        if not is_processed:
            print("Error!")
        else:
            song_ptr += 1


def get_matching_song(yt_list_data: List[dict], spotify_data: dict) -> Optional[dict]:
    selected_song = None
    for yt_data in yt_list_data:
        title_similarity = SequenceMatcher(
            a=yt_data["title"], b=spotify_data["title"]
        ).ratio()

        if title_similarity < 0.30:
            continue

        artist_similarity = SequenceMatcher(
            a=yt_data["artists"][0], b=spotify_data["artists"][0]
        ).ratio()

        if artist_similarity < 0.35:
            continue

        album_similarity = SequenceMatcher(
            a=yt_data["album"], b=spotify_data["album"]
        ).ratio()

        if album_similarity < 0.75:
            if title_similarity > 0.85:
                selected_song = yt_data if not selected_song else selected_song
            continue

        selected_song = (
            selected_song
            if selected_song
            and SequenceMatcher(
                a=selected_song["title"], b=spotify_data["title"]
            ).ratio()
            > title_similarity
            else yt_data
        )
        break

    return selected_song


def search_song(title: str, artists: List[str], album: str) -> Optional[dict]:
    ytmusic = YTMusic("youtube_music/headers_auth.json")

    album_regex = compile("[^A-Za-zÁÉÍÓÚáéíóúñÑ ]")
    album = album_regex.sub("", album)
    album_first_word = album.split()[0] if album.split() else ""

    search_query = f"{title} {', '.join(artists)} {album_first_word}"
    search_result = ytmusic.search(query=search_query, filter="songs", limit=5)

    spotify_data = dict(title=title, artists=artists, album=album)
    yt_list_data = []

    for song_data in search_result:
        yt_list_data.append(
            dict(
                title=song_data["title"],
                artists=[
                    artist.get("name", "") for artist in song_data.get("artists", [])
                ],
                album=album_regex.sub("", song_data.get("album", {}).get("name", "")),
                tokens=song_data.get("feedbackTokens", {}),
            )
        )

    selected_song = get_matching_song(yt_list_data, spotify_data)
    if not selected_song:
        return
    return selected_song


def add_songs_to_library(token: str):
    ytmusic = YTMusic("youtube_music/headers_auth.json")

    is_processed = False
    while not is_processed:
        add_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = add_response["feedbackResponses"][0]["isProcessed"]

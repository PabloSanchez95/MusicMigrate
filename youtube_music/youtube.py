from typing import List, Optional
from ytmusicapi import YTMusic


def clean_ytmusic_library():
    ytmusic = YTMusic("youtube_music/headers_auth.json")
    library = ytmusic.get_library_songs(limit=100)
    remove_tokens = [song.get("feedbackTokens", []).get("remove") for song in library]

    song_ptr = 0
    while song_ptr < len(remove_tokens):
        token = remove_tokens[song_ptr]

        remove_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = remove_response["feedbackResponses"][0]["isProcessed"]
        if not is_processed:
            print("Error!")
        else:
            song_ptr += 1


def search_song(title: str, artist: str, album: str) -> Optional[dict]:
    ytmusic = YTMusic("youtube_music/headers_auth.json")
    search_result = ytmusic.search(query=f"{title} {artist} {album}", filter="songs")
    if not search_result:
        print("No results for search")
        return
    return search_result[0].get("feedbackTokens")


def add_songs_to_library(tokens: List[str]):
    ytmusic = YTMusic("youtube_music/headers_auth.json")

    song_ptr = 0
    while song_ptr < len(tokens):
        token = tokens[song_ptr]
        add_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = add_response["feedbackResponses"][0]["isProcessed"]
        if is_processed:
            song_ptr += 1

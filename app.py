from json import dump

from spotify.spotify import get_spotify_complete_library
from youtube_music.youtube import (
    add_songs_to_library,
    clean_ytmusic_library,
    search_song,
)


def spotify_to_youtube_music():
    track_list = list(reversed(get_spotify_complete_library()))
    dump(track_list, open("spotify/tracklist.json", "w"))
    clean_ytmusic_library()

    not_found = []
    add_tokens = []
    for track in track_list:
        song_tokens = search_song(track["title"], track["artist"], track["album"])
        if not song_tokens or not song_tokens.get("add"):
            not_found.append(track)
            continue
        print(track["title"], track["artist"], track["album"])
        add_tokens.append(song_tokens["add"])

    dump(not_found, open("youtube_music/not_found.json", "w"))

    add_songs_to_library(add_tokens)


if __name__ == "__main__":
    spotify_to_youtube_music()

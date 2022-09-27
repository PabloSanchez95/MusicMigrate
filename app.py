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
    print("\033[1;36mMigrating songs \033[0m")
    for track in track_list:
        song = search_song(track["title"], track["artists"], track["album"])

        if not song or not song.get("tokens"):
            print(
                f'\033[1;36m{track["title"]}, {track["artists"][0]}, {track["album"]} not found \033[0m'
            )
            not_found.append(track)
            continue

        print(f'{song["title"]}, {song["artists"][0]}, {song["album"]}')
        add_songs_to_library(song.get("tokens", {}).get("add"))

    dump(not_found, open("youtube_music/not_found.json", "w"))


if __name__ == "__main__":
    spotify_to_youtube_music()

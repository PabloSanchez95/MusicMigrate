from json import dump

from spotify.spotify import get_spotify_complete_library
from youtube_music.youtube import add_songs_to_library, search_song


def spotify_to_youtube_music():
    track_list = list(reversed(get_spotify_complete_library()))
    dump(track_list, open("spotify/tracklist.json", "w"))

    not_found = []
    print("\033[1;36mMigrating songs \033[0m")
    total_tracks = len(track_list)
    for i, track in enumerate(track_list):
        title = track["track"]["name"]
        artists = [artist["name"] for artist in track["track"]["artists"]]
        album = track["track"]["album"]["name"]
        duration = round(track["track"]["duration_ms"] / 1000)

        song = search_song(title, artists, album, duration, True)

        if not song:
            song = search_song(title, artists, album, duration, False)

        if not song or not song.get("tokens"):
            print(f"\033[1;36m{title}, {artists[0]}, {album} not found \033[0m")
            not_found.append(
                dict(
                    title=title,
                    artists=artists,
                    album=album,
                    duration=duration,
                )
            )
            continue

        print(
            f'{int((i+1) * 100 / total_tracks)}% - {song["title"]}, {song["artists"]}, {song["album"]}'
        )
        add_songs_to_library(song.get("tokens", {}).get("add"))

    dump(not_found, open("youtube_music/not_found.json", "w"))


if __name__ == "__main__":
    spotify_to_youtube_music()

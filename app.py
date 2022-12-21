from json import dump, load
from re import sub
from time import sleep

from spotify.spotify import (
    get_spotify_complete_library,
    get_spotify_playlist_tracks,
    get_spotify_playlists,
)
from youtube_music.youtube import (
    add_songs_to_library,
    add_songs_to_playlist,
    create_yt_playlist,
    search_song,
)


def migrate_songs(track_list: list, playlist_info: dict = None):
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
                    duration=track["track"]["duration_ms"],
                )
            )
            continue

        print(
            f'{int((i+1) * 100 / total_tracks)}% - {song["title"]}, {song["artists"]}, {song["album"]}'
        )

        try:
            if playlist_info:
                add_songs_to_playlist(playlist_info.get("id"), song.get("videoId"))
            else:
                add_songs_to_library(song.get("tokens", {}).get("add"))
        except Exception as e:
            print(str(e))
            print(f"{title}, {artists} not added")
            not_found.append(
                dict(title=title, artists=artists, album=album, duration=duration)
            )

    if playlist_info:
        not_found = dict(
            playlistName=playlist_info["name"],
            playlistId=playlist_info["id"],
            tracks=not_found,
        )
        playlist_info["name"] = sub("[^A-Za-z0-9 ]", "", playlist_info["name"])
        playlist_info["name"] = playlist_info["name"].lower().replace(" ", "_") + "_"

    dump(
        not_found,
        open(f"youtube_music/{playlist_info.get('name') or ''}not_found.json", "w"),
    )


def spotify_to_youtube_music():
    track_list = list(reversed(get_spotify_complete_library()))
    dump(track_list, open("spotify/tracklist.json", "w"))

    migrate_songs(track_list)


def spotify_to_youtube_music_playlists():
    spotify_playlists = list(reversed(get_spotify_playlists()))
    dump(spotify_playlists, open("spotify/playlists.json", "w"))

    i = 0
    while i < len(spotify_playlists):
        playlist = spotify_playlists[i]
        playlist_name = playlist["name"]
        playlist_description = playlist["description"]

        try:
            playlist_id = create_yt_playlist(playlist_name, playlist_description)
        except Exception as e:
            print(str(e))
            sleep(5)
            continue

        tracks = get_spotify_playlist_tracks(playlist["id"], playlist_name)
        migrate_songs(tracks, dict(name=playlist_name, id=playlist_id))
        i += 1


def retry_yt_not_found(file_name: str):
    yt_not_found = load(open(file_name, "r"))
    tracks = yt_not_found.get("tracks")

    for i in range(len(tracks)):
        tracks[i] = dict(
            track=dict(
                name=tracks[i]["title"],
                artists=[{"name": artist_name} for artist_name in tracks[i]["artists"]],
                album=dict(name=tracks[i]["album"]),
                duration_ms=tracks[i]["duration"],
            )
        )

    migrate_songs(
        tracks,
        dict(name=yt_not_found.get("playlistName"), id=yt_not_found.get("playlistId")),
    )


if __name__ == "__main__":
    spotify_to_youtube_music()
    spotify_to_youtube_music_playlists()

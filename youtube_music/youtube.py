from difflib import SequenceMatcher

from re import compile, sub
from typing import List, Optional

from ytmusicapi import YTMusic

ytmusic = YTMusic("youtube_music/headers_auth.json")


def get_string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(a=a, b=b).ratio()


def clean_ytmusic_library():
    print("\033[1;36mCleaning existing library \033[0m")
    ytmusic = YTMusic("youtube_music/headers_auth.json")
    library = ytmusic.get_library_songs(limit=3000)  # TODO: Make this dynamic
    remove_tokens = [song.get("feedbackTokens", []).get("remove") for song in library]
    song_titles = [song.get("title", "") for song in library]

    song_ptr = 0
    total_songs = len(remove_tokens)
    while song_ptr < total_songs:
        token = remove_tokens[song_ptr]

        remove_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = remove_response["feedbackResponses"][0]["isProcessed"]
        print(f"{int((song_ptr+1) * 100 / total_songs)}% - {song_titles[song_ptr]}")
        if not is_processed:
            print("Error!")
        else:
            song_ptr += 1


def get_matchting_song_by_time(yt_list_data: List[dict], spotify_data: dict):
    highest_avg = 0
    selected_song = None
    ERROR_RANGE = 2
    TITLE_CONSTANT = 1.3

    for yt_data in yt_list_data:
        if not (
            spotify_data["duration"] - ERROR_RANGE
            <= yt_data["duration"]
            <= spotify_data["duration"] + ERROR_RANGE
        ):
            continue

        title_similarity = get_string_similarity(
            yt_data["title"], spotify_data["title"]
        )

        artist_similarity = get_string_similarity(
            yt_data["artists"], spotify_data["artists"]
        )

        album_similarity = get_string_similarity(
            yt_data["album"], spotify_data["album"]
        )

        avg = (
            (title_similarity * TITLE_CONSTANT) + artist_similarity + album_similarity
        ) / 3

        if avg > highest_avg and artist_similarity > 0.40 and title_similarity > 0.50:
            highest_avg = avg
            selected_song = yt_data

    return selected_song if highest_avg > 0.50 else None


def get_matching_song(
    yt_list_data: List[dict], spotify_data: dict, strict: bool
) -> Optional[dict]:
    if strict:
        title_ratio = 0.50
        artist_ratio = 0.55
        album_ratio = 0.75
        title_album_ratio = 0.90
    else:
        title_ratio = 0.30
        artist_ratio = 0.50
        album_ratio = 0.75
        title_album_ratio = 0.50

    selected_song = None

    for yt_data in yt_list_data:
        title_similarity = get_string_similarity(
            yt_data["title"], spotify_data["title"]
        )

        if title_similarity < title_ratio:
            continue

        artist_similarity = get_string_similarity(
            yt_data["artists"], spotify_data["artists"]
        )

        if artist_similarity < artist_ratio:
            continue

        album_similarity = get_string_similarity(
            yt_data["album"], spotify_data["album"]
        )

        if album_similarity < album_ratio:
            yt_title_similar = selected_song and (
                get_string_similarity(selected_song["title"], spotify_data["title"])
                <= title_similarity
            )  # look for a more similar title
            if title_similarity >= title_album_ratio and (
                yt_title_similar or not selected_song
            ):
                prev_selected_song_album_similar = selected_song and (
                    get_string_similarity(selected_song["album"], spotify_data["album"])
                    > +album_similarity
                )
                selected_song = (
                    selected_song if prev_selected_song_album_similar else yt_data
                )

            continue

        selected_song = (
            selected_song
            if selected_song
            and get_string_similarity(selected_song["title"], spotify_data["title"])
            >= title_similarity
            else yt_data
        )
        break

    return selected_song


def clean_title(title: str) -> str:
    title = title.lower()

    # possible_artists = search("([\(\[]).*(feat|ft).*?([\)\]])", title)
    # possible_artists = sub("(ft.|feat.|featuring|&)", "", possible_artists)

    title = sub(";[^;\r\n]+(?=(original|remaster|bonus|feat|with\s)).*", "", title)
    title = sub(
        ".([\[\(])[^\)\]]+(?=(riginal|emaster|onus|eat\.|ith\s|ingle|rom\s)).*?([\)\]])",
        "",
        title,
    )
    title = sub(
        "-[^-\r\n]+(?=(original|remaster|bonus|feat|with\s|single|from)).*", "", title
    )
    title = sub(".feat.*", "", title)
    return title.strip()


def clean_artists(artist: str) -> str:
    artist = artist.lower()
    artist = sub(",|\ ?&", "", artist)
    return artist.strip()


def clean_album(album: str) -> str:
    album = album.lower()
    album = sub(".([\[\(])[^\)\]]+(?=(emaster)).*?([\)\]])", "", album)
    album_regex = compile("[^A-Za-zÁÉÍÓÚáéíóúñÑ0-9 ]")
    album = album_regex.sub("", album)
    return album.strip()


def search_song(
    title: str, artists: List[str], album: str, duration: int, with_album: bool
) -> Optional[dict]:
    title = clean_title(title)

    album = clean_album(album)
    album_first_word = album.split()[0] if album.split() else ""

    complete_artists = ", ".join(artists)

    search_query = (
        f"{title} {complete_artists} {album_first_word if with_album else ''}".strip()
    )
    search_result = ytmusic.search(query=search_query or " ", filter="songs")

    spotify_data = dict(
        title=title,
        artists=clean_artists(complete_artists),
        album=album.lower(),
        duration=duration,
    )
    yt_list_data = []

    for song_data in search_result:
        try:
            yt_artist = [
                artist.get("name", "") for artist in song_data.get("artists", [])
            ]
            yt_list_data.append(
                dict(
                    title=clean_title(song_data["title"]),
                    artists=clean_artists(", ".join(yt_artist)),
                    album=clean_album(
                        (song_data.get("album", {}) or {}).get("name", "")
                    ),
                    tokens=song_data.get("feedbackTokens", {}),
                    duration=song_data["duration_seconds"],
                )
            )
        except AttributeError:
            print(song_data)
            return

    selected_song = get_matchting_song_by_time(yt_list_data, spotify_data)
    if not selected_song:
        selected_song = get_matching_song(yt_list_data, spotify_data, True)

    if not selected_song:
        spotify_data["artists"] = clean_artists(artists[0])
        selected_song = get_matching_song(yt_list_data, spotify_data, False)

    return selected_song


def add_songs_to_library(token: str):
    is_processed = False
    while not is_processed:
        add_response = ytmusic.edit_song_library_status(feedbackTokens=token)
        is_processed = add_response["feedbackResponses"][0]["isProcessed"]

# Music Migration Script

A collections of scripts to move music from a streaming service to another

## Services currently supported

- Spotify
- Youtube Music

## Installation

Make sure you have [Python 3.7+](https://www.python.org/) installed.

Setup your environment with:

```sh
make setup
```

## Running

To run the spotify -> ytmusic script:

```sh
make
```

### Connect services

#### Spotipy

To create a spotify app, please follow [Spotipys Documentation](https://spotipy.readthedocs.io/en/master/#authorization-code-flow)

#### ytmusicapi

To get a youtube music session, please folow [ytmusicpi Documentation](https://ytmusicapi.readthedocs.io/en/latest/setup.html#authenticated-requests)

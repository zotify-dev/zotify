# STILL IN DEVELOPMENT, NOT RECOMMENDED FOR GENERAL USE!

![Logo banner](https://s1.fileditch.ch/hOwJhfeCFEsYFRWUWaz.png)

# Zotify

A customizable music and podcast downloader. \
Formerly ZSp‌otify.

Available on [zotify.xyz](https://zotify.xyz/zotify/zotify) and [GitHub](https://github.com/zotify-dev/zotify).

## Features

- Save tracks at up to 320kbps\*
- Save to most popular audio formats
- Built in search
- Bulk downloads
- Downloads synced lyrics
- Embedded metadata
- Downloads all audio, metadata and lyrics directly, no substituting from other services.

\*Non-premium accounts are limited to 160kbps

## Installation

Requires Python 3.10 or greater. \
Optionally requires FFmpeg to save tracks as anything other than Ogg Vorbis.

Enter the following command in terminal to install Zotify. \
`python -m pip install https://get.zotify.xyz`

## General Usage

### Simplest usage

Downloads specified items. Accepts any combination of track, album, playlist, episode or artists, URLs or URIs. \
`zotify <items to download>`

### Basic options

```
    -p,  --playlist         Download selection of user's saved playlists
    -lt, --liked-tracks     Download user's liked tracks
    -le, --liked-episodes   Download user's liked episodes
    -f,  --followed         Download selection of users followed artists
    -s,  --search <search>  Searches for items to download
```

<details><summary>All configuration options</summary>

| Config key              | Command line argument     | Description                                         |
| ----------------------- | ------------------------- | --------------------------------------------------- |
| path_credentials        | --path-credentials        | Path to credentials file                            |
| path_archive            | --path-archive            | Path to track archive file                          |
| music_library           | --music-library           | Path to root of music library                       |
| podcast_library         | --podcast-library         | Path to root of podcast library                     |
| mixed_playlist_library  | --mixed-playlist-library  | Path to root of mixed content playlist library      |
| output_album            | --output-album            | File layout for saved albums                        |
| output_playlist_track   | --output-playlist-track   | File layout for tracks in a playlist                |
| output_playlist_episode | --output-playlist-episode | File layout for episodes in a playlist              |
| output_podcast          | --output-podcast          | File layout for saved podcasts                      |
| download_quality        | --download-quality        | Audio download quality (auto for highest available) |
| audio_format            | --audio-format            | Audio format of final track output                  |
| transcode_bitrate       | --transcode-bitrate       | Transcoding bitrate (-1 to use download rate)       |
| ffmpeg_path             | --ffmpeg-path             | Path to ffmpeg binary                               |
| ffmpeg_args             | --ffmpeg-args             | Additional ffmpeg arguments when transcoding        |
| save_credentials        | --save-credentials        | Save login credentials to a file                    |
| save_subtitles          | --save-subtitles          |
| save_artist_genres      | --save-arist-genres       |

</details>

### More about search

- `-c` or `--category` can be used to limit search results to certain categories.
  - Available categories are "album", "artist", "playlist", "track", "show" and "episode".
  - You can search in multiple categories at once
- You can also narrow down results by using field filters in search queries
  - Currently available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre.
  - Available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre.
  - The artist and year filters can be used while searching albums, artists and tracks. You can filter on a single year or a range (e.g. 1970-1982).
  - The album filter can be used while searching albums and tracks.
  - The genre filter can be used while searching artists and tracks.
  - The isrc and track filters can be used while searching tracks.
  - The upc, tag:new and tag:hipster filters can only be used while searching albums. The tag:new filter will return albums released in the past two weeks and tag:hipster can be used to show only albums in the lowest 10% of popularity.

## Usage as a library

Zotify can be used as a user-friendly library for saving music, podcasts, lyrics and metadata.

Here's a very simple example of downloading a track and its metadata:

```python
import zotify

session = zotify.Session.from_userpass(username="username", password="password")
track = session.get_track("4cOdK2wGLETKBW3PvgPWqT")
output = track.create_output("./Music", "{artist} - {title}")

file = track.write_audio_stream(output)

file.write_metadata(track.metadata)
file.write_cover_art(track.get_cover_art())
```

## Contributing

Pull requests are always welcome, but if adding an entirely new feature we encourage you to create an issue proposing the feature first so we can ensure it's something that fits sthe scope of the project.

Zotify aims to be a comprehensive and user-friendly tool for downloading music and podcasts.
It is designed to be simple by default but offer a high level of configuration for users that want it.
All new contributions should follow this principle to keep the program consistent.

## Will my account get banned if I use this tool?

No user has reported their account getting banned after using Zotify
However, it is still a possiblity and it is recommended you use Zotify with a burner account where possible.

Consider using [Exportify](https://github.com/watsonbox/exportify) to keep backups of your playlists.

## Disclaimer

Using Zotify violates Sp‌otify user guidelines and may get your account suspended.

Zotify is intended to be used in compliance with DMCA, Section 1201, for educational, private and fair use, or any simlar laws in other regions. \
Zotify contributors cannot be held liable for damages caused by the use of this tool. See the [LICENSE](./LICENCE) file for more details.

## Acknowledgements

- [Librespot-Python](https://github.com/kokarare1212/librespot-python) does most of the heavy lifting, it's used for authentication, fetching track data, and audio streaming.
- [music-tag](https://github.com/KristoforMaynard/music-tag) is used for writing metadata into the downloaded files.
- [FFmpeg](https://ffmpeg.org/) is used for transcoding audio.

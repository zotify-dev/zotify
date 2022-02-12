# Zotify

### A music and podcast downloader needing only a python interpreter and ffmpeg.

<p align="center">
  <img src="https://i.imgur.com/hGXQWSl.png" width="50%">
</p>

[Discord Server](https://discord.gg/XDYsFRTUjE)

### Install

```
Dependencies:

- Python 3.9 or greater
- ffmpeg*

Installation:

python -m pip install https://gitlab.com/team-zotify/zotify/-/archive/main/zotify-main.zip
```

\*Windows users can download the binaries from [ffmpeg.org](https://ffmpeg.org) and add them to %PATH%. Mac users can install it via [Homebrew](https://brew.sh) by running `brew install ffmpeg`. Linux users should already know how to install ffmpeg, I don't want to add instructions for every package manager.

### Command line usage

```
Basic command line usage:
  zotify <track/album/playlist/episode/artist url>   Downloads the track, album, playlist or podcast episode specified as a command line argument. If an artist url is given, all albums by specified artist will be downloaded. Can take multiple urls.

Basic options:
  (nothing)        Download the tracks/alumbs/playlists URLs from the parameter
  -d, --download   Download all tracks/alumbs/playlists URLs from the specified file
  -p, --playlist   Downloads a saved playlist from your account
  -l, --liked      Downloads all the liked songs from your account
  -s, --search     Searches for specified track, album, artist or playlist, loads search prompt if none are given.
```

### Options

All these options can either be configured in the config or via the commandline, in case of both the commandline-option has higher priority.  
Be aware you have to set boolean values in the commandline like this: `--download-real-time=True`

| Key (config)                 | commandline parameter            | Description
|------------------------------|----------------------------------|---------------------------------------------------------------------|
| ROOT_PATH                    | --root-path                      | directory where Zotify saves music
| ROOT_PODCAST_PATH            | --root-podcast-path              | directory where Zotify saves podcasts
| SKIP_EXISTING_FILES          | --skip-existing-files            | Skip songs with the same name
| SKIP_PREVIOUSLY_DOWNLOADED   | --skip-previously-downloaded     | Use a song_archive file to skip previously downloaded songs
| DOWNLOAD_FORMAT              | --download-format                | The download audio format (aac, fdk_aac, m4a, mp3, ogg, opus, vorbis)
| FORCE_PREMIUM                | --force-premium                  | Force the use of high quality downloads (only with premium accounts)
| ANTI_BAN_WAIT_TIME           | --anti-ban-wait-time             | The wait time between bulk downloads
| OVERRIDE_AUTO_WAIT           | --override-auto-wait             | Totally disable wait time between songs with the risk of instability
| CHUNK_SIZE                   | --chunk-size                     | Chunk size for downloading
| SPLIT_ALBUM_DISCS            | --split-album-discs              | Saves each disk in its own folder
| DOWNLOAD_REAL_TIME           | --download-real-time             | Downloads songs as fast as they would be played, should prevent account bans.
| LANGUAGE                     | --language                       | Language for spotify metadata
| BITRATE                      | --bitrate                        | Overwrite the bitrate for ffmpeg encoding
| SONG_ARCHIVE                 | --song-archive                   | The song_archive file for SKIP_PREVIOUSLY_DOWNLOADED
| CREDENTIALS_LOCATION         | --credentials-location           | The location of the credentials.json
| OUTPUT                       | --output                         | The output location/format (see below)
| PRINT_SPLASH                 | --print-splash                   | Print the splash message
| PRINT_SKIPS                  | --print-skips                    | Print messages if a song is being skipped
| PRINT_DOWNLOAD_PROGRESS      | --print-download-progress        | Print the download/playlist progress bars
| PRINT_ERRORS                 | --print-errors                   | Print errors
| PRINT_DOWNLOADS              | --print-downloads                | Print messages when a song is finished downloading
| TEMP_DOWNLOAD_DIR            | --temp-download-dir              | Download tracks to a temporary directory first

### Output format

With the option `OUTPUT` (or the commandline parameter `--output`) you can specify the output location and format.  
The value is relative to the `ROOT_PATH`/`ROOT_PODCAST_PATH` directory and can contain the following placeholder:

| Placeholder     | Description
|-----------------|--------------------------------
| {artist}        | The song artist
| {album}         | The song album
| {song_name}     | The song name
| {release_year}  | The song release year
| {disc_number}   | The disc number
| {track_number}  | The track_number
| {id}            | The song id
| {track_id}      | The track id
| {ext}           | The file extension
| {album_id}      | (only when downloading albums) ID of the album
| {album_num}     | (only when downloading albums) Incrementing track number
| {playlist}      | (only when downloading playlists) Name of the playlist 
| {playlist_num}  | (only when downloading playlists) Incrementing track number

Example values could be:
~~~~
{playlist}/{artist} - {song_name}.{ext}
{playlist}/{playlist_num} - {artist} - {song_name}.{ext}
Bangers/{artist} - {song_name}.{ext}
{artist} - {song_name}.{ext}
{artist}/{album}/{album_num} - {artist} - {song_name}.{ext}
/home/user/downloads/{artist} - {song_name} [{id}].{ext}
~~~~

### Docker Usage - CURRENTLY BROKEN
```
Build the docker image from the Dockerfile:
  docker build -t zotify .
Create and run a container from the image:
  docker run --rm -u $(id -u):$(id -g) -v "$PWD/zotify:/app" -v "$PWD/config.json:/config.json" -v "$PWD/Zotify Music:/Zotify Music" -v "$PWD/Zotify Podcasts:/Zotify Podcasts" -it zotify
```

### Will my account get banned if I use this tool?

Currently no user has reported their account getting banned after using Zotify.

It is recommended you use Zotify with a burner account.
Alternatively, there is a configuration option labled ```DOWNLOAD_REAL_TIME```, this limits the download speed to the duration of the song being downloaded thus appearing less suspicious.
This option is much slower and is only recommended for premium users who wish to download songs in 320kbps without buying premium on a burner account.

**Use Zotify at your own risk**, the developers of Zotify are not responsible if your account gets banned.

### What do I do if I see "Your session has been terminated"?

If you see this, don't worry! Just try logging back in. If you see the incorrect username or password error, reset your password and you should be able to log back in.

### Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)

### Changelog

Please refer to [CHANGELOG](CHANGELOG.md)

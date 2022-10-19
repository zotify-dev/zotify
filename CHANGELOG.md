# Changelog

## 0.6.9
- Fix low resolution cover art
- Fix crash when missing ffmpeg

## 0.6.8
- Improve check for direct download availability of podcasts

## 0.6.7
- Temporary fix for upstream protobuf error

## v0.6.6
- Added `-f` / `--followed` option to download every song by all of your followed artists

## v0.6.5
- Implemented more stable fix for bug still persisting after v0.6.4

## v0.6.4
- Fixed upstream bug causing tracks to not download fully

## 0.6.3
- Less stupid single format
- Fixed error in json fetching
- Default to search if no other option is provided

## v0.6.2
- Won't crash if downloading a song with no lyrics and `DOWNLOAD_LYRICS` is set to True
- Fixed visual glitch when entering login info
- Saving genre metadata is now optional (disabled by default) and configurable with the `MD_SAVE_GENRES`/`--md-save-genres` option
- Switched to new loading animation that hopefully renders a little better in Windows command shells
- Username and password can now be entered as arguments with `--username` and `--password` - does **not** take priority over credentials.json
- Added option to disable saving credentials `SAVE_CREDENTIALS`/`--save-credentials` - will still use credentials.json if already exists
- Default output format for singles is now `{artist}/Single - {song_name}/{artist} - {song_name}.{ext}`

## v0.6.1
- Added support for synced lyrics (unsynced is synced unavailable)
- Can be configured with the `DOWNLOAD_LYRICS` option in config.json or `--download-lyrics=True/False` as a command line argument

## v0.6
**General changes**
- Added "DOWNLOAD_QUALITY" config option. This can be "normal" (96kbks), "high" (160kpbs), "very-high" (320kpbs, premium only) or "auto" which selects the highest format available for your account automatically.
- The "FORCE_PREMIUM" option has been removed, the same result can be achieved with `--download-quality="very-high"`.
- The "BITRATE" option has been renamed "TRANSCODE_BITRATE" as it now only effects transcodes
- FFmpeg is now semi-optional, not having it installed means you are limited to saving music as ogg vorbis.
- Zotify can now be installed with `pip install https://gitlab.com/team-zotify/zotify/-/archive/main/zotify-main.zip`
- Zotify can be ran from any directory with `zotify [args]`, you no longer need to prefix "python" in the command.
- The -s option now takes search input as a command argument, it will still promt you if no search is given.
- The -ls/--liked-songs option has been shrotened to -l/--liked,
- Singles are now stored in their own folders under the artist folder
- Fixed default config not loading on first run
- Now shows asterisks when entering password
- Switched from os.path to pathlib
- New default config locations:
  - Windows: `%AppData%\Roaming\Zotify\config.json`
  - Linux: `~/.config/zotify/config.json`
  - macOS: `~/Library/Application Support/Zotify/config.json`
  - Other/Undetected: `.zotify/config.json` 
  - You can still use `--config-location` to specify a different location.
- New default credential locations:
  - Windows: `%AppData%\Roaming\Zotify\credentials.json`
  - Linux: `~/.local/share/zotify/credentials.json`
  - macOS: `~/Library/Application Support/Zotify/credentials.json`
  - Other/Undetected: `.zotify/credentials.json` 
  - You can still use `--credentials-location` to specify a different file.
- New default music and podcast locations:
  - Windows: `C:\Users\<user>\Music\Zotify Music\` & `C:\Users\<user>\Music\Zotify Podcasts\`
  - Linux & macOS: `~/Music/Zotify Music/` & `~/Music/Zotify Podcasts/`
  - Other/Undetected: `./Zotify Music/` & `./Zotify Podcasts/`
  - You can still use `--root-path` and `--root-podcast-path` respectively to specify a differnt location

**Docker**
- Dockerfile is currently broken, it will be fixed soon. \
The Dockerhub image is now discontinued, we will try to switch to GitLab's container registry.

**Windows installer**
- The Windows installer is unavilable with this release.
- The current installation system will be replaced and a new version will be available with the next release.

## v0.5.2
**General changes**
- Fixed filenaming on Windows
- Fixed removal of special characters metadata
- Can now download different songs with the same name
- Real-time downloads now work correctly
- Removed some debug messages
- Added album_artist metadata
- Added global song archive
- Added SONG_ARCHIVE config value
- Added CREDENTIALS_LOCATION config value
- Added `--download` argument
- Added `--config-location` argument
- Added `--output` for output templating
- Save extra data in .song_ids
- Added options to regulate terminal output
- Direct download support for certain podcasts  
  
**Docker images**
- Remember credentials between container starts
- Use same uid/gid in container as on host  
  
**Windows installer**
- Now comes with full installer
- Dependencies are installed if not found

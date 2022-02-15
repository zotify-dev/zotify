# Changelog
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

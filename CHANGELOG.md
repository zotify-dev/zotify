# Changelog
## v0.6
**General changes**
- Switched from os.path to pathlib
- Zotify can now be installed with pip - 
`pip install https://gitlab.com/team-zotify/zotify/-/archive/main/zotify-main.zip`
- Zotify can be ran from any directory with `zotify [args]`, you no longer need to prefix `python` in the command.
- New default config locations:
  - Windows: `%AppData%\Roaming\Zotify\config.json`
  - Linux: `~/.config/zotify/config.json`
  - macOS: `~/Library/Application Support/Zotify/config.json`
  - You can still use `--config-location` to specify a local config file.

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

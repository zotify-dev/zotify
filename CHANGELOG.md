# Changelog:
### v0.5.2:
**General changes:**
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
  
**Docker images:**
- Remember credentials between container starts
- Use same uid/gid in container as on host  
  
**Windows installer:**
- Now comes with full installer
- Dependencies are installed if not found

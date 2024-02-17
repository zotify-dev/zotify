# STILL IN DEVELOPMENT, EVERYTHING HERE IS SUBJECT TO CHANGE!

## v1.0.0

### BREAKING CHANGES AHEAD

- Most components have been completely rewritten to address some fundamental design issues with the previous codebase, This update will provide a better base for new features in the future.
- ~~Some~~ Most configuration options have been renamed, please check your configuration file.
- There is a new library path for playlists, existing playlists will stay where they are.

### Changes

- Genre metadata available for all tracks
- Boolean command line options are now set like `--save-metadata` or `--no-save-metadata` for True or False
- Setting `--config` (formerly `--config-location`) can be set to "None" to not use any config file
- Search result selector now accepts both comma-seperated and hyphen-seperated values at the same time
- Renamed `--liked`/`-l` to `--liked-tracks`/`-lt`
- Renamed `root_path` and `root_podcast_path` to `music_library` and `podcast_library`
- `--username` and `--password` arguments now take priority over saved credentials
- Regex pattern for cleaning filenames is now OS specific, allowing more usable characters on Linux & macOS.
- On Linux both `config.json` and `credentials.json` are now kept under `$XDG_CONFIG_HOME/zotify/`, (`~/.config/zotify/` by default).
- The output template used is now based on track info rather than search result category
- Search queries with spaces no longer need to be in quotes
- File metadata no longer uses sanitized file metadata, this will result in more accurate metadata.
- Replaced ffmpy with custom implementation providing more tags
- Fixed artist download missing some tracks

### Additions

- New library location for playlists `playlist_library`
- Added new command line arguments
  - `--library`/`-l` overrides both `music_library` and `podcast_library` options similar to `--output`/`-o`
  - `--category`/`-c` will limit search results to a certain type, accepted values are "album", "artist", "playlist", "track", "show", "episode". Accepts multiple choices.
  - `--debug` shows full tracebacks on crash instead of just the final error message
  - Added new shorthand aliases to some options:
    - `-oa` = `--output-album`
    - `-opt` = `--output-playlist-track`
    - `-ope` = `--output-playlist-episode`
    - `-op` = `--output-podcast`
- Search results can be narrowed down using search filters
  - Available filters are 'album', 'artist', 'track', 'year', 'upc', 'tag:hipster', 'tag:new', 'isrc', and 'genre'.
  - The 'artist' and 'year' filters only shows results from the given year or a range (e.g. 1970-1982).
  - The 'album' filter only shows results from the given album(s)
  - The 'genre' filter only shows results from the given genre(s)
  - The 'isrc' and 'track' filters can be used while searching tracks
  - The 'upc', tag:new and tag:hipster filters can only be used while searching albums
    - 'tag:new' filter will show albums released within the past two weeks
    - 'tag:hipster' will only show albums in the lowest 10% of popularity
- Search has been expanded to include podcasts and episodes
- New output placeholders / metadata tags for tracks
  - `{artists}`
  - `{album_artist}`
  - `{album_artists}`
  - `{duration}` (milliseconds)
  - `{explicit}`
  - `{isrc}`
  - `{licensor}`
  - `{popularity}`
  - `{release_date}`
  - `{track_number}`
- Genre information is now more accurate and is always enabled
- Added download option for "liked episodes" `--liked-episodes`/`-le`
- Added `save_metadata` option to fully disable writing track metadata
- Added support for ReplayGain
- Added support for transcoding to wav and wavpack formats
- Unsynced lyrics are saved to a txt file instead of lrc
- Unsynced lyrics can now be embedded directly into file metadata (for supported file types)
- Added new option `save_lyrics_file`
  - This option only affects the external lyrics files
  - Embedded lyrics are controlled with `save_metadata`

### Removals

- Removed "Zotify" ASCII banner
- Removed search prompt, searches can only be done as cli arguments now.
- Removed song archive files
- Removed `{ext}` option in output formats as file extentions are managed automatically
- Removed `split_album_discs` because the same functionality can be achieved by using output formatting
- Removed `print_api_errors` because API errors are now treated like regular errors
- Removed the following config options due to their corresponding features being removed:
  - `bulk_wait_time`
  - `chunk_size`
  - `download_real_time`
  - `md_allgenres`
  - `md_genredelimiter`
  - `metadata_delimiter`
  - `override_auto_wait`
  - `retry_attempts`
  - `save_genres`
  - `temp_download_dir`

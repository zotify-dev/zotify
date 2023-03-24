from argparse import Namespace
from json import dump, load
from pathlib import Path
from sys import platform as PLATFORM
from typing import Any

from zotify.utils import AudioFormat, ImageSize, Quality


ALL_ARTISTS = "all_artists"
ARTWORK_SIZE = "artwork_size"
AUDIO_FORMAT = "audio_format"
CHUNK_SIZE = "chunk_size"
CREATE_PLAYLIST_FILE = "create_playlist_file"
CREDENTIALS = "credentials"
DOWNLOAD_QUALITY = "download_quality"
FFMPEG_ARGS = "ffmpeg_args"
FFMPEG_PATH = "ffmpeg_path"
LANGUAGE = "language"
LYRICS_ONLY = "lyrics_only"
MUSIC_LIBRARY = "music_library"
OUTPUT = "output"
OUTPUT_ALBUM = "output_album"
OUTPUT_PLAYLIST_TRACK = "output_playlist_track"
OUTPUT_PLAYLIST_EPISODE = "output_playlist_episode"
OUTPUT_PODCAST = "output_podcast"
OUTPUT_SINGLE = "output_single"
PATH_ARCHIVE = "path_archive"
PLAYLIST_LIBRARY = "playlist_library"
PODCAST_LIBRARY = "podcast_library"
PRINT_DOWNLOADS = "print_downloads"
PRINT_ERRORS = "print_errors"
PRINT_PROGRESS = "print_progress"
PRINT_SKIPS = "print_skips"
PRINT_WARNINGS = "print_warnings"
REPLACE_EXISTING = "replace_existing"
SAVE_LYRICS = "save_lyrics"
SAVE_METADATA = "save_metadata"
SAVE_SUBTITLES = "save_subtitles"
SKIP_DUPLICATES = "skip_duplicates"
SKIP_PREVIOUS = "skip_previous"
TRANSCODE_BITRATE = "transcode_bitrate"

SYSTEM_PATHS = {
    "win32": Path.home().joinpath("AppData/Roaming/Zotify"),
    "linux": Path.home().joinpath(".config/zotify"),
    "darwin": Path.home().joinpath("Library/Application Support/Zotify"),
}

LIBRARY_PATHS = {
    "music": Path.home().joinpath("Music/Zotify Music"),
    "podcast": Path.home().joinpath("Music/Zotify Podcasts"),
    "playlist": Path.home().joinpath("Music/Zotify Playlists"),
}

CONFIG_PATHS = {
    "conf": SYSTEM_PATHS[PLATFORM].joinpath("config.json"),
    "creds": SYSTEM_PATHS[PLATFORM].joinpath("credentials.json"),
    "archive": SYSTEM_PATHS[PLATFORM].joinpath("track_archive"),
}

OUTPUT_PATHS = {
    "album": "{album_artist}/{album}/{track_number}. {artist} - {title}",
    "podcast": "{podcast}/{episode_number} - {title}",
    "playlist_track": "{playlist}/{playlist_number}. {artist} - {title}",
    "playlist_episode": "{playlist}/{playlist_number}. {episode_number} - {title}",
}

CONFIG_VALUES = {
    CREDENTIALS: {
        "default": CONFIG_PATHS["creds"],
        "type": Path,
        "arg": "--credentials",
        "help": "Path to credentials file",
    },
    PATH_ARCHIVE: {
        "default": CONFIG_PATHS["archive"],
        "type": Path,
        "arg": "--archive",
        "help": "Path to track archive file",
    },
    MUSIC_LIBRARY: {
        "default": LIBRARY_PATHS["music"],
        "type": Path,
        "arg": "--music-library",
        "help": "Path to root of music library",
    },
    PODCAST_LIBRARY: {
        "default": LIBRARY_PATHS["podcast"],
        "type": Path,
        "arg": "--podcast-library",
        "help": "Path to root of podcast library",
    },
    PLAYLIST_LIBRARY: {
        "default": LIBRARY_PATHS["playlist"],
        "type": Path,
        "arg": "--playlist-library",
        "help": "Path to root of playlist library",
    },
    OUTPUT_ALBUM: {
        "default": OUTPUT_PATHS["album"],
        "type": str,
        "arg": "--output-album",
        "help": "File layout for saved albums",
    },
    OUTPUT_PLAYLIST_TRACK: {
        "default": OUTPUT_PATHS["playlist_track"],
        "type": str,
        "arg": "--output-playlist-track",
        "help": "File layout for tracks in a playlist",
    },
    OUTPUT_PLAYLIST_EPISODE: {
        "default": OUTPUT_PATHS["playlist_episode"],
        "type": str,
        "arg": "--output-playlist-episode",
        "help": "File layout for episodes in a playlist",
    },
    OUTPUT_PODCAST: {
        "default": OUTPUT_PATHS["podcast"],
        "type": str,
        "arg": "--output-podcast",
        "help": "File layout for saved podcasts",
    },
    DOWNLOAD_QUALITY: {
        "default": "auto",
        "type": Quality.from_string,
        "choices": list(Quality),
        "arg": "--download-quality",
        "help": "Audio download quality (auto for highest available)",
    },
    ARTWORK_SIZE: {
        "default": "large",
        "type": ImageSize.from_string,
        "choices": list(ImageSize),
        "arg": "--artwork-size",
        "help": "Image size of track's cover art",
    },
    AUDIO_FORMAT: {
        "default": "vorbis",
        "type": AudioFormat,
        "choices": [n.value for n in AudioFormat],
        "arg": "--audio-format",
        "help": "Audio format of final track output",
    },
    TRANSCODE_BITRATE: {
        "default": -1,
        "type": int,
        "arg": "--bitrate",
        "help": "Transcoding bitrate (-1 to use download rate)",
    },
    FFMPEG_PATH: {
        "default": "",
        "type": str,
        "arg": "--ffmpeg-path",
        "help": "Path to ffmpeg binary",
    },
    FFMPEG_ARGS: {
        "default": "",
        "type": str,
        "arg": "--ffmpeg-args",
        "help": "Additional ffmpeg arguments when transcoding",
    },
    SAVE_SUBTITLES: {
        "default": False,
        "type": bool,
        "arg": "--save-subtitles",
        "help": "Save subtitles from podcasts to a .srt file",
    },
    LANGUAGE: {
        "default": "en",
        "type": str,
        "arg": "--language",
        "help": "Language for metadata"
    },
    SAVE_LYRICS: {
        "default": True,
        "type": bool,
        "arg": "--save-lyrics",
        "help": "Save lyrics to a file",
    },
    LYRICS_ONLY: {
        "default": False,
        "type": bool,
        "arg": "--lyrics-only",
        "help": "Only download lyrics and not actual audio",
    },
    CREATE_PLAYLIST_FILE: {
        "default": True,
        "type": bool,
        "arg": "--playlist-file",
        "help": "Save playlist information to an m3u8 file",
    },
    SAVE_METADATA: {
        "default": True,
        "type": bool,
        "arg": "--save-metadata",
        "help": "Save metadata, required for other metadata options",
    },
    ALL_ARTISTS: {
        "default": True,
        "type": bool,
        "arg": "--all-artists",
        "help": "Add all track artists to artist tag in metadata",
    },
    REPLACE_EXISTING: {
        "default": False,
        "type": bool,
        "arg": "--replace-existing",
        "help": "Overwrite existing files with the same name",
    },
    SKIP_PREVIOUS: {
        "default": True,
        "type": bool,
        "arg": "--skip-previous",
        "help": "Skip previously downloaded songs",
    },
    SKIP_DUPLICATES: {
        "default": True,
        "type": bool,
        "arg": "--skip-duplicates",
        "help": "Skip downloading existing track to different album",
    },
    CHUNK_SIZE: {
        "default": 131072,
        "type": int,
        "arg": "--chunk-size",
        "help": "Number of bytes read at a time during download",
    },
    PRINT_DOWNLOADS: {
        "default": False,
        "type": bool,
        "arg": "--print-downloads",
        "help": "Print messages when a song is finished downloading",
    },
    PRINT_PROGRESS: {
        "default": True,
        "type": bool,
        "arg": "--print-progress",
        "help": "Show progress bars",
    },
    PRINT_SKIPS: {
        "default": True,
        "type": bool,
        "arg": "--print-skips",
        "help": "Show messages if a song is being skipped",
    },
    PRINT_WARNINGS: {
        "default": True,
        "type": bool,
        "arg": "--print-warnings",
        "help": "Show warnings",
    },
    PRINT_ERRORS: {
        "default": True,
        "type": bool,
        "arg": "--print-errors",
        "help": "Show errors",
    },
}


class Config:
    __config_file: Path | None
    artwork_size: ImageSize
    audio_format: AudioFormat
    chunk_size: int
    credentials: Path
    download_quality: Quality
    ffmpeg_args: str
    ffmpeg_path: str
    music_library: Path
    language: str
    output_album: str
    output_liked: str
    output_podcast: str
    output_playlist_track: str
    output_playlist_episode: str
    playlist_library: Path
    podcast_library: Path
    print_progress: bool
    save_lyrics: bool
    save_metadata: bool
    transcode_bitrate: int

    def __init__(self, args: Namespace = Namespace()):
        jsonvalues = {}
        if args.config:
            self.__config_file = Path(args.config)
            # Valid config file found
            if self.__config_file.exists():
                with open(self.__config_file, "r", encoding="utf-8") as conf:
                    jsonvalues = load(conf)
            # Remove config file and make a new one
            else:
                self.__config_file.parent.mkdir(parents=True, exist_ok=True)
                jsonvalues = {}
                for key in CONFIG_VALUES:
                    if CONFIG_VALUES[key]["type"] in [str, int, bool]:
                        jsonvalues[key] = CONFIG_VALUES[key]["default"]
                    else:
                        jsonvalues[key] = str(CONFIG_VALUES[key]["default"])
                with open(self.__config_file, "w+", encoding="utf-8") as conf:
                    dump(jsonvalues, conf, indent=4)

        for key in CONFIG_VALUES:
            # Override config with commandline arguments
            if key in vars(args) and vars(args)[key] is not None:
                setattr(self, key, self.__parse_arg_value(key, vars(args)[key]))
            # If no command option specified use config
            elif key in jsonvalues:
                setattr(self, key, self.__parse_arg_value(key, jsonvalues[key]))
            # Use default values for missing keys
            else:
                setattr(
                    self,
                    key,
                    self.__parse_arg_value(key, CONFIG_VALUES[key]["default"]),
                )
        else:
            self.__config_file = None

        # Make "output" arg override all output_* options
        if args.output:
            self.output_album = args.output
            self.output_liked = args.output
            self.output_podcast = args.output
            self.output_playlist_track = args.output
            self.output_playlist_episode = args.output

    @staticmethod
    def __parse_arg_value(key: str, value: Any) -> Any:
        config_type = CONFIG_VALUES[key]["type"]
        if type(value) == config_type:
            return value
        elif config_type == Path:
            return Path(value).expanduser()
        elif config_type == AudioFormat:
            return AudioFormat(value)
        elif config_type == ImageSize.from_string:
            return ImageSize.from_string(value)
        elif config_type == Quality.from_string:
            return Quality.from_string(value)
        else:
            raise TypeError("Invalid Type: " + value)

    def get(self, key: str) -> Any:
        """
        Gets a value from config
        Args:
            key: config attribute to return value of
        Returns:
            Value of key
        """
        return getattr(self, key)

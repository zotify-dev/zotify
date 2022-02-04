import json
import sys
from pathlib import Path, PurePath
from typing import Any


ROOT_PATH = 'ROOT_PATH'
ROOT_PODCAST_PATH = 'ROOT_PODCAST_PATH'
SKIP_EXISTING_FILES = 'SKIP_EXISTING_FILES'
SKIP_PREVIOUSLY_DOWNLOADED = 'SKIP_PREVIOUSLY_DOWNLOADED'
DOWNLOAD_FORMAT = 'DOWNLOAD_FORMAT'
FORCE_PREMIUM = 'FORCE_PREMIUM'
ANTI_BAN_WAIT_TIME = 'ANTI_BAN_WAIT_TIME'
OVERRIDE_AUTO_WAIT = 'OVERRIDE_AUTO_WAIT'
CHUNK_SIZE = 'CHUNK_SIZE'
SPLIT_ALBUM_DISCS = 'SPLIT_ALBUM_DISCS'
DOWNLOAD_REAL_TIME = 'DOWNLOAD_REAL_TIME'
LANGUAGE = 'LANGUAGE'
BITRATE = 'BITRATE'
SONG_ARCHIVE = 'SONG_ARCHIVE'
CREDENTIALS_LOCATION = 'CREDENTIALS_LOCATION'
OUTPUT = 'OUTPUT'
PRINT_SPLASH = 'PRINT_SPLASH'
PRINT_SKIPS = 'PRINT_SKIPS'
PRINT_DOWNLOAD_PROGRESS = 'PRINT_DOWNLOAD_PROGRESS'
PRINT_ERRORS = 'PRINT_ERRORS'
PRINT_DOWNLOADS = 'PRINT_DOWNLOADS'
PRINT_API_ERRORS = 'PRINT_API_ERRORS'
TEMP_DOWNLOAD_DIR = 'TEMP_DOWNLOAD_DIR'
MD_ALLGENRES = 'MD_ALLGENRES'
MD_GENREDELIMITER = 'MD_GENREDELIMITER'
PRINT_PROGRESS_INFO = 'PRINT_PROGRESS_INFO'
PRINT_WARNINGS = 'PRINT_WARNINGS'
RETRY_ATTEMPTS = 'RETRY_ATTEMPTS'

CONFIG_VALUES = {
    ROOT_PATH:                  { 'default': './Zotify Music/',    'type': str,  'arg': '--root-path'                  },
    ROOT_PODCAST_PATH:          { 'default': './Zotify Podcasts/', 'type': str,  'arg': '--root-podcast-path'          },
    SKIP_EXISTING_FILES:        { 'default': 'True',               'type': bool, 'arg': '--skip-existing-files'        },
    SKIP_PREVIOUSLY_DOWNLOADED: { 'default': 'False',              'type': bool, 'arg': '--skip-previously-downloaded' },
    RETRY_ATTEMPTS:             { 'default': '5',                  'type': int,  'arg': '--retry-attemps'              },
    DOWNLOAD_FORMAT:            { 'default': 'ogg',                'type': str,  'arg': '--download-format'            },
    FORCE_PREMIUM:              { 'default': 'False',              'type': bool, 'arg': '--force-premium'              },
    ANTI_BAN_WAIT_TIME:         { 'default': '1',                  'type': int,  'arg': '--anti-ban-wait-time'         },
    OVERRIDE_AUTO_WAIT:         { 'default': 'False',              'type': bool, 'arg': '--override-auto-wait'         },
    CHUNK_SIZE:                 { 'default': '50000',              'type': int,  'arg': '--chunk-size'                 },
    SPLIT_ALBUM_DISCS:          { 'default': 'False',              'type': bool, 'arg': '--split-album-discs'          },
    DOWNLOAD_REAL_TIME:         { 'default': 'False',              'type': bool, 'arg': '--download-real-time'         },
    LANGUAGE:                   { 'default': 'en',                 'type': str,  'arg': '--language'                   },
    BITRATE:                    { 'default': '',                   'type': str,  'arg': '--bitrate'                    },
    SONG_ARCHIVE:               { 'default': '.song_archive',      'type': str,  'arg': '--song-archive'               },
    CREDENTIALS_LOCATION:       { 'default': 'credentials.json',   'type': str,  'arg': '--credentials-location'       },
    OUTPUT:                     { 'default': '',                   'type': str,  'arg': '--output'                     },
    PRINT_SPLASH:               { 'default': 'False',              'type': bool, 'arg': '--print-splash'               },
    PRINT_SKIPS:                { 'default': 'True',               'type': bool, 'arg': '--print-skips'                },
    PRINT_DOWNLOAD_PROGRESS:    { 'default': 'True',               'type': bool, 'arg': '--print-download-progress'    },
    PRINT_ERRORS:               { 'default': 'True',               'type': bool, 'arg': '--print-errors'               },
    PRINT_DOWNLOADS:            { 'default': 'False',              'type': bool, 'arg': '--print-downloads'            },
    PRINT_API_ERRORS:           { 'default': 'False',              'type': bool, 'arg': '--print-api-errors'           },
    PRINT_PROGRESS_INFO:        { 'default': 'True',               'type': bool, 'arg': '--print-progress-info'        },
    PRINT_WARNINGS:             { 'default': 'True',               'type': bool, 'arg': '--print-warnings'             },
    MD_ALLGENRES:               { 'default': 'False',              'type': bool, 'arg': '--md-allgenres'               },
    MD_GENREDELIMITER:          { 'default': ';',                  'type': str,  'arg': '--md-genredelimiter'          },
    TEMP_DOWNLOAD_DIR:          { 'default': '',                   'type': str,  'arg': '--temp-download-dir'          }
}

OUTPUT_DEFAULT_PLAYLIST = '{playlist}/{artist} - {song_name}.{ext}'
OUTPUT_DEFAULT_PLAYLIST_EXT = '{playlist}/{playlist_num} - {artist} - {song_name}.{ext}'
OUTPUT_DEFAULT_LIKED_SONGS = 'Liked Songs/{artist} - {song_name}.{ext}'
OUTPUT_DEFAULT_SINGLE = '{artist} - {song_name}.{ext}'
OUTPUT_DEFAULT_ALBUM = '{artist}/{album}/{album_num} - {artist} - {song_name}.{ext}'


class Config:
    Values = {}

    @classmethod
    def load(cls, args) -> None:
        system_paths = {
            'win32': Path.home() / 'AppData/Roaming/Zotify',
            'linux': Path.home() / '.config/zotify',
            'darwin': Path.home() / 'Library/Application Support/Zotify'
        }
        config_fp = system_paths[sys.platform] / 'config.json'
        if args.config_location:
            config_fp = args.config_location

        true_config_file_path = Path(config_fp).expanduser()

        # Load config from zconfig.json
        Path(PurePath(true_config_file_path).parent).mkdir(parents=True, exist_ok=True)
        if not Path(true_config_file_path).exists():
            with open(true_config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(cls.get_default_json(), config_file, indent=4)
        with open(true_config_file_path, encoding='utf-8') as config_file:
            jsonvalues = json.load(config_file)
            cls.Values = {}
            for key in CONFIG_VALUES:
                if key in jsonvalues:
                    cls.Values[key] = cls.parse_arg_value(key, jsonvalues[key])

        # Add default values for missing keys

        for key in CONFIG_VALUES:
            if key not in cls.Values:
                cls.Values[key] = cls.parse_arg_value(key, CONFIG_VALUES[key]['default'])

        # Override config from commandline arguments

        for key in CONFIG_VALUES:
            if key.lower() in vars(args) and vars(args)[key.lower()] is not None:
                cls.Values[key] = cls.parse_arg_value(key, vars(args)[key.lower()])

        if args.no_splash:
            cls.Values[PRINT_SPLASH] = False

    @classmethod
    def get_default_json(cls) -> Any:
        r = {}
        for key in CONFIG_VALUES:
            r[key] = CONFIG_VALUES[key]['default']
        return r

    @classmethod
    def parse_arg_value(cls, key: str, value: Any) -> Any:
        if type(value) == CONFIG_VALUES[key]['type']:
            return value
        if CONFIG_VALUES[key]['type'] == str:
            return str(value)
        if CONFIG_VALUES[key]['type'] == int:
            return int(value)
        if CONFIG_VALUES[key]['type'] == bool:
            if str(value).lower() in ['yes', 'true', '1']:
                return True
            if str(value).lower() in ['no', 'false', '0']:
                return False
            raise ValueError("Not a boolean: " + value)
        raise ValueError("Unknown Type: " + value)

    @classmethod
    def get(cls, key: str) -> Any:
        return cls.Values.get(key)

    @classmethod
    def get_root_path(cls) -> str:
        # return PurePath(Path.cwd()).joinpath(cls.get(ROOT_PATH))
        return PurePath(Path(cls.get(ROOT_PATH)).expanduser())

    @classmethod
    def get_root_podcast_path(cls) -> str:
        # return PurePath(Path.cwd()).joinpath(cls.get(ROOT_PODCAST_PATH))
        return PurePath(Path(cls.get(ROOT_PODCAST_PATH)).expanduser())

    @classmethod
    def get_skip_existing_files(cls) -> bool:
        return cls.get(SKIP_EXISTING_FILES)

    @classmethod
    def get_skip_previously_downloaded(cls) -> bool:
        return cls.get(SKIP_PREVIOUSLY_DOWNLOADED)

    @classmethod
    def get_split_album_discs(cls) -> bool:
        return cls.get(SPLIT_ALBUM_DISCS)

    @classmethod
    def get_chunk_size(cls) -> int:
        return cls.get(CHUNK_SIZE)

    @classmethod
    def get_override_auto_wait(cls) -> bool:
        return cls.get(OVERRIDE_AUTO_WAIT)

    @classmethod
    def get_force_premium(cls) -> bool:
        return cls.get(FORCE_PREMIUM)

    @classmethod
    def get_download_format(cls) -> str:
        return cls.get(DOWNLOAD_FORMAT)

    @classmethod
    def get_anti_ban_wait_time(cls) -> int:
        return cls.get(ANTI_BAN_WAIT_TIME)

    @classmethod
    def get_language(cls) -> str:
        return cls.get(LANGUAGE)

    @classmethod
    def get_download_real_time(cls) -> bool:
        return cls.get(DOWNLOAD_REAL_TIME)

    @classmethod
    def get_bitrate(cls) -> str:
        return cls.get(BITRATE)

    @classmethod
    def get_song_archive(cls) -> str:
        return PurePath(cls.get_root_path()).joinpath(cls.get(SONG_ARCHIVE))

    @classmethod
    def get_credentials_location(cls) -> str:
        return PurePath(Path.cwd()).joinpath(cls.get(CREDENTIALS_LOCATION))

    @classmethod
    def get_temp_download_dir(cls) -> str:
        if cls.get(TEMP_DOWNLOAD_DIR) == '':
            return ''
        return PurePath(cls.get_root_path()).joinpath(cls.get(TEMP_DOWNLOAD_DIR))
    
    @classmethod
    def get_all_genres(cls) -> bool:
        return cls.get(MD_ALLGENRES)

    @classmethod
    def get_all_genres_delimiter(cls) -> bool:
        return cls.get(MD_GENREDELIMITER)
    
    @classmethod
    def get_output(cls, mode: str) -> str:
        v = cls.get(OUTPUT)
        if v:
            return v
        if mode == 'playlist':
            if cls.get_split_album_discs():
                split = PurePath(OUTPUT_DEFAULT_PLAYLIST).parent
                return PurePath(split).joinpath('Disc {disc_number}').joinpath(split)
            return OUTPUT_DEFAULT_PLAYLIST
        if mode == 'extplaylist':
            if cls.get_split_album_discs():
                split = PurePath(OUTPUT_DEFAULT_PLAYLIST_EXT).parent
                return PurePath(split).joinpath('Disc {disc_number}').joinpath(split)
            return OUTPUT_DEFAULT_PLAYLIST_EXT
        if mode == 'liked':
            if cls.get_split_album_discs():
                split = PurePath(OUTPUT_DEFAULT_LIKED_SONGS).parent
                return PurePath(split).joinpath('Disc {disc_number}').joinpath(split)
            return OUTPUT_DEFAULT_LIKED_SONGS
        if mode == 'single':
            if cls.get_split_album_discs():
                split = PurePath(OUTPUT_DEFAULT_SINGLE).parent
                return PurePath(split).joinpath('Disc {disc_number}').joinpath(split)
            return OUTPUT_DEFAULT_SINGLE
        if mode == 'album':
            if cls.get_split_album_discs():
                split = PurePath(OUTPUT_DEFAULT_ALBUM).parent
                return PurePath(split).joinpath('Disc {disc_number}').joinpath(split)
            return OUTPUT_DEFAULT_ALBUM
        raise ValueError()

    @classmethod
    def get_retry_attempts(cls) -> int:
        return cls.get(RETRY_ATTEMPTS)
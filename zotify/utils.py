from argparse import Action, ArgumentError
from enum import Enum, IntEnum
from re import IGNORECASE, sub
from sys import platform as PLATFORM
from typing import NamedTuple

from librespot.audio.decoders import AudioQuality
from librespot.util import Base62, bytes_to_hex
from requests import get

API_URL = "https://api.sp" + "otify.com/v1/"
IMG_URL = "https://i.s" + "cdn.co/image/"
LYRICS_URL = "https://sp" + "client.wg.sp" + "otify.com/color-lyrics/v2/track/"
BASE62 = Base62.create_instance_with_inverted_character_set()


class AudioCodec(NamedTuple):
    ext: str
    name: str


class AudioFormat(Enum):
    AAC = AudioCodec("aac", "m4a")
    FDK_AAC = AudioCodec("fdk_aac", "m4a")
    FLAC = AudioCodec("flac", "flac")
    MP3 = AudioCodec("mp3", "mp3")
    OPUS = AudioCodec("opus", "ogg")
    VORBIS = AudioCodec("vorbis", "ogg")
    WAV = AudioCodec("wav", "wav")
    WV = AudioCodec("wavpack", "wv")


class Quality(Enum):
    NORMAL = AudioQuality.NORMAL  # ~96kbps
    HIGH = AudioQuality.HIGH  # ~160kbps
    VERY_HIGH = AudioQuality.VERY_HIGH  # ~320kbps
    AUTO = None  # Highest quality available for account

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_string(s):
        try:
            return Quality[s.upper()]
        except Exception:
            return s


class ImageSize(IntEnum):
    SMALL = 0  # 64px
    MEDIUM = 1  # 300px
    LARGE = 2  # 640px

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_string(s):
        try:
            return ImageSize[s.upper()]
        except Exception:
            return s


class OptionalOrFalse(Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs="?",
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None and not option_string.startswith("--no-"):
            raise ArgumentError(self, "expected 1 argument")
        setattr(
            namespace,
            self.dest,
            values if not option_string.startswith("--no-") else False,
        )


def fix_filename(filename: str, substitute: str = "_", platform: str = PLATFORM) -> str:
    """
    Replace invalid characters on Linux/Windows/MacOS with underscores.
    Original list from https://stackoverflow.com/a/31976060/819417
    Trailing spaces & periods are ignored on Windows.
    Args:
        filename: The name of the file to repair
        platform: Host operating system
        substitute: Replacement character for disallowed characters
    Returns:
        Filename with replaced characters
    """
    if platform == "linux":
        regex = r"[/\0]|^(?![^.])|[\s]$"
    elif platform == "darwin":
        regex = r"[/\0:]|^(?![^.])|[\s]$"
    else:
        regex = r"[/\\:|<>\"?*\0-\x1f]|^(AUX|COM[1-9]|CON|LPT[1-9]|NUL|PRN)(?![^.])|^\s|[\s.]$"
    return sub(regex, substitute, str(filename), flags=IGNORECASE)


def download_cover_art(images: list, size: ImageSize) -> bytes:
    """
    Returns image data of cover art
    Args:
        images: list of retrievable images
        size: Desired size in pixels of cover art, can be 640, 300, or 64
    Returns:
        Image data of cover art
    """
    return get(images[size.value]["url"]).content


def str_to_bool(value: str) -> bool:
    if value.lower() in ["yes", "y", "true"]:
        return True
    if value.lower() in ["no", "n", "false"]:
        return False
    raise TypeError("Not a boolean: " + value)


def bytes_to_base62(id: bytes) -> str:
    return BASE62.encode(id, 22).decode()


def b62_to_hex(base62: str) -> str:
    return bytes_to_hex(BASE62.decode(base62.encode(), 16))

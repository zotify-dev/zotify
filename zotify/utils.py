from argparse import Action, ArgumentError
from enum import Enum, IntEnum
from pathlib import Path
from re import IGNORECASE, sub
from typing import Any, NamedTuple

from librespot.audio.decoders import AudioQuality
from librespot.util import Base62

BASE62 = Base62.create_instance_with_inverted_character_set()


class AudioCodec(NamedTuple):
    name: str
    ext: str


class AudioFormat(Enum):
    AAC = AudioCodec("aac", "m4a")
    FDK_AAC = AudioCodec("fdk_aac", "m4a")
    FLAC = AudioCodec("flac", "flac")
    MP3 = AudioCodec("mp3", "mp3")
    OPUS = AudioCodec("opus", "ogg")
    VORBIS = AudioCodec("vorbis", "ogg")
    WAV = AudioCodec("wav", "wav")
    WAVPACK = AudioCodec("wavpack", "wv")

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_string(s):
        try:
            return AudioFormat[s.upper()]
        except Exception:
            return s


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


class MetadataEntry:
    name: str
    value: Any
    string: str

    def __init__(self, name: str, value: Any, string_value: str | None = None):
        """
        Holds metadata entries
        args:
            name: name of metadata key
            value: Value to use in metadata tags
            string_value: Value when used in output formatting, if none is provided
            will use value from previous argument.
        """
        self.name = name

        if isinstance(value, tuple):
            value = "\0".join(value)
        self.value = value

        if string_value is None:
            string_value = self.value
        if isinstance(string_value, list):
            string_value = ", ".join(string_value)
        self.string = str(string_value)


class PlayableType(Enum):
    TRACK = "track"
    EPISODE = "episode"


class PlayableData(NamedTuple):
    type: PlayableType
    id: str
    library: Path
    output_template: str
    metadata: list[MetadataEntry] = []


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
        if values is not None:
            raise ArgumentError(self, "expected 0 arguments")
        setattr(
            namespace,
            self.dest,
            (
                True
                if not (
                    option_string.startswith("--no-")
                    or option_string.startswith("--dont-")
                )
                else False
            ),
        )


def fix_filename(
    filename: str,
    substitute: str = "_",
) -> str:
    """
    Replace invalid characters. Trailing spaces & periods are ignored.
    Original list from https://stackoverflow.com/a/31976060/819417
    Args:
        filename: The name of the file to repair
        substitute: Replacement character for disallowed characters
    Returns:
        Filename with replaced characters
    """
    regex = (
        r"[/\\:|<>\"?*\0-\x1f]|^(AUX|COM[1-9]|CON|LPT[1-9]|NUL|PRN)(?![^.])|^\s|[\s.]$"
    )
    return sub(regex, substitute, str(filename), flags=IGNORECASE)


def bytes_to_base62(id: bytes) -> str:
    """
    Converts bytes to base62
    Args:
        id: bytes
    Returns:
        base62
    """
    return BASE62.encode(id, 22).decode()

from enum import Enum
from sys import stderr

from tqdm import tqdm

from zotify.config import (
    PRINT_DOWNLOADS,
    PRINT_ERRORS,
    PRINT_PROGRESS,
    PRINT_SKIPS,
    PRINT_WARNINGS,
    Config,
)


class LogChannel(Enum):
    SKIPS = PRINT_SKIPS
    PROGRESS = PRINT_PROGRESS
    ERRORS = PRINT_ERRORS
    WARNINGS = PRINT_WARNINGS
    DOWNLOADS = PRINT_DOWNLOADS


class Logger:
    __config: Config = Config()

    @classmethod
    def __init__(cls, config: Config):
        cls.__config = config

    @classmethod
    def log(cls, channel: LogChannel, msg: str) -> None:
        """
        Prints a message to console if the print channel is enabled
        Args:
            channel: LogChannel to print to
            msg: Message to log
        """
        if cls.__config.get(channel.value):
            if channel == LogChannel.ERRORS:
                print(msg, file=stderr)
            else:
                print(msg)

    @classmethod
    def progress(
        cls,
        iterable=None,
        desc=None,
        total=None,
        leave=False,
        position=0,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) -> tqdm:
        """
        Prints progress bar
        Returns:
            tqdm decorated iterable
        """
        return tqdm(
            iterable=iterable,
            desc=desc,
            total=total,
            disable=not cls.__config.print_progress,
            leave=leave,
            position=position,
            unit=unit,
            unit_scale=unit_scale,
            unit_divisor=unit_divisor,
        )

    @classmethod
    def print_loader(cls, msg: str) -> None:
        """
        Prints animated loading symbol
        Args:
            msg: Message to display
        """
        if cls.__config.print_progress:
            print(msg, flush=True, end="")

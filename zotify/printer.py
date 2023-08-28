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


class PrintChannel(Enum):
    SKIPS = PRINT_SKIPS
    PROGRESS = PRINT_PROGRESS
    ERRORS = PRINT_ERRORS
    WARNINGS = PRINT_WARNINGS
    DOWNLOADS = PRINT_DOWNLOADS


class Printer:
    __config: Config

    @classmethod
    def __init__(cls, config: Config):
        cls.__config = config

    @classmethod
    def print(cls, channel: PrintChannel, msg: str) -> None:
        """
        Prints a message to console if the print channel is enabled
        Args:
            channel: PrintChannel to print to
            msg: Message to print
        """
        if cls.__config.get(channel.value):
            if channel == PrintChannel.ERRORS:
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
        unit="it",
        unit_scale=False,
        unit_divisor=1000,
        disable: bool = False,
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
            disable=disable,  # cls.__config.print_progress,
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
            msg: Message to print
        """
        if cls.__config.print_progress:
            print(msg, flush=True, end="")

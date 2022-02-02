import sys
from enum import Enum
from tqdm import tqdm

from zotify.config import *
from zotify.zotify import Zotify


class PrintChannel(Enum):
    SPLASH = PRINT_SPLASH
    SKIPS = PRINT_SKIPS
    DOWNLOAD_PROGRESS = PRINT_DOWNLOAD_PROGRESS
    ERRORS = PRINT_ERRORS
    WARNINGS = PRINT_WARNINGS
    DOWNLOADS = PRINT_DOWNLOADS
    API_ERRORS = PRINT_API_ERRORS
    PROGRESS_INFO = PRINT_PROGRESS_INFO


ERROR_CHANNEL = [PrintChannel.ERRORS, PrintChannel.API_ERRORS]


class Printer:
    @staticmethod
    def print(channel: PrintChannel, msg: str) -> None:
        if Zotify.CONFIG.get(channel.value):
            if channel in ERROR_CHANNEL:
                print(msg, file=sys.stderr)
            else:
                print(msg)

    @staticmethod
    def print_loader(channel: PrintChannel, msg: str) -> None:
        if Zotify.CONFIG.get(channel.value):
            print(msg, flush=True, end="")

    @staticmethod
    def progress(iterable=None, desc=None, total=None, unit='it', disable=False, unit_scale=False, unit_divisor=1000):
        if not Zotify.CONFIG.get(PrintChannel.DOWNLOAD_PROGRESS.value):
            disable = True
        return tqdm(iterable=iterable, desc=desc, total=total, disable=disable, unit=unit, unit_scale=unit_scale, unit_divisor=unit_divisor)

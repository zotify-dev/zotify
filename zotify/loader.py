# load symbol from:
# https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running
from __future__ import annotations

from itertools import cycle
from shutil import get_terminal_size
from sys import platform
from threading import Thread
from time import sleep

from zotify.logger import Logger


class Loader:
    """
    Busy symbol.

    Can be called inside a context:

    with Loader("This take some Time..."):
        # do something
        pass
    """

    def __init__(self, desc="Loading...", end="", timeout=0.1, mode="std3") -> None:
        """
        A loader-like context manager
        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self.__thread = Thread(target=self.__animate, daemon=True)
        if platform == "win32":
            self.steps = ["/", "-", "\\", "|"]
        else:
            self.steps = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]

        self.done = False

    def start(self) -> Loader:
        self.__thread.start()
        return self

    def __animate(self) -> None:
        for c in cycle(self.steps):
            if self.done:
                break
            Logger.print_loader(f"\r {c} {self.desc} ")
            sleep(self.timeout)

    def __enter__(self) -> None:
        self.start()

    def stop(self) -> None:
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        Logger.print_loader("\r" + " " * cols)

        if self.end != "":
            Logger.print_loader(f"\r{self.end}")

    def __exit__(self, exc_type, exc_value, tb) -> None:
        # handle exceptions with those variables ^
        self.stop()

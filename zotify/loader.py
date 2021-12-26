# load symbol from:
# https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running

# imports
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

from termoutput import Printer


class Loader:
    """Busy symbol.

    Can be called inside a context:

    with Loader("This take some Time..."):
        # do something
        pass
    """
    def __init__(self, chan, desc="Loading...", end='', timeout=0.1, mode='std1'):
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
        self.channel = chan

        self._thread = Thread(target=self._animate, daemon=True)
        if mode == 'std1':
            self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        elif mode == 'std2':
            self.steps = ["◜","◝","◞","◟"]
        elif mode == 'std3':
            self.steps = ["😐 ","😐 ","😮 ","😮 ","😦 ","😦 ","😧 ","😧 ","🤯 ","💥 ","✨ ","\u3000 ","\u3000 ","\u3000 "]
        elif mode == 'prog':
            self.steps = ["[∙∙∙]","[●∙∙]","[∙●∙]","[∙∙●]","[∙∙∙]"]

        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            Printer.print_loader(self.channel, f"\r\t{c} {self.desc} ")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        Printer.print_loader(self.channel, "\r" + " " * cols)

        if self.end != "":
            Printer.print_loader(self.channel, f"\r{self.end}")

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()

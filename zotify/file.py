from errno import ENOENT
from pathlib import Path
from subprocess import Popen, PIPE
from typing import Any

from music_tag import load_file
from mutagen.oggvorbis import OggVorbisHeaderError

from zotify.utils import AudioFormat


# fmt: off
class TranscodingError(RuntimeError): ...
class TargetExistsError(FileExistsError, TranscodingError): ...
class FFmpegNotFoundError(FileNotFoundError, TranscodingError): ...
class FFmpegExecutionError(OSError, TranscodingError): ...
# fmt: on


class LocalFile:
    def __init__(
        self,
        path: Path,
        audio_format: AudioFormat | None = None,
        bitrate: int | None = None,
    ):
        self.__path = path
        self.__bitrate = bitrate
        if audio_format:
            self.__audio_format = audio_format

    def transcode(
        self,
        audio_format: AudioFormat | None = None,
        bitrate: int | None = None,
        replace: bool = False,
        ffmpeg: str = "ffmpeg",
        opt_args: list[str] = [],
    ) -> None:
        """
        Use ffmpeg to transcode a saved audio file
        Args:
            audio_format: Audio format to transcode file to
            bitrate: Bitrate to transcode file to in kbps
            replace: Replace existing file
            ffmpeg: Location of FFmpeg binary
            opt_args: Additional arguments to pass to ffmpeg
        """
        if audio_format is not None:
            new_ext = audio_format.value.ext
        else:
            new_ext = self.__audio_format.value.ext
        cmd = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(self.__path),
        ]
        newpath = self.__path.parent.joinpath(
            self.__path.name.rsplit(".", 1)[0] + new_ext
        )
        if self.__path == newpath:
            raise TargetExistsError(
                f"Transcoding Error: Cannot overwrite source, target file is already a {self.__audio_format} file."
            )

        cmd.extend(["-b:a", str(bitrate) + "k"]) if bitrate else None
        cmd.extend(["-c:a", audio_format.value.name]) if audio_format else None
        cmd.extend(opt_args)
        cmd.append(str(newpath))

        try:
            process = Popen(cmd, stdin=PIPE)
            process.wait()
        except OSError as e:
            if e.errno == ENOENT:
                raise FFmpegNotFoundError("Transcoding Error: FFmpeg was not found")
            else:
                raise
        if process.returncode != 0:
            raise FFmpegExecutionError(
                f'Transcoding Error: `{" ".join(cmd)}` failed with error code {process.returncode}'
            )

        if replace:
            self.__path.unlink()
        self.__path = newpath
        self.__bitrate = bitrate
        if audio_format:
            self.__audio_format = audio_format

    def write_metadata(self, metadata: dict[str, Any]) -> None:
        """
        Write metadata to file
        Args:
            metadata: key-value metadata dictionary
        """
        f = load_file(self.__path)
        f.save()
        for k, v in metadata.items():
            try:
                f[k] = str(v)
            except KeyError:
                pass
        try:
            f.save()
        except OggVorbisHeaderError:
            pass  # Thrown when using untranscoded file, nothing breaks.

    def write_cover_art(self, image: bytes) -> None:
        """
        Write cover artwork to file
        Args:
            image: raw image data
        """
        f = load_file(self.__path)
        f["artwork"] = image
        try:
            f.save()
        except OggVorbisHeaderError:
            pass

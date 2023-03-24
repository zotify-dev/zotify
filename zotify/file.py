from errno import ENOENT
from pathlib import Path
from subprocess import Popen, PIPE
from typing import Any

from music_tag import load_file
from mutagen.oggvorbis import OggVorbisHeaderError

from zotify.utils import AudioFormat, ExtMap


# fmt: off
class TranscodingError(RuntimeError): ...
class TargetExistsError(FileExistsError, TranscodingError): ...
class FFmpegNotFoundError(FileNotFoundError, TranscodingError): ...
class FFmpegExecutionError(OSError, TranscodingError): ...
# fmt: on


class LocalFile:
    audio_format: AudioFormat

    def __init__(
        self,
        path: Path,
        audio_format: AudioFormat | None = None,
        bitrate: int | None = None,
    ):
        self.path = path
        self.bitrate = bitrate
        if audio_format:
            self.audio_format = audio_format

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
        if audio_format:
            new_ext = ExtMap[audio_format.value]
        else:
            new_ext = ExtMap[self.audio_format.value]
        cmd = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(self.path),
        ]
        newpath = self.path.parent.joinpath(
            self.path.name.rsplit(".", 1)[0] + new_ext.value
        )
        if self.path == newpath:
            raise TargetExistsError(
                f"Transcoding Error: Cannot overwrite source, target file is already a {self.audio_format} file."
            )

        cmd.extend(["-b:a", str(bitrate) + "k"]) if bitrate else None
        cmd.extend(["-c:a", audio_format.value]) if audio_format else None
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
            Path(self.path).unlink()
        self.path = newpath
        self.bitrate = bitrate
        if audio_format:
            self.audio_format = audio_format

    def write_metadata(self, metadata: dict[str, Any]) -> None:
        """
        Write metadata to file
        Args:
            metadata: key-value metadata dictionary
        """
        f = load_file(self.path)
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
        f = load_file(self.path)
        f["artwork"] = image
        try:
            f.save()
        except OggVorbisHeaderError:
            pass

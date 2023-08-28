from errno import ENOENT
from pathlib import Path
from subprocess import PIPE, Popen

from music_tag import load_file
from mutagen.oggvorbis import OggVorbisHeaderError

from zotify.utils import AudioFormat, MetadataEntry


class TranscodingError(RuntimeError):
    ...


class LocalFile:
    def __init__(
        self,
        path: Path,
        audio_format: AudioFormat | None = None,
        bitrate: int = -1,
    ):
        self.__path = path
        self.__audio_format = audio_format
        self.__bitrate = bitrate

    def transcode(
        self,
        audio_format: AudioFormat | None = None,
        bitrate: int = -1,
        replace: bool = False,
        ffmpeg: str = "",
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
        if not audio_format:
            audio_format = self.__audio_format
        if audio_format:
            ext = audio_format.value.ext
        else:
            ext = self.__path.suffix[1:]

        cmd = [
            ffmpeg if ffmpeg != "" else "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(self.__path),
        ]
        path = self.__path.parent.joinpath(
            f'{self.__path.name.rsplit(".", 1)[0]}.{ext}'
        )
        if self.__path == path:
            raise TranscodingError(
                f"Cannot overwrite source, target file {path} already exists."
            )

        cmd.extend(["-b:a", str(bitrate) + "k"]) if bitrate > 0 else None
        cmd.extend(["-c:a", audio_format.value.ext]) if audio_format else None
        cmd.extend(opt_args)
        cmd.append(str(path))

        try:
            process = Popen(cmd, stdin=PIPE)
            process.wait()
        except OSError as e:
            if e.errno == ENOENT:
                raise TranscodingError("FFmpeg was not found")
            else:
                raise
        if process.returncode != 0:
            raise TranscodingError(
                f'`{" ".join(cmd)}` failed with error code {process.returncode}'
            )

        if replace:
            self.__path.unlink()
        self.__path = path
        self.__audio_format = audio_format
        self.__bitrate = bitrate

    def write_metadata(self, metadata: list[MetadataEntry]) -> None:
        """
        Write metadata to file
        Args:
            metadata: key-value metadata dictionary
        """
        f = load_file(self.__path)
        f.save()
        for m in metadata:
            try:
                f[m.name] = m.value
            except KeyError:
                if m.name == "album_artist":
                    f["albumartist"] = m.value
                if m.name == "artists":
                    f["artist"] = m.value
                if m.name == "date":
                    f["year"] = m.value
                if m.name == "disc":
                    f["discnumber"] = m.value
                if m.name == "track_number":
                    f["tracknumber"] = m.value
                try:
                    if m.name == "duration":
                        f["#length"] = m.value
                except KeyError:
                    continue
                except NotImplementedError:
                    continue
                if m.name == "replaygain_track_gain":
                    f["replaygaintrackgain"] = m.value
                continue
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
            pass  # Thrown when using untranscoded file, nothing breaks.

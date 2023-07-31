from math import floor
from pathlib import Path
from typing import Any

from librespot.core import PlayableContentFeeder
from librespot.structure import GeneralAudioStream
from librespot.util import bytes_to_hex
from requests import get

from zotify.file import LocalFile
from zotify.printer import Printer
from zotify.utils import (
    IMG_URL,
    LYRICS_URL,
    AudioFormat,
    ImageSize,
    MetadataEntry,
    bytes_to_base62,
    fix_filename,
)


class Lyrics:
    def __init__(self, lyrics: dict, **kwargs):
        self.lines = []
        self.sync_type = lyrics["syncType"]
        for line in lyrics["lines"]:
            self.lines.append(line["words"] + "\n")
        if self.sync_type == "line_synced":
            self.lines_synced = []
            for line in lyrics["lines"]:
                timestamp = int(line["start_time_ms"])
                ts_minutes = str(floor(timestamp / 60000)).zfill(2)
                ts_seconds = str(floor((timestamp % 60000) / 1000)).zfill(2)
                ts_millis = str(floor(timestamp % 1000))[:2].zfill(2)
                self.lines_synced.append(
                    f"[{ts_minutes}:{ts_seconds}.{ts_millis}]{line.words}\n"
                )

    def save(self, path: Path, prefer_synced: bool = True) -> None:
        """
        Saves lyrics to file
        Args:
            location: path to target lyrics file
            prefer_synced: Use line synced lyrics if available
        """
        if self.sync_type == "line_synced" and prefer_synced:
            with open(f"{path}.lrc", "w+", encoding="utf-8") as f:
                f.writelines(self.lines_synced)
        else:
            with open(f"{path}.txt", "w+", encoding="utf-8") as f:
                f.writelines(self.lines[:-1])


class Playable:
    cover_images: list[Any]
    metadata: list[MetadataEntry]
    name: str
    input_stream: GeneralAudioStream

    def create_output(self, library: Path, output: str, replace: bool = False) -> Path:
        """
        Creates save directory for the output file
        Args:
            library: Path to root content library
            output: Template for the output filepath
            replace: Replace existing files with same output
        Returns:
            File path for the track
        """
        for m in self.metadata:
            if m.output is not None:
                output = output.replace("{" + m.name + "}", fix_filename(m.output))
        file_path = library.joinpath(output).expanduser()
        if file_path.exists() and not replace:
            raise FileExistsError("File already downloaded")
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return file_path

    def write_audio_stream(
        self,
        output: Path,
        chunk_size: int = 128 * 1024,
    ) -> LocalFile:
        """
        Writes audio stream to file
        Args:
            output: File path of saved audio stream
            chunk_size: maximum number of bytes to read at a time
        Returns:
            LocalFile object
        """
        file = f"{output}.ogg"
        with open(file, "wb") as f, Printer.progress(
            desc=self.name,
            total=self.input_stream.size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            position=0,
            leave=False,
        ) as p_bar:
            chunk = None
            while chunk != b"":
                chunk = self.input_stream.stream().read(chunk_size)
                p_bar.update(f.write(chunk))
        return LocalFile(Path(file), AudioFormat.VORBIS)

    def get_cover_art(self, size: ImageSize = ImageSize.LARGE) -> bytes:
        """
        Returns image data of cover art
        Args:
            size: Size of cover art
        Returns:
            Image data of cover art
        """
        return get(
            IMG_URL + bytes_to_hex(self.cover_images[size.value].file_id)
        ).content


class Track(PlayableContentFeeder.LoadedStream, Playable):
    lyrics: Lyrics

    def __init__(self, track: PlayableContentFeeder.LoadedStream, api):
        super(Track, self).__init__(
            track.track,
            track.input_stream,
            track.normalization_data,
            track.metrics,
        )
        self.__api = api
        self.cover_images = self.album.cover_group.image
        self.metadata = self.__default_metadata()

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return super().__getattribute__("track").__getattribute__(name)

    def __default_metadata(self) -> list[MetadataEntry]:
        date = self.album.date
        return [
            MetadataEntry("album", self.album.name),
            MetadataEntry("album_artist", [a.name for a in self.album.artist]),
            MetadataEntry("artist", self.artist[0].name),
            MetadataEntry("artists", [a.name for a in self.artist]),
            MetadataEntry("date", f"{date.year}-{date.month}-{date.day}"),
            MetadataEntry("disc", self.disc_number),
            MetadataEntry("duration", self.duration),
            MetadataEntry("explicit", self.explicit, "[E]" if self.explicit else ""),
            MetadataEntry("isrc", self.external_id[0].id),
            MetadataEntry("popularity", int(self.popularity * 255) / 100),
            MetadataEntry("track_number", self.number, str(self.number).zfill(2)),
            MetadataEntry("title", self.name),
            MetadataEntry(
                "replaygain_track_gain", self.normalization_data.track_gain_db, ""
            ),
            MetadataEntry(
                "replaygain_track_peak", self.normalization_data.track_peak, ""
            ),
            MetadataEntry(
                "replaygain_album_gain", self.normalization_data.album_gain_db, ""
            ),
            MetadataEntry(
                "replaygain_album_peak", self.normalization_data.album_peak, ""
            ),
        ]

    def get_lyrics(self) -> Lyrics:
        """Returns track lyrics if available"""
        if not self.track.has_lyrics:
            raise FileNotFoundError(
                f"No lyrics available for {self.track.artist[0].name} - {self.track.name}"
            )
        try:
            return self.lyrics
        except AttributeError:
            self.lyrics = Lyrics(
                self.__api.invoke_url(LYRICS_URL + bytes_to_base62(self.track.gid))[
                    "lyrics"
                ]
            )
            return self.lyrics


class Episode(PlayableContentFeeder.LoadedStream, Playable):
    def __init__(self, episode: PlayableContentFeeder.LoadedStream, api):
        super(Episode, self).__init__(
            episode.episode,
            episode.input_stream,
            episode.normalization_data,
            episode.metrics,
        )
        self.__api = api
        self.cover_images = self.episode.cover_image.image
        self.metadata = self.__default_metadata()

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return super().__getattribute__("episode").__getattribute__(name)

    def __default_metadata(self) -> list[MetadataEntry]:
        return [
            MetadataEntry("description", self.description),
            MetadataEntry("duration", self.duration),
            MetadataEntry("episode_number", self.number),
            MetadataEntry("explicit", self.explicit, "[E]" if self.explicit else ""),
            MetadataEntry("language", self.language),
            MetadataEntry("podcast", self.show.name),
            MetadataEntry("date", self.publish_time),
            MetadataEntry("title", self.name),
        ]

    def write_audio_stream(
        self, output: Path, chunk_size: int = 128 * 1024
    ) -> LocalFile:
        """
        Writes audio stream to file
        Args:
            output: File path of saved audio stream
            chunk_size: maximum number of bytes to read at a time
        Returns:
            LocalFile object
        """
        if not bool(self.external_url):
            return super().write_audio_stream(output, chunk_size)
        file = f"{output}.{self.external_url.rsplit('.', 1)[-1]}"
        with get(self.external_url, stream=True) as r, open(
            file, "wb"
        ) as f, Printer.progress(
            desc=self.name,
            total=self.input_stream.size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            position=0,
            leave=False,
        ) as p_bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                p_bar.update(f.write(chunk))
        return LocalFile(Path(file))

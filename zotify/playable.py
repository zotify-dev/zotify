from math import floor
from pathlib import Path
from typing import Any

from librespot.core import PlayableContentFeeder
from librespot.metadata import AlbumId
from librespot.structure import GeneralAudioStream
from librespot.util import bytes_to_hex
from requests import get
from tqdm import tqdm

from zotify.file import LocalFile
from zotify.utils import (
    AudioFormat,
    ImageSize,
    MetadataEntry,
    bytes_to_base62,
    fix_filename,
)

IMG_URL = "https://i.s" + "cdn.co/image/"
LYRICS_URL = "https://sp" + "client.wg.sp" + "otify.com/color-lyrics/v2/track/"


class Lyrics:
    def __init__(self, lyrics: dict, **kwargs):
        self.__lines = []
        self.__sync_type = lyrics["syncType"]
        for line in lyrics["lines"]:
            self.__lines.append(line["words"] + "\n")
        if self.__sync_type == "line_synced":
            self.__lines_synced = []
            for line in lyrics["lines"]:
                timestamp = int(line["start_time_ms"])
                ts_minutes = str(floor(timestamp / 60000)).zfill(2)
                ts_seconds = str(floor((timestamp % 60000) / 1000)).zfill(2)
                ts_millis = str(floor(timestamp % 1000))[:2].zfill(2)
                self.__lines_synced.append(
                    f"[{ts_minutes}:{ts_seconds}.{ts_millis}]{line.words}\n"
                )

    def save(self, path: Path | str, prefer_synced: bool = True) -> None:
        """
        Saves lyrics to file
        Args:
            location: path to target lyrics file
            prefer_synced: Use line synced lyrics if available
        """
        if not isinstance(path, Path):
            path = Path(path).expanduser()
        if self.__sync_type == "line_synced" and prefer_synced:
            with open(f"{path}.lrc", "w+", encoding="utf-8") as f:
                f.writelines(self.__lines_synced)
        else:
            with open(f"{path}.txt", "w+", encoding="utf-8") as f:
                f.writelines(self.__lines[:-1])


class Playable:
    cover_images: list[Any]
    input_stream: GeneralAudioStream
    metadata: list[MetadataEntry]
    name: str

    def create_output(
        self,
        library: Path | str = Path("./"),
        output: str = "{title}",
        replace: bool = False,
    ) -> Path:
        """
        Creates save directory for the output file
        Args:
            library: Path to root content library
            output: Template for the output filepath
            replace: Replace existing files with same output
        Returns:
            File path for the track
        """
        if not isinstance(library, Path):
            library = Path(library)
        for meta in self.metadata:
            if meta.string is not None:
                output = output.replace(
                    "{" + meta.name + "}", fix_filename(meta.string)
                )
        file_path = library.joinpath(output).expanduser()
        if file_path.exists() and not replace:
            raise FileExistsError("File already downloaded")
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return file_path

    def write_audio_stream(
        self, output: Path | str, p_bar: tqdm = tqdm(disable=True)
    ) -> LocalFile:
        """
        Writes audio stream to file
        Args:
            output: File path of saved audio stream
            p_bar: tqdm progress bar
        Returns:
            LocalFile object
        """
        if not isinstance(output, Path):
            output = Path(output).expanduser()
        file = f"{output}.ogg"
        with open(file, "wb") as f, p_bar as p_bar:
            chunk = None
            while chunk != b"":
                chunk = self.input_stream.stream().read(1024)
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
    __lyrics: Lyrics

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
        if not hasattr(self.album, "genre"):
            self.track.album = self.__api().get_metadata_4_album(
                AlbumId.from_hex(bytes_to_hex(self.album.gid))
            )
        return [
            MetadataEntry("album", self.album.name),
            MetadataEntry("album_artist", self.album.artist[0].name),
            MetadataEntry("album_artists", [a.name for a in self.album.artist]),
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
            MetadataEntry("year", date.year),
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
            return self.__lyrics
        except AttributeError:
            self.__lyrics = Lyrics(
                self.__api.invoke_url(LYRICS_URL + bytes_to_base62(self.track.gid))[
                    "lyrics"
                ]
            )
            return self.__lyrics


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
        self, output: Path | str, p_bar: tqdm = tqdm(disable=True)
    ) -> LocalFile:
        """
        Writes audio stream to file.
        Uses external source if available for faster download.
        Args:
            output: File path of saved audio stream
            p_bar: tqdm progress bar
        Returns:
            LocalFile object
        """
        if not isinstance(output, Path):
            output = Path(output).expanduser()
        if not bool(self.external_url):
            return super().write_audio_stream(output)
        file = f"{output}.{self.external_url.rsplit('.', 1)[-1]}"
        with get(self.external_url, stream=True) as r, open(
            file, "wb"
        ) as f, p_bar as p_bar:
            for chunk in r.iter_content(chunk_size=1024):
                p_bar.update(f.write(chunk))
        return LocalFile(Path(file))

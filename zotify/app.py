from argparse import Namespace
from enum import Enum
from pathlib import Path
from typing import Any, NamedTuple

from librespot.metadata import (
    AlbumId,
    ArtistId,
    EpisodeId,
    PlayableId,
    PlaylistId,
    ShowId,
    TrackId,
)
from librespot.util import bytes_to_hex

from zotify import Session
from zotify.config import Config
from zotify.file import TranscodingError
from zotify.loader import Loader
from zotify.printer import PrintChannel, Printer
from zotify.utils import API_URL, AudioFormat, b62_to_hex


class ParsingError(RuntimeError):
    ...


class PlayableType(Enum):
    TRACK = "track"
    EPISODE = "episode"


class PlayableData(NamedTuple):
    type: PlayableType
    id: PlayableId
    library: Path
    output: str


class Selection:
    def __init__(self, session: Session):
        self.__session = session

    def search(
        self,
        search_text: str,
        category: list = [
            "track",
            "album",
            "artist",
            "playlist",
            "show",
            "episode",
        ],
    ) -> list[str]:
        categories = ",".join(category)
        resp = self.__session.api().invoke_url(
            API_URL + "search",
            {
                "q": search_text,
                "type": categories,
                "include_external": "audio",
                "market": self.__session.country(),
            },
            limit=10,
            offset=0,
        )

        count = 0
        links = []
        for c in categories.split(","):
            label = c + "s"
            if len(resp[label]["items"]) > 0:
                print(f"\n### {label.capitalize()} ###")
                for item in resp[label]["items"]:
                    links.append(item)
                    self.__print(count + 1, item)
                    count += 1
        return self.__get_selection(links)

    def get(self, item: str, suffix: str) -> list[str]:
        resp = self.__session.api().invoke_url(f"{API_URL}me/{item}", limit=50)[suffix]
        for i in range(len(resp)):
            self.__print(i + 1, resp[i])
        return self.__get_selection(resp)

    @staticmethod
    def from_file(file_path: Path) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]

    @staticmethod
    def __get_selection(items: list[dict[str, Any]]) -> list[str]:
        print("\nResults to save (eg: 1,2,5 1-3)")
        selection = ""
        while len(selection) == 0:
            selection = input("==> ")
        ids = []
        selections = selection.split(",")
        for i in selections:
            if "-" in i:
                split = i.split("-")
                for x in range(int(split[0]), int(split[1]) + 1):
                    ids.append(items[x - 1]["uri"])
            else:
                ids.append(items[int(i) - 1]["uri"])
        return ids

    def __print(self, i: int, item: dict[str, Any]) -> None:
        match item["type"]:
            case "album":
                self.__print_album(i, item)
            case "playlist":
                self.__print_playlist(i, item)
            case "track":
                self.__print_track(i, item)
            case "show":
                self.__print_show(i, item)
            case _:
                print(
                    "{:<2} {:<77}".format(i, self.__fix_string_length(item["name"], 77))
                )

    def __print_album(self, i: int, item: dict[str, Any]) -> None:
        artists = ", ".join([artist["name"] for artist in item["artists"]])
        print(
            "{:<2} {:<38} {:<38}".format(
                i,
                self.__fix_string_length(item["name"], 38),
                self.__fix_string_length(artists, 38),
            )
        )

    def __print_playlist(self, i: int, item: dict[str, Any]) -> None:
        print(
            "{:<2} {:<38} {:<38}".format(
                i,
                self.__fix_string_length(item["name"], 38),
                self.__fix_string_length(item["owner"]["display_name"], 38),
            )
        )

    def __print_track(self, i: int, item: dict[str, Any]) -> None:
        artists = ", ".join([artist["name"] for artist in item["artists"]])
        print(
            "{:<2} {:<38} {:<38} {:<38}".format(
                i,
                self.__fix_string_length(item["name"], 38),
                self.__fix_string_length(artists, 38),
                self.__fix_string_length(item["album"]["name"], 38),
            )
        )

    def __print_show(self, i: int, item: dict[str, Any]) -> None:
        print(
            "{:<2} {:<38} {:<38}".format(
                i,
                self.__fix_string_length(item["name"], 38),
                self.__fix_string_length(item["publisher"], 38),
            )
        )

    @staticmethod
    def __fix_string_length(text: str, max_length: int) -> str:
        if len(text) > max_length:
            return text[: max_length - 3] + "..."
        return text


class App:
    __config: Config
    __session: Session
    __playable_list: list[PlayableData] = []

    def __init__(self, args: Namespace):
        self.__config = Config(args)
        Printer(self.__config)

        if self.__config.audio_format == AudioFormat.VORBIS and (
            self.__config.ffmpeg_args != "" or self.__config.ffmpeg_path != ""
        ):
            Printer.print(
                PrintChannel.WARNINGS,
                "FFmpeg options will be ignored since no transcoding is required",
            )

        with Loader("Logging in..."):
            if (
                args.username != "" and args.password != ""
            ) or not self.__config.credentials.is_file():
                self.__session = Session.from_userpass(
                    args.username,
                    args.password,
                    self.__config.credentials,
                    self.__config.language,
                )
            else:
                self.__session = Session.from_file(
                    self.__config.credentials, self.__config.language
                )

        ids = self.get_selection(args)
        with Loader("Parsing input..."):
            try:
                self.parse(ids)
            except ParsingError as e:
                Printer.print(PrintChannel.ERRORS, str(e))
        self.download_all()

    def get_selection(self, args: Namespace) -> list[str]:
        selection = Selection(self.__session)
        try:
            if args.search:
                return selection.search(" ".join(args.search), args.category)
            elif args.playlist:
                return selection.get("playlists", "items")
            elif args.followed:
                return selection.get("following?type=artist", "artists")
            elif args.liked_tracks:
                return selection.get("tracks", "items")
            elif args.liked_episodes:
                return selection.get("episodes", "items")
            elif args.download:
                ids = []
                for x in args.download:
                    ids.extend(selection.from_file(x))
                return ids
            elif args.urls:
                return args.urls
        except (FileNotFoundError, ValueError, KeyboardInterrupt):
            pass
        Printer.print(PrintChannel.WARNINGS, "there is nothing to do")
        exit()

    def parse(self, links: list[str]) -> None:
        """
        Parses list of selected tracks/playlists/shows/etc...
        Args:
            links: List of links
        """
        for link in links:
            link = link.rsplit("?", 1)[0]
            try:
                split = link.split(link[-23])
                _id = split[-1]
                id_type = split[-2]
            except IndexError:
                raise ParsingError(f'Could not parse "{link}"')

            match id_type:
                case "album":
                    self.__parse_album(b62_to_hex(_id))
                case "artist":
                    self.__parse_artist(b62_to_hex(_id))
                case "show":
                    self.__parse_show(b62_to_hex(_id))
                case "track":
                    self.__parse_track(b62_to_hex(_id))
                case "episode":
                    self.__parse_episode(b62_to_hex(_id))
                case "playlist":
                    self.__parse_playlist(_id)
                case _:
                    raise ParsingError(f'Unknown content type "{id_type}"')

    def __parse_album(self, hex_id: str) -> None:
        album = self.__session.api().get_metadata_4_album(AlbumId.from_hex(hex_id))
        for disc in album.disc:
            for track in disc.track:
                self.__playable_list.append(
                    PlayableData(
                        PlayableType.TRACK,
                        TrackId.from_hex(bytes_to_hex(track.gid)),
                        self.__config.music_library,
                        self.__config.output_album,
                    )
                )

    def __parse_artist(self, hex_id: str) -> None:
        artist = self.__session.api().get_metadata_4_artist(ArtistId.from_hex(hex_id))
        for album in artist.album_group + artist.single_group:
            album = self.__session.api().get_metadata_4_album(
                AlbumId.from_hex(album.gid)
            )
            for disc in album.disc:
                for track in disc.track:
                    self.__playable_list.append(
                        PlayableData(
                            PlayableType.TRACK,
                            TrackId.from_hex(bytes_to_hex(track.gid)),
                            self.__config.music_library,
                            self.__config.output_album,
                        )
                    )

    def __parse_playlist(self, b62_id: str) -> None:
        playlist = self.__session.api().get_playlist(PlaylistId(b62_id))
        for item in playlist.contents.items:
            split = item.uri.split(":")
            playable_type = PlayableType(split[1])
            id_map = {PlayableType.TRACK: TrackId, PlayableType.EPISODE: EpisodeId}
            playable_id = id_map[playable_type].from_base62(split[2])
            self.__playable_list.append(
                PlayableData(
                    playable_type,
                    playable_id,
                    self.__config.playlist_library,
                    self.__config.get(f"output_playlist_{playable_type.value}"),
                )
            )

    def __parse_show(self, hex_id: str) -> None:
        show = self.__session.api().get_metadata_4_show(ShowId.from_hex(hex_id))
        for episode in show.episode:
            self.__playable_list.append(
                PlayableData(
                    PlayableType.EPISODE,
                    EpisodeId.from_hex(bytes_to_hex(episode.gid)),
                    self.__config.podcast_library,
                    self.__config.output_podcast,
                )
            )

    def __parse_track(self, hex_id: str) -> None:
        self.__playable_list.append(
            PlayableData(
                PlayableType.TRACK,
                TrackId.from_hex(hex_id),
                self.__config.music_library,
                self.__config.output_album,
            )
        )

    def __parse_episode(self, hex_id: str) -> None:
        self.__playable_list.append(
            PlayableData(
                PlayableType.EPISODE,
                EpisodeId.from_hex(hex_id),
                self.__config.podcast_library,
                self.__config.output_podcast,
            )
        )

    def get_playable_list(self) -> list[PlayableData]:
        """Returns list of Playable items"""
        return self.__playable_list

    def download_all(self) -> None:
        """Downloads playable to local file"""
        for playable in self.__playable_list:
            self.__download(playable)

    def __download(self, playable: PlayableData) -> None:
        if playable.type == PlayableType.TRACK:
            with Loader("Fetching track..."):
                track = self.__session.get_track(
                    playable.id, self.__config.download_quality
                )
        elif playable.type == PlayableType.EPISODE:
            with Loader("Fetching episode..."):
                track = self.__session.get_episode(playable.id)
        else:
            Printer.print(
                PrintChannel.SKIPS,
                f'Download Error: Unknown playable content "{playable.type}"',
            )
            return

        output = track.create_output(playable.library, playable.output)
        file = track.write_audio_stream(
            output,
            self.__config.chunk_size,
        )

        if self.__config.save_lyrics and playable.type == PlayableType.TRACK:
            with Loader("Fetching lyrics..."):
                try:
                    track.get_lyrics().save(output)
                except FileNotFoundError as e:
                    Printer.print(PrintChannel.SKIPS, str(e))

        Printer.print(PrintChannel.DOWNLOADS, f"\nDownloaded {track.name}")

        if self.__config.audio_format != AudioFormat.VORBIS:
            try:
                with Loader(PrintChannel.PROGRESS, "Converting audio..."):
                    file.transcode(
                        self.__config.audio_format,
                        self.__config.transcode_bitrate,
                        True,
                        self.__config.ffmpeg_path,
                        self.__config.ffmpeg_args.split(),
                    )
            except TranscodingError as e:
                Printer.print(PrintChannel.ERRORS, str(e))

        if self.__config.save_metadata:
            with Loader("Writing metadata..."):
                file.write_metadata(track.metadata)
                file.write_cover_art(track.get_cover_art(self.__config.artwork_size))

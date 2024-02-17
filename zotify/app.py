from argparse import Namespace
from pathlib import Path
from typing import Any

from zotify import Session
from zotify.collections import Album, Artist, Collection, Episode, Playlist, Show, Track
from zotify.config import Config
from zotify.file import TranscodingError
from zotify.loader import Loader
from zotify.logger import LogChannel, Logger
from zotify.utils import (
    AudioFormat,
    CollectionType,
    PlayableType,
)


class ParseError(ValueError): ...


class Selection:
    def __init__(self, session: Session):
        self.__session = session
        self.__items: list[dict[str, Any]] = []
        self.__print_labels = {
            "album": ("name", "artists"),
            "playlist": ("name", "owner"),
            "track": ("title", "artists", "album"),
            "show": ("title", "creator"),
        }

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
        with Loader("Searching..."):
            country = self.__session.api().invoke_url("me")["country"]
            resp = self.__session.api().invoke_url(
                "search",
                {
                    "q": search_text,
                    "type": categories,
                    "include_external": "audio",
                    "market": country,
                },
                limit=10,
                offset=0,
            )

        count = 0
        for cat in categories.split(","):
            label = cat + "s"
            items = resp[label]["items"]
            if len(items) > 0:
                print(f"\n### {label.capitalize()} ###")
                try:
                    self.__print(count, items, *self.__print_labels[cat])
                except KeyError:
                    self.__print(count, items, "name")
                count += len(items)
                self.__items.extend(items)
        return self.__get_selection()

    def get(self, category: str, name: str = "", content: str = "") -> list[str]:
        with Loader("Fetching items..."):
            r = self.__session.api().invoke_url(f"me/{category}", limit=50)
            if content != "":
                r = r[content]
            resp = r["items"]

        for i in range(len(resp)):
            try:
                item = resp[i][name]
            except KeyError:
                item = resp[i]
            self.__items.append(item)
            self.__print(i + 1, item)
        return self.__get_selection()

    @staticmethod
    def from_file(file_path: Path) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]

    def __get_selection(self) -> list[str]:
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
                    ids.append(self.__items[x - 1]["uri"])
            else:
                ids.append(self.__items[int(i) - 1]["uri"])
        return ids

    def __print(self, count: int, items: list[dict[str, Any]], *args: str) -> None:
        arg_range = range(len(args))
        category_str = "   " + " ".join("{:<38}" for _ in arg_range)
        print(category_str.format(*[s.upper() for s in list(args)]))
        for item in items:
            count += 1
            fmt_str = "{:<2} ".format(count) + " ".join("{:<38}" for _ in arg_range)
            fmt_vals: list[str] = []
            for arg in args:
                match arg:
                    case "artists":
                        fmt_vals.append(
                            ", ".join([artist["name"] for artist in item["artists"]])
                        )
                    case "owner":
                        fmt_vals.append(item["owner"]["display_name"])
                    case "album":
                        fmt_vals.append(item["album"]["name"])
                    case "creator":
                        fmt_vals.append(item["publisher"])
                    case "title":
                        fmt_vals.append(item["name"])
                    case _:
                        fmt_vals.append(item[arg])
            print(
                fmt_str.format(
                    *(self.__fix_string_length(fmt_vals[x], 38) for x in arg_range),
                )
            )

    @staticmethod
    def __fix_string_length(text: str, max_length: int) -> str:
        if len(text) > max_length:
            return text[: max_length - 3] + "..."
        return text


class App:
    def __init__(self, args: Namespace):
        self.__config = Config(args)
        Logger(self.__config)

        # Check options
        if self.__config.audio_format == AudioFormat.VORBIS and (
            self.__config.ffmpeg_args != "" or self.__config.ffmpeg_path != ""
        ):
            Logger.log(
                LogChannel.WARNINGS,
                "FFmpeg options will be ignored since no transcoding is required",
            )

        # Create session
        if args.username != "" and args.password != "":
            self.__session = Session.from_userpass(
                args.username,
                args.password,
                self.__config.credentials,
                self.__config.language,
            )
        elif self.__config.credentials.is_file():
            self.__session = Session.from_file(
                self.__config.credentials, self.__config.language
            )
        else:
            self.__session = Session.from_prompt(
                self.__config.credentials, self.__config.language
            )

        # Get items to download
        ids = self.get_selection(args)
        with Loader("Parsing input..."):
            try:
                collections = self.parse(ids)
            except ParseError as e:
                Logger.log(LogChannel.ERRORS, str(e))
        if len(collections) > 0:
            self.download_all(collections)
        else:
            Logger.log(LogChannel.WARNINGS, "there is nothing to do")
        exit(0)

    def get_selection(self, args: Namespace) -> list[str]:
        selection = Selection(self.__session)
        try:
            if args.search:
                return selection.search(" ".join(args.search), args.category)
            elif args.playlist:
                return selection.get("playlists")
            elif args.followed:
                return selection.get("following?type=artist", content="artists")
            elif args.liked_tracks:
                return selection.get("tracks", "track")
            elif args.liked_episodes:
                return selection.get("episodes")
            elif args.download:
                ids = []
                for x in args.download:
                    ids.extend(selection.from_file(x))
                return ids
            elif args.urls:
                return args.urls
        except (FileNotFoundError, ValueError):
            Logger.log(LogChannel.WARNINGS, "there is nothing to do")
        except KeyboardInterrupt:
            Logger.log(LogChannel.WARNINGS, "\nthere is nothing to do")
            exit(130)
        exit(0)

    def parse(self, links: list[str]) -> list[Collection]:
        collections: list[Collection] = []
        for link in links:
            link = link.rsplit("?", 1)[0]
            try:
                split = link.split(link[-23])
                _id = split[-1]
                id_type = split[-2]
            except IndexError:
                raise ParseError(f'Could not parse "{link}"')

            match id_type:
                case "album":
                    collections.append(Album(self.__session, _id))
                case "artist":
                    collections.append(Artist(self.__session, _id))
                case "show":
                    collections.append(Show(self.__session, _id))
                case "track":
                    collections.append(Track(self.__session, _id))
                case "episode":
                    collections.append(Episode(self.__session, _id))
                case "playlist":
                    collections.append(Playlist(self.__session, _id))
                case _:
                    raise ParseError(f'Unsupported content type "{id_type}"')
        return collections

    def download_all(self, collections: list[Collection]) -> None:
        """Downloads playable to local file"""
        for collection in collections:
            for i in range(len(collection.playables)):
                playable = collection.playables[i]

                # Get track data
                if playable.type == PlayableType.TRACK:
                    with Loader("Fetching track..."):
                        track = self.__session.get_track(
                            playable.id, self.__config.download_quality
                        )
                elif playable.type == PlayableType.EPISODE:
                    with Loader("Fetching episode..."):
                        track = self.__session.get_episode(playable.id)
                else:
                    Logger.log(
                        LogChannel.SKIPS,
                        f'Download Error: Unknown playable content "{playable.type}"',
                    )
                    return

                # Create download location and generate file name
                match collection.type():
                    case CollectionType.PLAYLIST:
                        # TODO: add playlist name to track metadata
                        library = self.__config.playlist_library
                        template = (
                            self.__config.output_playlist_track
                            if playable.type == PlayableType.TRACK
                            else self.__config.output_playlist_episode
                        )
                    case CollectionType.SHOW | CollectionType.EPISODE:
                        library = self.__config.podcast_library
                        template = self.__config.output_podcast
                    case _:
                        library = self.__config.music_library
                        template = self.__config.output_album
                output = track.create_output(
                    library, template, self.__config.replace_existing
                )

                file = track.write_audio_stream(output)

                # Download lyrics
                if playable.type == PlayableType.TRACK and self.__config.lyrics_file:
                    with Loader("Fetching lyrics..."):
                        try:
                            track.get_lyrics().save(output)
                        except FileNotFoundError as e:
                            Logger.log(LogChannel.SKIPS, str(e))
                Logger.log(LogChannel.DOWNLOADS, f"\nDownloaded {track.name}")

                # Transcode audio
                if self.__config.audio_format != AudioFormat.VORBIS:
                    try:
                        with Loader(LogChannel.PROGRESS, "Converting audio..."):
                            file.transcode(
                                self.__config.audio_format,
                                self.__config.transcode_bitrate,
                                True,
                                self.__config.ffmpeg_path,
                                self.__config.ffmpeg_args.split(),
                            )
                    except TranscodingError as e:
                        Logger.log(LogChannel.ERRORS, str(e))

                # Write metadata
                if self.__config.save_metadata:
                    with Loader("Writing metadata..."):
                        file.write_metadata(track.metadata)
                        file.write_cover_art(
                            track.get_cover_art(self.__config.artwork_size)
                        )

#! /usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path

from zotify.app import client
from zotify.config import CONFIG_PATHS, CONFIG_VALUES
from zotify.utils import OptionalOrFalse

VERSION = "0.9.0"


def main():
    parser = ArgumentParser(
        prog="zotify",
        description="A fast and customizable music and podcast downloader",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print version and exit",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATHS["conf"],
        help="Specify the config.json location",
    )
    parser.add_argument(
        "-l",
        "--library",
        type=Path,
        help="Specify a path to the root of a music/podcast library",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Specify the output location/format"
    )
    parser.add_argument(
        "-c",
        "--category",
        type=str,
        choices=["album", "artist", "playlist", "track", "show", "episode"],
        default=["album", "artist", "playlist", "track", "show", "episode"],
        nargs="+",
        help="Searches for only this type",
    )
    parser.add_argument("--username", type=str, help="Account username")
    parser.add_argument("--password", type=str, help="Account password")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "urls",
        type=str,
        default="",
        nargs="*",
        help="Downloads the track, album, playlist, podcast, episode or artist from a URL or URI. Accepts multiple options.",
    )
    group.add_argument(
        "-d",
        "--download",
        type=str,
        help="Downloads tracks, playlists and albums from the URLs written in the file passed.",
    )
    group.add_argument(
        "-f",
        "--followed",
        action="store_true",
        help="Download all songs from your followed artists.",
    )
    group.add_argument(
        "-lt",
        "--liked-tracks",
        action="store_true",
        help="Download all of your liked songs.",
    )
    group.add_argument(
        "-le",
        "--liked-episodes",
        action="store_true",
        help="Download all of your liked episodes.",
    )
    group.add_argument(
        "-p",
        "--playlist",
        action="store_true",
        help="Download a saved playlists from your account.",
    )
    group.add_argument(
        "-s",
        "--search",
        type=str,
        nargs="+",
        help="Search for a specific track, album, playlist, artist or podcast",
    )

    for k, v in CONFIG_VALUES.items():
        if v["type"] == bool:
            parser.add_argument(
                v["arg"],
                action=OptionalOrFalse,
                default=v["default"],
                help=v["help"],
            )
        else:
            try:
                parser.add_argument(
                    v["arg"],
                    type=v["type"],
                    choices=v["choices"],
                    default=None,
                    help=v["help"],
                )
            except KeyError:
                parser.add_argument(
                    v["arg"],
                    type=v["type"],
                    default=None,
                    help=v["help"],
                )

    parser.set_defaults(func=client)
    args = parser.parse_args()
    if args.version:
        print(VERSION)
        return
    args.func(args)
    return
    try:
        args.func(args)
    except Exception as e:
        print(f"Fatal Error: {e}")


if __name__ == "__main__":
    main()

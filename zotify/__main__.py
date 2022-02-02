#! /usr/bin/env python3

"""
Zotify
It's like youtube-dl, but for that other music platform.
"""

import argparse

from zotify.app import client
from zotify.config import CONFIG_VALUES

def main():
    parser = argparse.ArgumentParser(prog='zotify',
        description='A music and podcast downloader needing only a python interpreter and ffmpeg.')
    parser.add_argument('-ns', '--no-splash',
                        action='store_true',
                        help='Suppress the splash screen when loading.')
    parser.add_argument('--config-location',
                        type=str,
                        help='Specify the zconfig.json location')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('urls',
                       type=str,
                       # action='extend',
                       default='',
                       nargs='*',
                       help='Downloads the track, album, playlist, podcast episode, or all albums by an artist from a url. Can take multiple urls.')
    group.add_argument('-ls', '--liked-songs',
                       dest='liked_songs',
                       action='store_true',
                       help='Downloads all the liked songs from your account.')
    group.add_argument('-p', '--playlist',
                       action='store_true',
                       help='Downloads a saved playlist from your account.')
    group.add_argument('-s', '--search',
                       dest='search_spotify',
                       action='store_true',
                       help='Loads search prompt to find then download a specific track, album or playlist')
    group.add_argument('-d', '--download',
                       type=str,
                       help='Downloads tracks, playlists and albums from the URLs written in the file passed.')

    for configkey in CONFIG_VALUES:
        parser.add_argument(CONFIG_VALUES[configkey]['arg'],
                            type=str,
                            default=None,
                            help='Specify the value of the ['+configkey+'] config value')

    parser.set_defaults(func=client)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

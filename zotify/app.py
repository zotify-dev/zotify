from librespot.audio.decoders import AudioQuality
from tabulate import tabulate
import os

from album import download_album, download_artist_albums
from const import TRACK, NAME, ID, ARTIST, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUM, ALBUMS, \
    OWNER, PLAYLIST, PLAYLISTS, DISPLAY_NAME
from playlist import get_playlist_songs, get_playlist_info, download_from_user_playlist, download_playlist
from podcast import download_episode, get_show_episodes
from termoutput import Printer, PrintChannel
from track import download_track, get_saved_tracks
from utils import splash, split_input, regex_input_for_urls
from zspotify import ZSpotify

SEARCH_URL = 'https://api.spotify.com/v1/search'


def client(args) -> None:
    """ Connects to spotify to perform query's and get songs to download """
    ZSpotify(args)

    Printer.print(PrintChannel.SPLASH, splash())

    if ZSpotify.check_premium():
        Printer.print(PrintChannel.SPLASH, '[ DETECTED PREMIUM ACCOUNT - USING VERY_HIGH QUALITY ]\n\n')
        ZSpotify.DOWNLOAD_QUALITY = AudioQuality.VERY_HIGH
    else:
        Printer.print(PrintChannel.SPLASH, '[ DETECTED FREE ACCOUNT - USING HIGH QUALITY ]\n\n')
        ZSpotify.DOWNLOAD_QUALITY = AudioQuality.HIGH

    if args.download:
        urls = []
        filename = args.download
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                urls.extend([line.strip() for line in file.readlines()])

            download_from_urls(urls)

        else:
            Printer.print(PrintChannel.ERRORS, f'File {filename} not found.\n')

    if args.urls:
        download_from_urls(args.urls)

    if args.playlist:
        download_from_user_playlist()

    if args.liked_songs:
        for song in get_saved_tracks():
            if not song[TRACK][NAME] or not song[TRACK][ID]:
                Printer.print(PrintChannel.SKIPS, '###   SKIPPING:  SONG DOES NOT EXIST ON SPOTIFY ANYMORE   ###' + "\n")
            else:
                download_track('liked', song[TRACK][ID])

    if args.search_spotify:
        search_text = ''
        while len(search_text) == 0:
            search_text = input('Enter search or URL: ')

        if not download_from_urls([search_text]):
            search(search_text)

def download_from_urls(urls: list[str]) -> bool:
    """ Downloads from a list of spotify urls """
    download = False

    for spotify_url in urls:
        track_id, album_id, playlist_id, episode_id, show_id, artist_id = regex_input_for_urls(
            spotify_url)

        if track_id is not None:
            download = True
            download_track('single', track_id)
        elif artist_id is not None:
            download = True
            download_artist_albums(artist_id)
        elif album_id is not None:
            download = True
            download_album(album_id)
        elif playlist_id is not None:
            download = True
            playlist_songs = get_playlist_songs(playlist_id)
            name, _ = get_playlist_info(playlist_id)
            enum = 1
            char_num = len(str(len(playlist_songs)))
            for song in playlist_songs:
                if not song[TRACK][NAME] or not song[TRACK][ID]:
                    Printer.print(PrintChannel.SKIPS, '###   SKIPPING:  SONG DOES NOT EXIST ON SPOTIFY ANYMORE   ###' + "\n")
                else:
                    download_track('playlist', song[TRACK][ID], extra_keys=
                    {
                        'playlist_song_name': song[TRACK][NAME],
                        'playlist': name,
                        'playlist_num': str(enum).zfill(char_num),
                        'playlist_id': playlist_id,
                        'playlist_track_id': song[TRACK][ID]
                    })
                    enum += 1
        elif episode_id is not None:
            download = True
            download_episode(episode_id)
        elif show_id is not None:
            download = True
            for episode in get_show_episodes(show_id):
                download_episode(episode)

    return download


def search(search_term):
    """ Searches Spotify's API for relevant data """
    params = {'limit': '10',
              'offset': '0',
              'q': search_term,
              'type': 'track,album,artist,playlist'}

    # Parse args
    splits = search_term.split()
    for split in splits:
        index = splits.index(split)

        if split[0] == '-' and len(split) > 1:
            if len(splits)-1 == index:
                raise IndexError('No parameters passed after option: {}\n'.
                                 format(split))

        if split == '-l' or split == '-limit':
            try:
                int(splits[index+1])
            except ValueError:
                raise ValueError('Paramater passed after {} option must be an integer.\n'.
                                 format(split))
            if int(splits[index+1]) > 50:
                raise ValueError('Invalid limit passed. Max is 50.\n')
            params['limit'] = splits[index+1]

        if split == '-t' or split == '-type':

            allowed_types = ['track', 'playlist', 'album', 'artist']
            passed_types = []
            for i in range(index+1, len(splits)):
                if splits[i][0] == '-':
                    break

                if splits[i] not in allowed_types:
                    raise ValueError('Parameters passed after {} option must be from this list:\n{}'.
                                     format(split, '\n'.join(allowed_types)))

                passed_types.append(splits[i])
            params['type'] = ','.join(passed_types)

    if len(params['type']) == 0:
        params['type'] = 'track,album,artist,playlist'

    # Clean search term
    search_term_list = []
    for split in splits:
        if split[0] == "-":
            break
        search_term_list.append(split)
    if not search_term_list:
        raise ValueError("Invalid query.")
    params["q"] = ' '.join(search_term_list)

    resp = ZSpotify.invoke_url_with_params(SEARCH_URL, **params)

    counter = 1
    dics = []

    total_tracks = 0
    if TRACK in params['type'].split(','):
        tracks = resp[TRACKS][ITEMS]
        if len(tracks) > 0:
            print('###  TRACKS  ###')
            track_data = []
            for track in tracks:
                if track[EXPLICIT]:
                    explicit = '[E]'
                else:
                    explicit = ''

                track_data.append([counter, f'{track[NAME]} {explicit}',
                                  ','.join([artist[NAME] for artist in track[ARTISTS]])])
                dics.append({
                    ID: track[ID],
                    NAME: track[NAME],
                    'type': TRACK,
                })

                counter += 1
            total_tracks = counter - 1
            print(tabulate(track_data, headers=[
                  'S.NO', 'Name', 'Artists'], tablefmt='pretty'))
            print('\n')
            del tracks
            del track_data

    total_albums = 0
    if ALBUM in params['type'].split(','):
        albums = resp[ALBUMS][ITEMS]
        if len(albums) > 0:
            print('###  ALBUMS  ###')
            album_data = []
            for album in albums:
                album_data.append([counter, album[NAME],
                                  ','.join([artist[NAME] for artist in album[ARTISTS]])])
                dics.append({
                    ID: album[ID],
                    NAME: album[NAME],
                    'type': ALBUM,
                })

                counter += 1
            total_albums = counter - total_tracks - 1
            print(tabulate(album_data, headers=[
                  'S.NO', 'Album', 'Artists'], tablefmt='pretty'))
            print('\n')
            del albums
            del album_data

    total_artists = 0
    if ARTIST in params['type'].split(','):
        artists = resp[ARTISTS][ITEMS]
        if len(artists) > 0:
            print('###  ARTISTS  ###')
            artist_data = []
            for artist in artists:
                artist_data.append([counter, artist[NAME]])
                dics.append({
                    ID: artist[ID],
                    NAME: artist[NAME],
                    'type': ARTIST,
                })
                counter += 1
            total_artists = counter - total_tracks - total_albums - 1
            print(tabulate(artist_data, headers=[
                  'S.NO', 'Name'], tablefmt='pretty'))
            print('\n')
            del artists
            del artist_data

    total_playlists = 0
    if PLAYLIST in params['type'].split(','):
        playlists = resp[PLAYLISTS][ITEMS]
        if len(playlists) > 0:
            print('###  PLAYLISTS  ###')
            playlist_data = []
            for playlist in playlists:
                playlist_data.append(
                    [counter, playlist[NAME], playlist[OWNER][DISPLAY_NAME]])
                dics.append({
                    ID: playlist[ID],
                    NAME: playlist[NAME],
                    'type': PLAYLIST,
                })
                counter += 1
            total_playlists = counter - total_artists - total_tracks - total_albums - 1
            print(tabulate(playlist_data, headers=[
                  'S.NO', 'Name', 'Owner'], tablefmt='pretty'))
            print('\n')
            del playlists
            del playlist_data

    if total_tracks + total_albums + total_artists + total_playlists == 0:
        print('NO RESULTS FOUND - EXITING...')
    else:
        selection = ''
        print('> SELECT A DOWNLOAD OPTION BY ID')
        print('> SELECT A RANGE BY ADDING A DASH BETWEEN BOTH ID\'s')
        print('> OR PARTICULAR OPTIONS BY ADDING A COMMA BETWEEN ID\'s\n')
        while len(selection) == 0:
            selection = str(input('ID(s): '))
        inputs = split_input(selection)
        for pos in inputs:
            position = int(pos)
            for dic in dics:
                print_pos = dics.index(dic) + 1
                if print_pos == position:
                    if dic['type'] == TRACK:
                        download_track('single', dic[ID])
                    elif dic['type'] == ALBUM:
                        download_album(dic[ID])
                    elif dic['type'] == ARTIST:
                        download_artist_albums(dic[ID])
                    else:
                        download_playlist(dic)

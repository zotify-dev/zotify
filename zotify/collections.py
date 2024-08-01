from librespot.metadata import (
    AlbumId,
    ArtistId,
    PlaylistId,
    ShowId,
)

from zotify import Api
from zotify.config import Config
from zotify.utils import MetadataEntry, PlayableData, PlayableType, bytes_to_base62


class Collection:
    playables: list[PlayableData] = []

    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        raise NotImplementedError


class Album(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        album = api.get_metadata_4_album(AlbumId.from_base62(b62_id))
        for disc in album.disc:
            for track in disc.track:
                self.playables.append(
                    PlayableData(
                        PlayableType.TRACK,
                        bytes_to_base62(track.gid),
                        config.album_library,
                        config.output_album,
                    )
                )


class Artist(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        artist = api.get_metadata_4_artist(ArtistId.from_base62(b62_id))
        for album_group in (
            artist.album_group
            and artist.single_group
            and artist.compilation_group
            and artist.appears_on_group
        ):
            album = api.get_metadata_4_album(AlbumId.from_hex(album_group.album[0].gid))
            for disc in album.disc:
                for track in disc.track:
                    self.playables.append(
                        PlayableData(
                            PlayableType.TRACK,
                            bytes_to_base62(track.gid),
                            config.album_library,
                            config.output_album,
                        )
                    )


class Show(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        show = api.get_metadata_4_show(ShowId.from_base62(b62_id))
        for episode in show.episode:
            self.playables.append(
                PlayableData(
                    PlayableType.EPISODE,
                    bytes_to_base62(episode.gid),
                    config.podcast_library,
                    config.output_podcast,
                )
            )


class Playlist(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        playlist = api.get_playlist(PlaylistId(b62_id))
        for i in range(len(playlist.contents.items)):
            item = playlist.contents.items[i]
            split = item.uri.split(":")
            playable_type = split[1]
            playable_id = split[2]
            metadata = [
                MetadataEntry("playlist", playlist.attributes.name),
                MetadataEntry("playlist_length", playlist.length),
                MetadataEntry("playlist_owner", playlist.owner_username),
                MetadataEntry(
                    "playlist_number",
                    i + 1,
                    str(i + 1).zfill(len(str(playlist.length + 1))),
                ),
            ]
            if playable_type == "track":
                self.playables.append(
                    PlayableData(
                        PlayableType.TRACK,
                        playable_id,
                        config.playlist_library,
                        config.output_playlist_track,
                        metadata,
                    )
                )
            elif playable_type == "episode":
                self.playables.append(
                    PlayableData(
                        PlayableType.EPISODE,
                        playable_id,
                        config.playlist_library,
                        config.output_playlist_episode,
                        metadata,
                    )
                )
            else:
                raise ValueError("Unknown playable content", playable_type)


class Track(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        self.playables.append(
            PlayableData(
                PlayableType.TRACK, b62_id, config.album_library, config.output_album
            )
        )


class Episode(Collection):
    def __init__(self, b62_id: str, api: Api, config: Config = Config()):
        self.playables.append(
            PlayableData(
                PlayableType.EPISODE,
                b62_id,
                config.podcast_library,
                config.output_podcast,
            )
        )

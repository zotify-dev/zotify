from librespot.metadata import (
    AlbumId,
    ArtistId,
    PlaylistId,
    ShowId,
)

from zotify import Session
from zotify.utils import CollectionType, PlayableData, PlayableType, bytes_to_base62


class Collection:
    playables: list[PlayableData] = []

    def type(self) -> CollectionType:
        return CollectionType(self.__class__.__name__.lower())


class Album(Collection):
    def __init__(self, session: Session, b62_id: str):
        album = session.api().get_metadata_4_album(AlbumId.from_base62(b62_id))
        for disc in album.disc:
            for track in disc.track:
                self.playables.append(
                    PlayableData(
                        PlayableType.TRACK,
                        bytes_to_base62(track.gid),
                    )
                )


class Artist(Collection):
    def __init__(self, session: Session, b62_id: str):
        artist = session.api().get_metadata_4_artist(ArtistId.from_base62(b62_id))
        for album_group in (
            artist.album_group
            and artist.single_group
            and artist.compilation_group
            and artist.appears_on_group
        ):
            album = session.api().get_metadata_4_album(
                AlbumId.from_hex(album_group.album[0].gid)
            )
            for disc in album.disc:
                for track in disc.track:
                    self.playables.append(
                        PlayableData(
                            PlayableType.TRACK,
                            bytes_to_base62(track.gid),
                        )
                    )


class Show(Collection):
    def __init__(self, session: Session, b62_id: str):
        show = session.api().get_metadata_4_show(ShowId.from_base62(b62_id))
        for episode in show.episode:
            self.playables.append(
                PlayableData(PlayableType.EPISODE, bytes_to_base62(episode.gid))
            )


class Playlist(Collection):
    def __init__(self, session: Session, b62_id: str):
        playlist = session.api().get_playlist(PlaylistId(b62_id))
        # self.name = playlist.title
        for item in playlist.contents.items:
            split = item.uri.split(":")
            playable_type = split[1]
            if playable_type == "track":
                self.playables.append(
                    PlayableData(
                        PlayableType.TRACK,
                        split[2],
                    )
                )
            elif playable_type == "episode":
                self.playables.append(
                    PlayableData(
                        PlayableType.EPISODE,
                        split[2],
                    )
                )
            else:
                raise ValueError("Unknown playable content", playable_type)


class Track(Collection):
    def __init__(self, session: Session, b62_id: str):
        self.playables.append(PlayableData(PlayableType.TRACK, b62_id))


class Episode(Collection):
    def __init__(self, session: Session, b62_id: str):
        self.playables.append(PlayableData(PlayableType.EPISODE, b62_id))

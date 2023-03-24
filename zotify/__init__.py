from pathlib import Path

from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.core import (
    ApiClient,
    PlayableContentFeeder,
    Session as LibrespotSession,
)
from librespot.metadata import EpisodeId, PlayableId, TrackId
from pwinput import pwinput
from requests import HTTPError, get

from zotify.playable import Episode, Track
from zotify.utils import (
    API_URL,
    Quality,
)


class Api(ApiClient):
    def __init__(self, session: LibrespotSession, language: str = "en"):
        super(Api, self).__init__(session)
        self.__session = session
        self.__language = language

    def __get_token(self) -> str:
        """Returns user's API token"""
        return (
            self.__session.tokens()
            .get_token(
                "playlist-read-private",  # Private playlists
                "user-follow-read",  # Followed artists
                "user-library-read",  # Liked tracks/episodes/etc.
                "user-read-private",  # Country
            )
            .access_token
        )

    def invoke_url(
        self,
        url: str,
        params: dict = {},
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """
        Requests data from api
        Args:
            url: API url and to get data from
            params: parameters to be sent in the request
            limit: The maximum number of items in the response
            offset: The offset of the items returned
        Returns:
            Dictionary representation of json response
        """
        headers = {
            "Authorization": f"Bearer {self.__get_token()}",
            "Accept": "application/json",
            "Accept-Language": self.__language,
            "app-platform": "WebPlayer",
        }
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        response = get(url, headers=headers, params=params)
        data = response.json()

        try:
            raise HTTPError(
                f"{url}\nAPI Error {data['error']['status']}: {data['error']['message']}"
            )
        except KeyError:
            return data


class Session:
    __api: Api
    __country: str
    __is_premium: bool
    __session: LibrespotSession

    def __init__(
        self,
        cred_file: Path | None = None,
        username: str | None = None,
        password: str | None = None,
        save: bool | None = False,
        language: str = "en",
    ) -> None:
        """
        Authenticates user, saves credentials to a file
        and generates api token
        Args:
            cred_file: Path to the credentials file
            username: Account username
            password: Account password
            save: Save given credentials to a file
        """
        # Find an existing credentials file
        if cred_file is not None and cred_file.is_file():
            conf = (
                LibrespotSession.Configuration.Builder()
                .set_store_credentials(False)
                .build()
            )
            self.__session = (
                LibrespotSession.Builder(conf).stored_file(str(cred_file)).create()
            )
        # Otherwise get new credentials
        else:
            username = input("Username: ") if username is None else username
            password = (
                pwinput(prompt="Password: ", mask="*") if password is None else password
            )

            # Save credentials to file
            if save and cred_file:
                cred_file.parent.mkdir(parents=True, exist_ok=True)
                conf = (
                    LibrespotSession.Configuration.Builder()
                    .set_stored_credential_file(str(cred_file))
                    .build()
                )
            else:
                conf = (
                    LibrespotSession.Configuration.Builder()
                    .set_store_credentials(False)
                    .build()
                )
            self.__session = (
                LibrespotSession.Builder(conf).user_pass(username, password).create()
            )
        self.__api = Api(self.__session, language)

    def __get_playable(
        self, playable_id: PlayableId, quality: Quality
    ) -> PlayableContentFeeder.LoadedStream:
        if quality.value is None:
            quality = Quality.VERY_HIGH if self.is_premium() else Quality.HIGH
        return self.__session.content_feeder().load(
            playable_id,
            VorbisOnlyAudioQuality(quality.value),
            False,
            None,
        )

    def get_track(self, track_id: TrackId, quality: Quality = Quality.AUTO) -> Track:
        """
        Gets track/episode data and audio stream
        Args:
            track_id: Base62 ID of track
            quality: Audio quality of track when downloaded
        Returns:
            Track object
        """
        return Track(self.__get_playable(track_id, quality), self.api())

    def get_episode(self, episode_id: EpisodeId) -> Episode:
        """
        Gets track/episode data and audio stream
        Args:
            episode: Base62 ID of episode
        Returns:
            Episode object
        """
        return Episode(self.__get_playable(episode_id, Quality.NORMAL), self.api())

    def api(self) -> ApiClient:
        """Returns API Client"""
        return self.__api

    def country(self) -> str:
        """Returns two letter country code of user's account"""
        try:
            return self.__country
        except AttributeError:
            self.__country = self.api().invoke_url(API_URL + "me")["country"]
            return self.__country

    def is_premium(self) -> bool:
        """Returns users premium account status"""
        return self.__session.get_user_attribute("type") == "premium"

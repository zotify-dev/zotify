from __future__ import annotations

from pathlib import Path

from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.core import ApiClient, ApResolver, PlayableContentFeeder
from librespot.core import Session as LibrespotSession
from librespot.metadata import EpisodeId, PlayableId, TrackId
from pwinput import pwinput
from requests import HTTPError, get

from zotify.loader import Loader
from zotify.playable import Episode, Track
from zotify.utils import Quality

API_URL = "https://api.sp" + "otify.com/v1/"


class Api(ApiClient):
    def __init__(self, session: Session):
        super(Api, self).__init__(session)
        self.__session = session

    def __get_token(self) -> str:
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
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Requests data from API
        Args:
            url: API URL and to get data from
            params: parameters to be sent in the request
            limit: The maximum number of items in the response
            offset: The offset of the items returned
        Returns:
            Dictionary representation of JSON response
        """
        headers = {
            "Authorization": f"Bearer {self.__get_token()}",
            "Accept": "application/json",
            "Accept-Language": self.__session.language(),
            "app-platform": "WebPlayer",
        }
        params["limit"] = limit
        params["offset"] = offset

        response = get(API_URL + url, headers=headers, params=params)
        data = response.json()

        try:
            raise HTTPError(
                f"{url}\nAPI Error {data['error']['status']}: {data['error']['message']}"
            )
        except KeyError:
            return data


class Session(LibrespotSession):
    def __init__(
        self, session_builder: LibrespotSession.Builder, language: str = "en"
    ) -> None:
        """
        Authenticates user, saves credentials to a file and generates api token.
        Args:
            session_builder: An instance of the Librespot Session builder
            langauge: ISO 639-1 language code
        """
        with Loader("Logging in..."):
            super(Session, self).__init__(
                LibrespotSession.Inner(
                    session_builder.device_type,
                    session_builder.device_name,
                    session_builder.preferred_locale,
                    session_builder.conf,
                    session_builder.device_id,
                ),
                ApResolver.get_random_accesspoint(),
            )
            self.connect()
            self.authenticate(session_builder.login_credentials)
            self.__api = Api(self)
            self.__language = language

    @staticmethod
    def from_file(cred_file: Path | str, language: str = "en") -> Session:
        """
        Creates session using saved credentials file
        Args:
            cred_file: Path to credentials file
            language: ISO 639-1 language code for API responses
        Returns:
            Zotify session
        """
        if not isinstance(cred_file, Path):
            cred_file = Path(cred_file).expanduser()
        conf = (
            LibrespotSession.Configuration.Builder()
            .set_store_credentials(False)
            .build()
        )
        session = LibrespotSession.Builder(conf).stored_file(str(cred_file))
        return Session(session, language)

    @staticmethod
    def from_userpass(
        username: str,
        password: str,
        save_file: Path | str | None = None,
        language: str = "en",
    ) -> Session:
        """
        Creates session using username & password
        Args:
            username: Account username
            password: Account password
            save_file: Path to save login credentials to, optional.
            language: ISO 639-1 language code for API responses
        Returns:
            Zotify session
        """
        builder = LibrespotSession.Configuration.Builder()
        if save_file:
            if not isinstance(save_file, Path):
                save_file = Path(save_file).expanduser()
            save_file.parent.mkdir(parents=True, exist_ok=True)
            builder.set_stored_credential_file(str(save_file))
        else:
            builder.set_store_credentials(False)

        session = LibrespotSession.Builder(builder.build()).user_pass(
            username, password
        )
        return Session(session, language)

    @staticmethod
    def from_prompt(
        save_file: Path | str | None = None, language: str = "en"
    ) -> Session:
        """
        Creates a session with username + password supplied from CLI prompt
        Args:
            save_file: Path to save login credentials to, optional.
            language: ISO 639-1 language code for API responses
        Returns:
            Zotify session
        """
        username = input("Username: ")
        password = pwinput(prompt="Password: ", mask="*")
        return Session.from_userpass(username, password, save_file, language)

    def __get_playable(
        self, playable_id: PlayableId, quality: Quality
    ) -> PlayableContentFeeder.LoadedStream:
        if quality.value is None:
            quality = Quality.VERY_HIGH if self.is_premium() else Quality.HIGH
        return self.content_feeder().load(
            playable_id,
            VorbisOnlyAudioQuality(quality.value),
            False,
            None,
        )

    def get_track(self, track_id: str, quality: Quality = Quality.AUTO) -> Track:
        """
        Gets track/episode data and audio stream
        Args:
            track_id: Base62 ID of track
            quality: Audio quality of track when downloaded
        Returns:
            Track object
        """
        return Track(
            self.__get_playable(TrackId.from_base62(track_id), quality), self.api()
        )

    def get_episode(self, episode_id: str) -> Episode:
        """
        Gets track/episode data and audio stream
        Args:
            episode: Base62 ID of episode
        Returns:
            Episode object
        """
        return Episode(
            self.__get_playable(EpisodeId.from_base62(episode_id), Quality.NORMAL),
            self.api(),
        )

    def api(self) -> Api:
        """Returns API Client"""
        return self.__api

    def language(self) -> str:
        """Returns session language"""
        return self.__language

    def is_premium(self) -> bool:
        """Returns users premium account status"""
        return self.get_user_attribute("type") == "premium"

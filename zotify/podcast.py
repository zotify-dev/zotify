# import os
from pathlib import PurePath, Path
import time
from typing import Optional, Tuple

from librespot.metadata import EpisodeId

from zotify.const import ERROR, ID, ITEMS, NAME, SHOW, DURATION_MS
from zotify.termoutput import PrintChannel, Printer
from zotify.utils import create_download_directory, fix_filename, convert_audio_format
from zotify.zotify import Zotify
from zotify.loader import Loader


EPISODE_INFO_URL = 'https://api.spotify.com/v1/episodes'
SHOWS_URL = 'https://api.spotify.com/v1/shows'


def get_episode_info(episode_id_str) -> Tuple[Optional[str], Optional[str]]:
    with Loader(PrintChannel.PROGRESS_INFO, "Fetching episode information..."):
        (raw, info) = Zotify.invoke_url(f'{EPISODE_INFO_URL}/{episode_id_str}')
    if not info:
        Printer.print(PrintChannel.ERRORS, "###   INVALID EPISODE ID   ###")
    duration_ms = info[DURATION_MS]
    if ERROR in info:
        return None, None
    return fix_filename(info[SHOW][NAME]), duration_ms,  fix_filename(info[NAME])


def get_show_episodes(show_id_str) -> list:
    episodes = []
    offset = 0
    limit = 50

    with Loader(PrintChannel.PROGRESS_INFO, "Fetching episodes..."):
        while True:
            resp = Zotify.invoke_url_with_params(
                f'{SHOWS_URL}/{show_id_str}/episodes', limit=limit, offset=offset)
            offset += limit
            for episode in resp[ITEMS]:
                episodes.append(episode[ID])
            if len(resp[ITEMS]) < limit:
                break

    return episodes


def download_podcast_directly(url, filename):
    import functools
    # import pathlib
    import shutil
    import requests
    from tqdm.auto import tqdm

    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(
            f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get('Content-Length', 0))

    # path = pathlib.Path(filename).expanduser().resolve()
    path = Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    r.raw.read = functools.partial(
        r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)

    return path


def download_episode(episode_id) -> None:
    podcast_name, duration_ms, episode_name = get_episode_info(episode_id)
    extra_paths = podcast_name + '/'
    prepare_download_loader = Loader(PrintChannel.PROGRESS_INFO, "Preparing download...")
    prepare_download_loader.start()

    if podcast_name is None:
        Printer.print(PrintChannel.SKIPS, '###   SKIPPING: (EPISODE NOT FOUND)   ###')
        prepare_download_loader.stop()
    else:
        filename = podcast_name + ' - ' + episode_name

        direct_download_url = Zotify.invoke_url(
            'https://api-partner.spotify.com/pathfinder/v1/query?operationName=getEpisode&variables={"uri":"spotify:episode:' + episode_id + '"}&extensions={"persistedQuery":{"version":1,"sha256Hash":"224ba0fd89fcfdfb3a15fa2d82a6112d3f4e2ac88fba5c6713de04d1b72cf482"}}')[1]["data"]["episode"]["audio"]["items"][-1]["url"]

        download_directory = PurePath(Zotify.CONFIG.get_root_podcast_path()).joinpath(extra_paths)
        # download_directory = os.path.realpath(download_directory)
        create_download_directory(download_directory)

        if "anon-podcast.scdn.co" in direct_download_url:
            episode_id = EpisodeId.from_base62(episode_id)
            stream = Zotify.get_content_stream(
                episode_id, Zotify.DOWNLOAD_QUALITY)

            total_size = stream.input_stream.size

            filepath = PurePath(download_directory).joinpath(f"{filename}.ogg")
            if (
                Path(filepath).isfile()
                and Path(filepath).stat().st_size == total_size
                and Zotify.CONFIG.get_skip_existing_files()
            ):
                Printer.print(PrintChannel.SKIPS, "\n###   SKIPPING: " + podcast_name + " - " + episode_name + " (EPISODE ALREADY EXISTS)   ###")
                prepare_download_loader.stop()
                return

            prepare_download_loader.stop()
            time_start = time.time()
            downloaded = 0
            with open(filepath, 'wb') as file, Printer.progress(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024
            ) as p_bar:
                prepare_download_loader.stop()
                for _ in range(int(total_size / Zotify.CONFIG.get_chunk_size()) + 1):
                    data = stream.input_stream.stream().read(Zotify.CONFIG.get_chunk_size())
                    p_bar.update(file.write(data))
                    downloaded += len(data)
                    if Zotify.CONFIG.get_download_real_time():
                        delta_real = time.time() - time_start
                        delta_want = (downloaded / total_size) * (duration_ms/1000)
                        if delta_want > delta_real:
                            time.sleep(delta_want - delta_real)
        else:
            filepath = PurePath(download_directory).joinpath(f"{filename}.mp3")
            download_podcast_directly(direct_download_url, filepath)

    prepare_download_loader.stop()

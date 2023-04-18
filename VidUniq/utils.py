from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlparse

import filetype
import pathvalidate
import requests


def is_video_file(path: Path | str) -> bool:
    obj = filetype.guess(str(path))
    return 'video' in obj.mime


def download_video(url: str, path: Path | str) -> bool:
    response = requests.get(url)
    if response.status_code == HTTPStatus.OK:
        if len(response.content) == 0:
            return False
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    return False


def url_to_path(url: str) -> str:
    o = urlparse(url)
    # Universal max filename = 260
    filename = f'{o.netloc}{".".join(map(lambda x: x[:10], o.path.split("/")))}'[:255]
    return pathvalidate.sanitize_filename(filename)

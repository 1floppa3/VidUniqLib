from urllib.parse import urlparse

import filetype
import pathvalidate


def is_video_file(path: str) -> bool:
    obj = filetype.guess(path)
    return 'video' in obj.mime


def url_to_path(url: str) -> str:
    # Universal max filename = 260
    o = urlparse(url)
    filename = f'{o.netloc}{".".join(map(lambda x: x[:10], o.path.split("/")))}'[:255]
    return pathvalidate.sanitize_filename(filename)

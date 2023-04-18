# VidUniqLib

![Python](https://img.shields.io/badge/Language-Python3.10-yellow.svg?style=flat)
![License](https://img.shields.io/pypi/l/VidUniq?color=blueviolet)
![Version](https://img.shields.io/pypi/v/VidUniq?color=orange)

_**PyPi**_ Video Uniquelizer Library
###### The purpose of the library is to slightly modify the video so that it cannot be matched with the original video

## Installation
Install the current version with [PyPI](https://pypi.org/project/VidUniqLib/):
```bash
pip install VidUniq
```
Or from GitHub:
```bash
pip install https://github.com/1floppa3/VidUniqLib/archive/main.zip
```

## Usage
```python
from VidUniq import VideoUniquelizer

url = 'https://some_invalid_site.site/api.php?wtf=invalid.mp4'
path_list = [
    'some_invalid_folder_IdnaP19f/',
    'some_invalid_file_dmAgo30z.mp4'
]

uniq = VideoUniquelizer(True)

uniq.add_video(url=url)
# uniq.add_video_by_url(url)  Also working

for path in path_list:
    uniq.add_video_by_path(path, remove_after_save_uniquelized=True)

uniq.uniquelize(fadein=1, fadeout=3, speedx=1.1)

uniq.save_videos('uniquelized_videos/')
```

## Example
You can find an example of usage here: [VidUniq](https://github.com/1floppa3/VidUniq)

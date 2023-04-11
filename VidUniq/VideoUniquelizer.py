import random
from http import HTTPStatus
from pathlib import Path
from typing import Any

import requests
import moviepy.video.fx.all as vfx
from moviepy.editor import VideoFileClip

from decorators import convert_string_to_path
from utils import is_video_file, url_to_path


class VideoUniquelizer:
    def __init__(self, verbose: bool):
        self.clips_list: list[dict[str, Any]] = []
        self.verbose = verbose

    @convert_string_to_path(['path'])
    def add_video(self, *, path: Path | str | None = None, url: str | None = None,
                  remove_after_save_uniquelized: bool = False) -> bool:
        result = False
        if path:
            result |= self.add_video_by_path(path, remove_after_save_uniquelized)

        if url:
            result |= self.add_video_by_url(url)
        return result

    @convert_string_to_path(['path'])
    def add_video_by_path(self, path: Path | str, remove_after_save_uniquelized: bool = False) -> bool:
        if any(path == clip_data['path'] for clip_data in self.clips_list):
            if self.verbose:
                print(f'[WARNING] Path "{str(path)}" is already added to this VideoUniquelizer object. (Skip)')
            return False

        if path.exists():
            if path.is_dir():
                for file in path.iterdir():
                    if not file.is_file() or not is_video_file(str(file)):
                        continue
                    self.clips_list.append({'clip': VideoFileClip(str(file)),
                                            'remove': remove_after_save_uniquelized,
                                            'path': file,
                                            'is_url': False})
                return True

            elif path.is_file() and is_video_file(str(path)):
                self.clips_list.append({'clip': VideoFileClip(str(path)),
                                        'remove': remove_after_save_uniquelized,
                                        'path': path,
                                        'is_url': False})
                return True

        if self.verbose:
            print(f'[WARNING] Path "{str(path)}" is invalid. (Skip)')
        return False

    def add_video_by_url(self, url: str) -> bool:
        filename = self.__format_filename(url_to_path(url))
        dl_filename = Path(f'temp_{filename}')

        if any(dl_filename == clip_data['path'] for clip_data in self.clips_list):
            if self.verbose:
                print(f'[WARNING] URL "{url}" is already added to this VideoUniquelizer object. (Skip)')
            return False

        if self.__download_video(url, dl_filename):
            self.clips_list.append({'clip': VideoFileClip(str(dl_filename)),
                                    'remove': True,
                                    'path': dl_filename,
                                    'is_url': True})
            return True

        if self.verbose:
            print(f'[WARNING] URL "{url}" is invalid. (Skip)')
        return False

    def uniquelize(self, *, fadein: int | None = None, fadeout: int | None = None,
                   colorx: float | None = None, gamma: float | None = None,
                   mirror_x: bool | None = None, mirror_y: bool | None = None):
        for clip_data in self.clips_list:
            # Applying video effects
            clip = clip_data['clip']
            if fadein:
                clip = vfx.fadein(clip, duration=fadein)
            if fadeout:
                clip = vfx.fadeout(clip, duration=fadeout)
            if colorx:
                clip = vfx.colorx(clip, colorx)
            if gamma:
                clip = vfx.gamma_corr(clip, gamma)
            if mirror_x:
                clip = vfx.mirror_x(clip)
            if mirror_y:
                clip = vfx.mirror_y(clip)
            clip_data['clip'] = clip

    @convert_string_to_path(['folder'])
    def save_videos(self, folder: Path | str):
        # Create folder if not exists
        folder.mkdir(parents=True, exist_ok=True)

        for clip_data in self.clips_list:
            filter_complex = ['-filter_complex', self.__uniquelize_filter()]

            # Save into folder
            filename = clip_data['path'].stem

            # Removing temp_ and second .mp4 from final path
            if clip_data['is_url']:
                filename = filename[len('temp_'):]
                filename = filename[:-len('.mp4'-1)]

            path = folder.joinpath(self.__format_filename(filename))
            clip_data['clip'].write_videofile(str(path), ffmpeg_params=filter_complex)

            if clip_data['remove']:
                clip_data['path'].unlink()

    @staticmethod
    def __download_video(url: str, path: Path) -> bool:
        response = requests.get(url)
        if response.status_code == HTTPStatus.OK:
            if len(response.content) == 0:
                return False
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        return False

    @staticmethod
    def __uniquelize_filter():
        # Slightly modify video colors
        filter_params = []
        for c in 'rgb':  # 'rgb' - red, green, blue
            for r in 's':  # 'smh' - shadows, midtones, highlights
                filter_params.append(f'colorbalance={c}{r}={random.uniform(-0.15, 0.15)}')
        return random.choice(filter_params)

    @staticmethod
    def __format_filename(name: str) -> str:
        # Uniquelized video filename pattern
        return f'{name}_uniq.mp4'

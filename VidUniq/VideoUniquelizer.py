import random
from pathlib import Path
from typing import Any

import moviepy.video.fx.all as vfx
from moviepy.editor import VideoFileClip

from decorators import convert_string_to_path
from utils import is_video_file, url_to_path, download_video


class VideoUniquelizer:
    def __init__(self, verbose: bool) -> None:
        """
        Create the Video Uniquelizer

        :param verbose: Whether to log VideoUniquelizer actions to console
        """
        self.clips_list: list[dict[str, Any]] = []
        self.verbose = verbose

    @convert_string_to_path(['path'])
    def add_video(self, *, path: Path | str | None = None, url: str | None = None,
                  remove_after_save_uniquelized: bool = False) -> bool:
        """
        Add video by path or by url to the VideoUniquelizer object

        :param path: [Optional] Path to the original video to uniquelize
        :param url: [Optional] URL to the video to uniquelize
        :param remove_after_save_uniquelized: [Optional] Whether to remove the original video after uniquelizing.
               If only 'url' is specified, this parameter has no meaning
        :return: True if video was successfully added, otherwise False
        """
        result = False
        if path:
            result |= self.add_video_by_path(path, remove_after_save_uniquelized)

        if url:
            result |= self.add_video_by_url(url)

        if self.verbose:
            print(f'[WARNING] No video was added by \'add_video()\'')

        return result

    @convert_string_to_path(['path'])
    def add_video_by_path(self, path: Path | str, remove_after_save_uniquelized: bool = False) -> bool:
        """
        Add video by path to the VideoUniquelizer object

        :param path: Path to the original video to uniquelize
        :param remove_after_save_uniquelized: [Optional] Whether to remove the original video after uniquelizing.
        :return: True if video was successfully added, otherwise False
        """
        if any(path == clip_data['path'] for clip_data in self.clips_list):
            if self.verbose:
                print(f'[WARNING] Path "{str(path)}" is already added to this VideoUniquelizer object. (Skip)')
            return False

        if path.exists():
            if path.is_dir():
                for file in path.iterdir():
                    if not file.is_file() or not is_video_file(file):
                        continue
                    self.clips_list.append({'clip': VideoFileClip(str(file)),
                                            'remove': remove_after_save_uniquelized,
                                            'path': file,
                                            'is_url': False})
                    if self.verbose:
                        print(f'#{len(self.clips_list)}. File "{str(file)}" was added')
                return True

            elif path.is_file() and is_video_file(path):
                self.clips_list.append({'clip': VideoFileClip(str(path)),
                                        'remove': remove_after_save_uniquelized,
                                        'path': path,
                                        'is_url': False})
                if self.verbose:
                    print(f'#{len(self.clips_list)}. File "{str(path)}" was added')
                return True

        if self.verbose:
            print(f'[WARNING] Path "{str(path)}" is invalid. (Skip)')
        return False

    def add_video_by_url(self, url: str) -> bool:
        """
        Add video by url to the VideoUniquelizer object

        :param url: URL to the video to uniquelize
        :return: True if video was successfully added, otherwise False
        """
        filename = self.__format_filename(url_to_path(url))
        dl_filename = Path(f'temp_{filename}')

        if any(dl_filename == clip_data['path'] for clip_data in self.clips_list):
            if self.verbose:
                print(f'[WARNING] URL "{url}" is already added to this VideoUniquelizer object. (Skip)')
            return False

        if download_video(url, dl_filename):
            self.clips_list.append({'clip': VideoFileClip(str(dl_filename)),
                                    'remove': True,
                                    'path': dl_filename,
                                    'is_url': True})
            if self.verbose:
                print(f'#{len(self.clips_list)}. File "{str(dl_filename)}" was added')
            return True

        if self.verbose:
            print(f'[WARNING] URL "{url}" is invalid. (Skip)')
        return False

    def uniquelize(self, *, fadein: int | None = None, fadeout: int | None = None,
                   colorx: float | None = None, gamma: float | None = None,
                   mirror_x: bool | None = None, mirror_y: bool | None = None,
                   speedx: float | None = 1.05) -> None:
        """
        Uniquelize videos added to the VideoUniquelizer object, with specified effects

        :param fadein: [Optional] Seconds of fadein effect
        :param fadeout:  [Optional] Seconds of fadeout effect
        :param colorx: [Optional] Factor of colorx effect
        :param gamma: [Optional] Factor of gamma_corr effect
        :param mirror_x: [Optional] Whether to mirror video on the x-axis
        :param mirror_y: [Optional] Whether to mirror video on the y-axis
        :param speedx: [Optional] Speed up or slow down factor of the video
        :return: None
        """
        for clip_data in self.clips_list:
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
            if speedx:
                clip = vfx.speedx(clip, speedx)
            clip_data['clip'] = clip

    @convert_string_to_path(['folder'])
    def save_videos(self, folder: Path | str) -> bool:
        """
        Save all videos from VideoUniquelizer object

        :param folder: Path to the folder where the videos should be saved
        :return: True if at least one video was successfully saved, otherwise False
        """
        if len(self.clips_list) == 0:
            if self.verbose:
                print(f'[WARNING] There is no videos to save in VideoUniquelizer (\'save_videos()\')')
            return False

        # Create folder if not exists
        folder.mkdir(parents=True, exist_ok=True)

        for idx, clip_data in enumerate(self.clips_list):
            filter_complex = ['-filter_complex', self.__get_random_colorbalance_filter()]

            filename = clip_data['path'].stem

            # Removing temp_ from final path if is temp url video
            if clip_data['is_url']:
                filename = filename[len('temp_'):]

            path = folder.joinpath(self.__format_filename(filename))
            clip_data['clip'].write_videofile(str(path), ffmpeg_params=filter_complex, verbose=False, logger=None)
            if self.verbose:
                print(f'[{idx+1}/{len(self.clips_list)}] Video "{str(path)}" successfully saved')

            if clip_data['remove']:
                clip_data['path'].unlink()
            if self.verbose:
                print(f'[{idx + 1}/{len(self.clips_list)}] File "{clip_data["path"]}" was removed')

        return True

    @staticmethod
    def __get_random_colorbalance_filter() -> str:
        """
        Get random ffmpeg colorbalance filter

        :return: Random colorbalance filter
        """
        filter_params = []
        for c in 'rgb':  # 'rgb' - red, green, blue
            for r in 's':  # 'smh' - shadows, midtones, highlights
                filter_params.append(f'colorbalance={c}{r}={random.uniform(-0.15, 0.15)}')
        return random.choice(filter_params)

    @staticmethod
    def __format_filename(name: str) -> str:
        """
        Apply uniq pattern to filename (without extension)

        :param name: File name (without extension)
        :return: Final filename
        """
        return f'{name}_uniq.mp4'

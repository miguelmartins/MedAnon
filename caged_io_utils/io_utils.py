import os
import re
import ffmpeg
import shutil

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm
from typing import Dict, List


class VideoExtractor:
    def __init__(self, data_path: str, video_codec: str = '.mp4'):
        self.data_path = data_path
        self.video_codec = video_codec

    def _get_path_data(self) -> Dict[int, Dict[str, List[str]]]:
        """
        Given the data directory return a dictionary containing the required
        metadata for I/O
        :param data_path: A string containing the relative path of the data
        :return: A dictionary d[directory, video_list]
        """
        return \
            {int(video_dir): {
                f'{self.data_path}/{video_dir}/video_files': os.listdir(f'{self.data_path}/{video_dir}/video_files')}
                for video_dir in os.listdir(self.data_path) if os.path.isdir(f'{self.data_path}/{video_dir}')}

    def _get_video_paths(self, video_dict: Dict[str, List[str]]) -> List[str]:
        """
        :param video_dict: A dictionary containing the video file directory metadata
        :return: A list of all paths pointing to video files in the directory
        """
        return [f'{key}/{value}'
                for key in video_dict.keys()
                for values in video_dict.values() for value in values if value.endswith(self.video_codec)]

    def canonical_format(self):
        data_dict = self._get_path_data()
        for key, dict_values in data_dict.items():
            video_sources = self._get_video_paths(dict_values)
            for video_source in video_sources:
                target = re.sub('\..+', '', video_source) + '.mp4'
                os.system(f'mv {video_source} {target}')

    def __call__(self, target_path: str):
        self.canonical_format()
        # absolute_path = os.getcwd()
        if not os.path.exists(target_path):
            try:
                os.mkdir(target_path)
            except:
                print(f"Failed to create target directory: {target_path}")
        path_data_dict = self._get_path_data()
        for key, dict_values in path_data_dict.items():
            video_sources = sorted(self._get_video_paths(dict_values))
            if len(video_sources) > 1:
                clips = [VideoFileClip(c) for c in video_sources]
                concatenated_clip = concatenate_videoclips(clips)
                # write the output video file
                concatenated_clip.write_videofile(f'{target_path}/{key}_temp.mp4')
                command = f'ffmpeg -i {target_path}/{key}_temp.mp4.mp4 -filter:v "crop=1371:1080:549:0" -c:a copy {target_path}/{key}.mp4'
                os.system(command)
                os.system(f'rm -R {target_path}/{key}_temp.mp4')
            else:
                command = f'ffmpeg -i {video_sources[0]}.mp4 -filter:v "crop=1371:1080:549:0" -c:a copy {target_path}/{key}.mp4'
                os.system(command)


def convert_mov_to_mp4(mov_file: str):
    # Answer to: https://stackoverflow.com/questions/64519818/converting-mkv-files-to-mp4-with-ffmpeg-python
    name, ext = os.path.splitext(mov_file)
    out_name = f'{name}.mp4'
    ffmpeg.input(mov_file).output(out_name, vcodec='h264').run()
    print("Finished converting {}".format(mov_file))


def system_mov_to_mp4(mov_file: str):
    name, ext = os.path.splitext(mov_file)

    out_name = 'test.mp4'
    print(name, " ext")
    command = 'ffmpeg -i CAGED_Videos/20220106084748-0.mp4 -filter:v "crop=1371:1080:549:0" -c:a copy out.mp4'
    os.system(command)
    print("Finished converting {}".format(mov_file))


def convert_videos(path: str):
    # ffmpeg -i CAGED_Videos/20220106084748-0.mp4 -filter:v "crop=1371:1080:549:0" -c:a copy out.mp4
    #  ffmpeg -i out.mp4 -c:v libx265 outh265.mp4

    # ffmpeg -y -i out.mp4 -c:v libx265 -b:v 1365k -x265-params pass=1 -an -f null /dev/null && \
    # ffmpeg -i out.mp4 -c:v libx265 -b:v 1365k -x265-params pass=2 out_test.mp4
    videos = os.listdir(path)
    for video in tqdm(videos):
        system_mov_to_mp4(f'{path}/{video}')
        break

import os
import ffmpeg
import shutil
from tqdm import tqdm
from typing import Dict, List


class VideoExtractor:
    def __init__(self, data_path: str, video_codec: str = '.mov'):
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

    def __call__(self, target_path: str):
        absolute_path = os.getcwd()
        if not os.path.exists(target_path):
            try:
                os.mkdir(target_path)
            except:
                print(f"Failed to create target directory: {target_path}")
        path_data_dict = self._get_path_data()
        for key, dict_values in path_data_dict.items():
            video_sources = self._get_video_paths(dict_values)
            for id_, source in enumerate(video_sources):
                shutil.copy(f'{absolute_path}/{source}', f'{target_path}/{key}-{id_}.mov')


def convert_mov_to_mp4(mov_file: str):
    # Answer to: https://stackoverflow.com/questions/64519818/converting-mkv-files-to-mp4-with-ffmpeg-python
    name, ext = os.path.splitext(mov_file)
    out_name = f'{name}.mp4'
    ffmpeg.input(mov_file).output(out_name, vcodec='h264').run()
    print("Finished converting {}".format(mov_file))


def convert_videos(path: str):
    videos = os.listdir(path)
    for video in tqdm(videos):
        convert_mov_to_mp4(f'{path}/{video}')

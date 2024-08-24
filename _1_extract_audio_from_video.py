import os

from moviepy.editor import VideoFileClip
from _utils import AUDIO_DIR, create_new_logger, generate_unique_file_name


def extract_audio(video_file_path):
    logger = create_new_logger()
    file_name_with_ext = os.path.basename(video_file_path)
    file_name = generate_unique_file_name(file_name_with_ext.split('.')[0])

    curr_audio_dir = f'{AUDIO_DIR}/{file_name}'
    os.makedirs(curr_audio_dir, exist_ok=True)
    audio_file_name = f'{file_name}.wav'
    audio_file_path = f'{curr_audio_dir}/{audio_file_name}'

    try:
        video_clip = VideoFileClip(video_file_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_file_path)
        video_clip.close()
        logger.info(f"Audio extracted successfully for {video_file_path}")
        print(f"Audio extracted successfully for {video_file_path}")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        print("An error occurred:", e)

    return file_name

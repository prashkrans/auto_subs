import os
import json
import logging
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Timestamped_word:
    start_time: int # both start_time and end_time are in ms (So, multiply by 1000 from segments)
    end_time: int
    word: str

    def to_dict(self):
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "word": self.word
        }

with open('config.json') as f:
    config = json.load(f)

with open('word_options.json') as f:
    word_options_list = json.load(f)

RESOURCES_DIR = config['RESOURCES_DIR']
VIDEO_DIR = config['VIDEO_DIR']
AUDIO_DIR = config['AUDIO_DIR']
JSON_DIR = config['JSON_DIR']
SUBTITLES_DIR = config['SUBTITLES_DIR']
OUTPUT_DIR = config['OUTPUT_DIR']
TMP_OUTPUT_DIR = config['TMP_OUTPUT_DIR']
TMP_SUBTITLES_DIR = config['TMP_SUBTITLES_DIR']
LOGS_DIR = config['LOGS_DIR']
FONTS_DIR = config['FONTS_DIR']
THUMBNAILS_DIR = config['THUMBNAILS_DIR']
PARAMS_JSON_1_PATH = config['PARAMS_JSON_1_PATH']
PARAMS_JSON_2_PATH = config['PARAMS_JSON_2_PATH']
FONTS_JSON_PATH = config['FONTS_JSON_PATH']

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SUBTITLES_DIR, exist_ok=True)

word_options_index_map = {
    "1-2 words per line": "1",
    "3-4 words per line": "2",
    "5-7 words per line": "3",
    "8-10 words per line": "4",
    "11-12 words per line": "5",
    "13-15 words per line": "6",
}

video_quality_map = { # maps video quality to crf value that varies from 0 to 51, lower the better quality
    'highest': '12',
    'high': '15',
    'medium': '18',
    'low': '20',
    'lowest': '23',
    'reduced': '30'
}

def json_read(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)  # Don't use file.read() here

def json_write(json_path, text):
    with open(json_path, 'w') as file:
        json.dump(text, file, indent=4)

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_text_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

config = json_read('config.json')
word_options_json_path = config['WORD_OPTIONS_JSON_PATH']


def get_video_files_from_dir(dir):
    # List files in the directory
    files = os.listdir(dir)
    video_file_names_with_ext = []

    for file in files:
        if (file.lower().endswith(('.mp4', '.mkv', '.mov'))): # Currently supporting three types of video extension
            video_file_names_with_ext.append(file)

    return video_file_names_with_ext

def convert_time(decimal_time):
    minutes = 0
    seconds = int(decimal_time)
    milliseconds = int((decimal_time - seconds) * 1000)

    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def generate_log_name():
    # Get current date and time
    current_datetime = datetime.now()

    # Format date and time as strings
    date_string = current_datetime.strftime('%Y-%m-%d')
    time_string = current_datetime.strftime('%H%M%S')

    # Create filename
    filename = f"{date_string}_{time_string}"

    return filename

def get_curr_log_file_path():
    log_name = generate_log_name()
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file_path = f'{LOGS_DIR}/{log_name}.log'
    print(f'Log file path: {log_file_path}')
    return log_name, log_file_path

def create_new_logger():
    curr_log_file_name, curr_log_file_path = get_curr_log_file_path()
    log_path_dict = {
        'log_name': curr_log_file_name,
        'log_path': curr_log_file_path
    }
    json_write(f'./logs.json', log_path_dict)
    logging.basicConfig(filename=curr_log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(curr_log_file_path)

def get_curr_logger():
    log_path_dict = json_read(f'./logs.json')
    curr_log_file_path = log_path_dict['log_path']
    logging.basicConfig(filename=curr_log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s') # Dont delete the lines
    return logging.getLogger(curr_log_file_path)

def generate_unique_file_name(file_name):
    now = datetime.now()
    unique_file_name = f'{file_name}_{now.strftime("%Y-%m-%d_%H-%M-%S-%f")}'
    return unique_file_name

def generate_current_time_suffix():
    now = datetime.now()
    current_time_suffix = f'{now.strftime("%H-%M-%S-%f")}'
    return current_time_suffix

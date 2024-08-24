import json
import os

from _2_generate_transcript_matrix import Timestamped_word
from _utils import (get_curr_logger, JSON_DIR, word_options_index_map, json_read, word_options_json_path, SUBTITLES_DIR,
                    write_text_file)


def dict_to_timestamped_word(d):
    return Timestamped_word(
        start_time=d["start_time"],
        end_time=d["end_time"],
        word=d["word"]
    )

def transcript_json_to_transcript_matrix(transcript_json_path):
    # Read the JSON data from the file
    with open(transcript_json_path, 'r') as f:
        transcript_matrix_dict = json.load(f)

    # Convert the list of dictionaries back to a list of lists of Timestamped_word objects
    transcript_matrix = [
        [dict_to_timestamped_word(word_dict) for word_dict in row]
        for row in transcript_matrix_dict
    ]

    return transcript_matrix

def convert_time(time_in_ms):
    # Calculate hours, minutes, seconds, and milliseconds
    hours = int(time_in_ms // 3600000)
    minutes = int((time_in_ms % 3600000) // 60000)
    seconds = int((time_in_ms % 60000) // 1000)
    ms = int(time_in_ms % 1000)
    ms //= 10 # Since the format is H:MM:SS:MS
    # Format the time string
    time_string = f"{hours}:{minutes:02}:{seconds:02}.{ms:02}"

    return time_string

def convert_time_for_vtt_and_srt(time_in_ms, format):
    # Calculate hours, minutes, seconds, and milliseconds
    hours = int(time_in_ms // 3600000)
    minutes = int((time_in_ms % 3600000) // 60000)
    seconds = int((time_in_ms % 60000) // 1000)
    ms = int(time_in_ms % 1000)
    # Format the time string
    if(format == ".vtt"):
        # This time format introduces slight error in subtitles timings
        # time_string = f"{hours:02}:{minutes:02}:{seconds:02}.{ms:03}" # HH:MM:SS.MSS

        # This time format introduces the maximum error in subtitles timings
        # time_string = f"{minutes:02}:{seconds:02}.{ms//10}" # MM:SS.MS - no hours here

        # This time format for .vtt files is the most accurate for ffmpeg to embed them into videos
        time_string = f"{minutes:02}:{seconds:02}.{ms:03}" # MM:SS.MSS - no hours here
    else:
        time_string = f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

    return time_string


def convert_transcript_to_subtitles(transcript_text, file_name, params_dict):
    logger = get_curr_logger()
    curr_json_dir = f'{JSON_DIR}/{file_name}'
    transcript_json_name = f'{file_name}_transcript.json'
    transcript_json_path = f'{curr_json_dir}/{transcript_json_name}'
    transcript_matrix = transcript_json_to_transcript_matrix(transcript_json_path)

    lines = transcript_text.splitlines()
    
    for row, line in zip(transcript_matrix, lines):
        print(f"line: {line}")
        words = line.split(" | ") # Since, delimiter used was " | " (space-pipe-space)
        for node, word in zip(row, words):
            node.word = word

    logger.info(f'params_dict_2: {params_dict}')
    print(f'params_dict_2: {params_dict}')

    # Reading params_dict
    is_upper = eval(params_dict["is_upper"])

    word_options_index = word_options_index_map[params_dict["word_options_key"]]
    word_options = json_read(word_options_json_path)
    max_words_per_line = int(word_options[word_options_index]["max_words_per_line"])
    max_line_width = int(word_options[word_options_index]["max_line_width"])


    curr_num_words = 0
    curr_length = 0
    vtt_line = ""
    vtt_lines = ["WEBVTT\n"]
    srt_lines = []
    srt_index = 1
    unicode_lines = []
    for i in range(len(transcript_matrix)):
        for j in range(len(transcript_matrix[i])):

            current_word = transcript_matrix[i][j].word
            if (is_upper):
                current_word = current_word.upper()
            word_start_time = transcript_matrix[i][j].start_time
            word_end_time = transcript_matrix[i][j].end_time

            # Use double braces {{}} in an f-string to include the literal braces in the output.
            # Don't use "{\\r} " instead use " {\\r}" as the former treats space as a different word instance thus giving bad animations

            # Changes made to fix one word's length exceeding max_line_width of 9 instead of increasing mwl instead
            if(curr_num_words == 0
                    or (curr_num_words > 0 and curr_num_words <= max_words_per_line and curr_length <= max_line_width)):
                if(curr_num_words == 0):
                    line_start_time = word_start_time
                vtt_line += current_word + " "
                curr_num_words += 1
                curr_length += len(current_word)
                line_end_time = word_end_time
                if(
                    current_word.endswith((".", "?"))
                    # The line below makes sure that one word is appended to the line even if it exceeds max_line_width of 9 for word options index of 1
                    or curr_length >= max_line_width
                    or (
                        j+1 < len(transcript_matrix[i])
                        and len(transcript_matrix[i][j+1].word) + curr_length > max_line_width
                    )
                    or curr_num_words == max_words_per_line
                    or (i==len(transcript_matrix)-1 and j==len(transcript_matrix[i])-1)
                ):
                    # [:-1] skips the trailing space for each line, but not using it for line as "{\r}" is at the end
                    vtt_lines.append(f"{convert_time_for_vtt_and_srt(line_start_time, '.vtt')} --> "
                                     f"{convert_time_for_vtt_and_srt(line_end_time, '.vtt')}\n{vtt_line[:-1]}\n")
                    srt_lines.append(f"{srt_index}\n{convert_time_for_vtt_and_srt(line_start_time, '.srt')} --> "
                                     f"{convert_time_for_vtt_and_srt(line_end_time, '.srt')}\n{vtt_line[:-1]}\n")
                    srt_index += 1
                    curr_num_words = 0
                    curr_length = 0
                    vtt_line = ""

    vtt_text = "\n".join(vtt_lines)
    srt_text = "\n".join(srt_lines)

    curr_subtitles_dir = f'{SUBTITLES_DIR}/{file_name}'
    os.makedirs(curr_subtitles_dir, exist_ok=True)

    vtt_subtitle_path = f'{curr_subtitles_dir}/{file_name}.vtt'
    srt_subtitle_path = f'{curr_subtitles_dir}/{file_name}.srt'
    write_text_file(vtt_subtitle_path, vtt_text)
    write_text_file(srt_subtitle_path, srt_text)

    logger.info(f'Generated .vtt and .srt subtitles directly from segments.')
    print(f'Generated .vtt and .srt subtitles directly from segments.')

    return vtt_subtitle_path, srt_subtitle_path

import os
import torch
import whisper

from _utils import get_curr_logger, AUDIO_DIR, Timestamped_word, JSON_DIR, json_write, write_text_file


def generate_transcript_matrix(file_name, params_dict):
    logger = get_curr_logger()

    logger.info(f'params_dict_1: {params_dict}')
    print(f'params_dict_1: {params_dict}')

    curr_audio_dir = f'{AUDIO_DIR}/{file_name}'
    audio_file_name = f'{file_name}.wav'
    audio_file_path = f'{curr_audio_dir}/{audio_file_name}'

    model_name = "large-v2"
    # model_name = "large-v3"
    # model_name = "medium"
    device = "cuda" if torch.cuda.is_available() else "cpu"  # use "cpu" for deployment in cloud
    model = whisper.load_model(model_name, device) # Works but is slow, uses CUDA by default
    
    logger.info(f'Loaded model: {model_name} successfully on device {device}')
    print(f'Loaded model: {model_name} successfully on device {device}')
    logger.info(f'Processing audio file: {audio_file_name}')
    print(f'Processing audio file: {audio_file_name}')
    
    task = 'transcribe'  # Task could be transcription to source audio language or translation to english only
    translate_to_english = eval(params_dict['translate_to_english'])

    if translate_to_english == True:
        task = 'translate'
        logger.info(f'task: {task} to english')
        print(f'task: {task} to english')
    else:
        logger.info(f'task: {task} to source audio language')
        print(f'task: {task} to source audio language')

    result = model.transcribe(
        audio_file_path,
        task=task,
        word_timestamps=True
    )

    segments = result['segments']
    # print(f'segments: {segments}')

    transcript_matrix = []
    for i in range(len(segments)):
        words = segments[i]["words"]
        current_row = []
        for j in range(len(words)):
            word_instance = Timestamped_word(
                start_time = int(words[j]["start"]*1000),
                end_time = int(words[j]["end"]*1000),
                word = words[j]["word"][1:], #IMP - Using [1:] as words from whisper contain a space as prefix
            )
            current_row.append(word_instance)
        transcript_matrix.append(current_row)

    # Convert transcript_matrix to a list of lists of dictionaries
    transcript_matrix_2d_list = [
        [word_instance.to_dict() for word_instance in row]
        for row in transcript_matrix
    ]

    curr_json_dir = f'{JSON_DIR}/{file_name}'
    os.makedirs(curr_json_dir, exist_ok=True)
    transcript_matrix_json_name = f'{file_name}_transcript.json'
    transcript_matrix_json_path = f'{curr_json_dir}/{transcript_matrix_json_name}'
    json_write(transcript_matrix_json_path, transcript_matrix_2d_list)

    lines = []
    for i in range(len(transcript_matrix)):
        line = ""
        for j in range(len(transcript_matrix[i])):
            delimiter = " | " # Delimiter used is (space-pipe-space)
            if(j == len(transcript_matrix[i])-1):
                delimiter = "" # i.e. except the last word
            line += transcript_matrix[i][j].word + delimiter
        lines.append(line)
    transcript_text = "\n".join(lines)

    transcript_text_file_name = f'{file_name}_tt.txt'
    transcript_text_file_path = f'{curr_json_dir}/{transcript_text_file_name}'
    write_text_file(transcript_text_file_path, transcript_text)
    return transcript_text

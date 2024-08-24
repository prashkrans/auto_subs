import os
import subprocess
import time

from _utils import get_curr_logger, SUBTITLES_DIR, TMP_OUTPUT_DIR, generate_current_time_suffix, video_quality_map, \
    json_read, FONTS_JSON_PATH, FONTS_DIR

logger = get_curr_logger()
def embed_subtitles(
        input_video_path,
        file_name,
        params_dict
):
    logger = get_curr_logger()
    start_time = time.time()

    curr_subtitles_dir = f"{SUBTITLES_DIR}/{file_name}"
    subtitles_path = f"{curr_subtitles_dir}/{file_name}.vtt"
    curr_tmp_output_dir = f"{TMP_OUTPUT_DIR}/{file_name}"
    os.makedirs(curr_tmp_output_dir, exist_ok=True)
    video_ext = "mp4"
    # video_ext = "mov"
    output_video_path = f"{curr_tmp_output_dir}/{file_name[:-16]}_{generate_current_time_suffix()}.{video_ext}"

    logger.info(f'params_dict_3: {params_dict}')
    print(f'params_dict_3: {params_dict}')

    crf = video_quality_map[params_dict["video_quality_key"]]

    fonts_dict = json_read(FONTS_JSON_PATH)

    font_name = params_dict["eng_font"]
    font_lang = "english_fonts"

    font_file_name = fonts_dict[font_lang][font_name]
    font_path = f'{FONTS_DIR}/{font_lang}/{font_file_name}'

    logger.info(f'font_lang: {font_lang} | font_file_name: {font_file_name} | font_name: {font_name}')
    print(f'font_lang: {font_lang} | font_file_name: {font_file_name} | font_name: {font_name}')

    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_video_path,          # Input video file
        # '-vf', f"ass={input_subtitle_path}",  # ass doesn't allow custom fonts | Don't delete the comments
        # "-vf", f"subtitles={input_subtitle_path}",
        "-vf", f"subtitles={subtitles_path}:fontsdir={font_path}:force_style='Fontname={font_name}'", # Works the best
        '-c:a', 'copy',            # Copy audio codec
        '-c:v', 'libx264',         # Re-encode video codec (older but stable)
        # '-c:v', 'libx265',       # Re-encode video codec (newer more efficient)
        '-preset', 'ultrafast',    # Preset for faster encoding - increases the file size
        # '-preset', 'medium',     # Preset for slower encoding - only slightly increases the file size TODO - Revert
        '-crf', f'{crf}',          # Constant Rate Factor for quality (lower is better)
        '-y',                      # Overwrite output files without asking
        output_video_path          # Output video file
    ]


    # Run ffmpeg command without logs
    subprocess.run(ffmpeg_cmd)  # Note the use of subprocess.run here

    end_time = time.time()
    elapsed_time = int(end_time - start_time)
    print(f'Time taken to complete {elapsed_time} seconds')

    logger.info('The adv ssa subtitle was successfully embedded to the input video')
    logger.info('The entire process completed successfully')
    logger.info('####################################################################')

    print('The adv ssa subtitle was successfully embedded to the input video')
    print('The entire process completed successfully')

    return output_video_path

import gradio as gr

from _1_extract_audio_from_video import extract_audio
from _2_generate_transcript_matrix import generate_transcript_matrix
from _3_format_subtitles import convert_transcript_to_subtitles
from _4_embed_subtitles import embed_subtitles
from _utils import (AUDIO_DIR, SUBTITLES_DIR, TMP_OUTPUT_DIR, TMP_SUBTITLES_DIR, PARAMS_JSON_1_PATH, PARAMS_JSON_2_PATH,
                    create_new_logger, get_curr_logger, json_write, write_text_file, read_text_file,
                    generate_unique_file_name, video_quality_map, THUMBNAILS_DIR)

js = """
function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';

    var text = 'AutoSubs: Auto-generate and embed subtitles in videos with multiple font options';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.5s';
                letter.innerText = text[i];

                container.appendChild(letter);

                setTimeout(function() {
                    letter.style.opacity = '1';
                }, 100);
            }, i * 100);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);

    return 'Animation created';
}
"""

# Custom CSS for video responsiveness
# css = """
# #video-preview video {
#     width: auto;  /* Make the video width responsive */
#     height: auto; /* Maintain the aspect ratio */
# }
# """


def extract_audio_and_gen_transcript_matrix_gr(
    input_video_path,
    translate_to_english,
):
    logger = create_new_logger()

    # Destroy params_1.json
    json_write(PARAMS_JSON_1_PATH, '')

    # Create dictionary
    params_dict_1 = {
        'input_video_path': f'{input_video_path}',
        'translate_to_english': f'{translate_to_english}',
    }

    # We don't read params_dict_1, _2 or _3 from local as it might get changed if another concurrent user changes it.
    # Only saving them to refer the format for testing and debugging
    json_write(PARAMS_JSON_1_PATH, params_dict_1)

    file_name = extract_audio(input_video_path)
    transcript_text = generate_transcript_matrix(file_name, params_dict_1)

    proc_completed_message = ("Transcript generated successfully. Please review and edit it if required, then select "
                              "transcription language and click on \"Process Subtitles\" button to continue")

    logger.info(proc_completed_message)
    print(proc_completed_message)

    return (
        proc_completed_message,
        gr.Textbox(value=transcript_text, interactive=True),
        file_name,
        gr.Button(interactive=True)
    )

def eng_font_change_gr(eng_font_comp):
    font_lang = "english_fonts"
    font_name = eng_font_comp
    gif_path = f"{THUMBNAILS_DIR}/{font_lang}/{font_name}.gif"
    return gr.Image(value=gif_path)

def format_subtitles_and_embed_subtitles_gr(
    input_video_path,
    transcript_text,
    file_name,
    is_upper,
    word_options_key,
    eng_font,
    video_quality_key
):
    logger = get_curr_logger()

    # Destroy params_2.json
    json_write(PARAMS_JSON_2_PATH, '')

    params_dict_3 = {
        'input_video_path': f'{input_video_path}',
        'file_name': f'{file_name}',
        'is_upper': f'{is_upper}',
        'word_options_key': f'{word_options_key}',
        'eng_font': f'{eng_font}',
        'video_quality_key': f'{video_quality_key}'
    }

    json_write(PARAMS_JSON_2_PATH, params_dict_3)

    download_vtt_path, download_srt_path = convert_transcript_to_subtitles(transcript_text, file_name, params_dict_3)
    download_video_path = embed_subtitles(input_video_path, file_name, params_dict_3)

    proc_completed_message = 'Subtitles embedding completed. Please download the video along with the .vtt and .srt subtitles.'

    logger.info(proc_completed_message)
    print(proc_completed_message)

    return (
        proc_completed_message,
        gr.DownloadButton(
            value=download_vtt_path,
            interactive=True,
            visible=True
        ),
        gr.DownloadButton(
            value=download_srt_path,
            interactive=True,
            visible=True
        ),
        gr.Video( # There is an issue with returning gr.Video that it doesn't refresh
            value=download_video_path,
            interactive=False, # Keep interactive as false even in a return
            visible=True
        )
    )

with gr.Blocks(
    title='AutoSubs', 
    theme=gr.themes.Soft(), 
    js=js,
    # css=css,
    analytics_enabled=False, 
    fill_height=True
) as auto_subs:
    filename_comp = gr.Textbox(value='', visible=False)
    with gr.Row(variant="compact"):
        with gr.Column(variant="panel"):
            input_video_path_comp = gr.Video(
                label="Upload Video",
                width=720,
                height=480
            ) # Don't change the height and width
            translate_to_english_comp = gr.Checkbox(
                label='Translate to english',
                info='It translates the audio and generates subtitles in English.',
                value=False,
            )
            ### Taking params_1 input till here
            button1 = gr.Button("Generate Subtitles", variant="primary", scale=1)
        with gr.Column(variant="panel", scale=1):
            notify_text_1 = gr.Textbox(
                label='Subtitles Generation Status',
                lines=1,
                placeholder='Upload your video and then click on "Generate Subtitles" button to continue',
                scale=1
            )
            transcript_text_comp = gr.Textbox(label="Preview & Edit Subtitles", lines=22, interactive=False)
    with gr.Row(variant="panel"):
        with gr.Column(variant="panel"):
            dummy_button_1 = gr.Button(value="Customize Subtitles", variant="stop")
            # with gr.Row(variant="panel"):
            #     with gr.Column(variant="panel"):
            is_upper_comp = gr.Checkbox(
                info="It converts the subtitles to uppercase",
                label='Upper Case',
                value=False,
                visible=True
            )
            word_options_key_comp = gr.Dropdown(
                choices=[
                    "1-2 words per line", "3-4 words per line", "5-7 words per line",
                    "8-10 words per line", "11-12 words per line", "13-15 words per line",
                ],
                info="It selects the number of words per line for the subtitles",
                label="Words Per Line",
                value="3-4 words per line"
            )
            video_quality_key_comp = gr.Dropdown(
                choices=["highest", "high", "medium", "low", "lowest", "reduced"],
                value="reduced",
                label="Video Quality",
                info="It sets the quality of the output video"
            )
            eng_font_comp = gr.Dropdown(  # TODO - Convert font index from a dropdown to dataset (better)
                choices=[
                    "Pricedown", "Komika Axis", "Bungee", "Kalam",
                    "Bangers", "Blenda Script", "Luckiest Guy", "HACKED",
                    "Heavy Heap", "a Alloy Ink", "Ghastly Panic", "Merienda",
                    "Neuropol", "a Abstract Groovy", "Shrikhand", "Nautilus Pompilius",
                    "Muska", "Super Rugged", "Space Mono", "Roboto",
                ],
                value="Pricedown",
                label="English Fonts",
                info="It selects the font type for the text in Roman Script",
                visible=True  # Made it visible by default as English is the default language
            )
        # with gr.Column(variant="panel"):
            font_preview_comp = gr.Image(
                value=f"{THUMBNAILS_DIR}/english_fonts/Pricedown.gif",
                type="filepath",
                height=None,
                width=None,
                label="Font Preview",
                show_download_button=False,
            )
            button2 = gr.Button("Embed Subtitles", variant="primary", interactive=False, scale=1)
            notify_text_2 = gr.Textbox(
                label='Subtitles embedding Status',
                lines=2,
                placeholder="Waiting for subtitles embedding...",
                visible=False  # Making this invisible as it doesn't fit with the current layout
            )
        with gr.Column(variant="panel", scale=2):
            video_preview_comp = gr.Video(
                label="Subbed Video",
                interactive=False,
                visible=False,
                show_download_button=True,
                # elem_id="video-preview"  # Adding an element ID for custom styling
                width = 1080,
                height = 720
            )
            with gr.Row(variant="panel"):
                with gr.Column(variant="panel"):
                    vtt_download_button = gr.DownloadButton(
                        label='Download Subs as .vtt',
                        variant='primary',
                        interactive=False,
                        visible=False
                    )
                with gr.Column(variant="panel"):
                    srt_download_button = gr.DownloadButton(
                        label='Download Subs as .srt',
                        variant='primary',
                        interactive=False,
                        visible=False
                    )

    button1.click(
        fn=extract_audio_and_gen_transcript_matrix_gr,
        inputs=[
            input_video_path_comp,
            translate_to_english_comp
        ],
        outputs=[
            notify_text_1,
            transcript_text_comp,
            filename_comp,
            button2
        ]
    )

    eng_font_comp.change(
        fn=eng_font_change_gr,
        inputs=eng_font_comp,
        outputs=font_preview_comp
    )

    button2.click(
        fn=format_subtitles_and_embed_subtitles_gr,
        inputs=[
            input_video_path_comp,
            transcript_text_comp,
            filename_comp,
            is_upper_comp,
            word_options_key_comp,
            eng_font_comp,
            video_quality_key_comp
        ],
        outputs=[
            notify_text_2,
            vtt_download_button,
            srt_download_button,
            video_preview_comp
        ]
    )


# Keep both max_size and default_concurrency_limit as 1
auto_subs.queue(
    api_open=False,
    max_size=1,
    default_concurrency_limit=1
).launch(server_port=7880)  # Local launch
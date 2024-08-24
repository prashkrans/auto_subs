# Auto Subs
A Gradio web application in Python for automatically generating and embedding subtitles in videos, with customization options.

### Demo Video:

### Prerequisites:
- Python 3.10 (Might work with lower/higher versions as well).
- NVIDIA CUDA for faster processing.
- VRAM requirements: Atleast 6GB VRAM for `medium` and 11 GB for `large-v2` models of whisper.
- Also, works on CPU only but is awfully slow.
- Developed on Debian 12, please make the required changes for other OS or distros.

### Setup:
1. Clone the repo and move to the root dir.
```commandline
git clone https://github.com/prashkrans/auto_subs.git
cd auto_subs/
```
2. Create a python virtual environment.
```commandline
python3 -m venv env_auto_subs
source env_auto_subs/bin/activate
```
3. Install the requirements (Might take some time).   
```
pip install -r requirements.txt
```

### Usage:
1. Source `env_auto_subs`  
`source env_auto_subs/bin/activate`
2. Run `main_gradio_app.py`  
`python3 main_gradio_app.py`
3. Open the local host link in a web browser by either `Ctrl + Left Click` on the link provided in the terminal or copying and pasting the same in the browser.
4. Upload the video to be subbed.
5. Click on `Generate Subtitles` and wait for the subtitles to be generated.
6. Review and edit the generated subtitles if required.
7. Customize subtitles as required and then click on `Embed Subtitles` to hard burn the subtitles in the provided video.
8. Download the video by clicking in the top right corner of the video preview.
9. Download .vtt and .srt subtitles if required.

### Note:
- Change model name `model_name = "large-v2"` to `medium` or `large-v3` in line 23 of [_2_generate_transcript_matrix.py](_2_generate_transcript_matrix.py) to use different available models of open-ai whisper.
- Ignore the error: `/tmp/tmpnbw41k68/main.c:4:10: fatal error: Python.h: No such file or directory
    4 | #include <Python.h>`
- When running for the first time, it downloads the whisper models which takes some time as its about 2GBs in size. 


### License:
This app and ViTMatte's model weights are released under the MIT License. See [LICENSE](LICENSE) for further details.

### Credits:
- [Open AI Whisper](https://github.com/openai/whisper) | [MIT License](https://github.com/openai/whisper?tab=MIT-1-ov-file)
- [Gradio](https://github.com/gradio-app/gradio) | [Apache-2.0 License](https://github.com/gradio-app/gradio?tab=Apache-2.0-1-ov-file)
- [Moviepy](https://github.com/Zulko/moviepy) | [MIT License](https://github.com/Zulko/moviepy?tab=MIT-1-ov-file)



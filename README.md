# Piano-AI-Transcription

This is a simple Python "wrapper" that utilizes ByteDance's amazing polyphonic transcription tool. The model is not widely-known but it is definitely a powerful tool. In my opinion, no other models beat this.

It also just supports direct YouTube URL input so you don't have to use shady sites to download audio.

I plan to add a youtube download module later so users can simply copy the link and let the tool handle the rest.

# Source Model

ByteDance: https://github.com/bytedance/piano_transcription

# Usage

1. Install python3.7 from https://www.python.org/downloads/
2. Drag any audio file to the **Input** folder.
3. Or you can follow the instructions in command line and directly render Youtube URLs. (Pretty handy right?)
4. Open terminal and type **python3.7** then press **SPACE**
5. Drag **RUN.py** and press **ENTER**
6. MIDI will be exported to the **Output** folder.
7. Currently, the python script will automatically remove the audio files in Input to save storage.

# Examples

The Input and Output folder in this repo already contains an example render of Charles Cornell's sexy "Heart and Soul" jazz piano performance.

The output file is in MIDI format and you can use any DAW and VST to render the audio yourself.

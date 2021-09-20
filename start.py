import re
import subprocess
import sys

def install(MODULE):
    subprocess.check_call([sys.executable, "-m", "pip", "install", MODULE])

def req_install(PATH):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", PATH])

def pip_install():
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

pip_install()

import os
import shutil
from pathlib import Path
d = os.path.dirname(os.path.realpath(__file__))
input = d + "/Input"
output = d + "/Output"
home = os.path.expanduser('~')

if not os.path.isdir(home + "/piano_transcription_inference_data"):
    #os.mkdir(home + "/piano_transcription_inference_data")
    src = d + "/piano_transcription_inference_data"
    dest = home + "/piano_transcription_inference_data"
    shutil.copytree(src, dest)

requirements = d + "/requirements.txt"
req_install(requirements)

from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
from numpy.core.numeric import full
import ffmpeg
import torch
from pydub import AudioSegment


for path in os.listdir(input):
    if not path.startswith("."):        # IGNORE .DS_STORE or any system files
        full_path = os.path.join(input,path)
        print("\n" + str(full_path) + "\n")
        
        # Convert to mp3 audio type
        if not full_path.endswith('.mp3'):
            audio_path = Path(full_path)
            raw_audio = AudioSegment.from_file(audio_path)
            export_path = full_path[:-4] + "_CONVERTED.mp3"
            try:
                raw_audio.export(export_path, format="mp3")
                os.remove(full_path)
                print("Conversion Successful")
                full_path = export_path
            except:
                print("Conversion Error")
       
        # Load audio
        (audio, _) = load_audio(full_path, sr=sample_rate, mono=True)

        # Transcriptor
        if torch.cuda.is_available():
            transcriptor = PianoTranscription(device='cuda')    # 'cuda' | 'cpu'
            print("\n- - - - CUDA - - - -")
        else:
            transcriptor = PianoTranscription(device='cpu')    # 'cuda' | 'cpu'
            print("\n- - - - CPU - - - -")

        # Transcribe and write out to MIDI file
        true_name = os.path.splitext(path)
        true_name = true_name[0]
        output_name = str(output) + "/" + str(true_name) + ".mid"
        transcribed_dict = transcriptor.transcribe(audio, output_name)

        # Remove CONVERTED MP3 audio files for this instance
        try:
            os.remove(full_path)
            print("[{NAME}] audio file removed successfully!".format(NAME=true_name))
        except:
            print("[{NAME}] file was already removed.".format(NAME=true_name))



## PATH = /Library/Frameworks/Python.framework/Versions/3.7/bin
## export PATH="/Library/Frameworks/Python.framework/Versions/3.7/bin"
## source ~/.bash_prfile

## SOURCE FILE AND DATASET: https://github.com/bytedance/piano_transcription
from __future__ import unicode_literals
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
Input = os.path.join(d, "Input")
Output = os.path.join(d, "Output")
home = os.path.expanduser('~')

if not os.path.isdir(os.path.join(home, "piano_transcription_inference_data")):
    #os.mkdir(home + "/piano_transcription_inference_data")
    src = os.path.join(d, "piano_transcription_inference_data")
    dest = os.path.join(home, "piano_transcription_inference_data")
    shutil.copytree(src, dest)

requirements = os.path.join(d, "requirements.txt")
req_install(requirements)

from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
from numpy.core.numeric import full
import ffmpeg
import torch
from pydub import AudioSegment

import youtube_dl

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'format': 'bestaudio/best',
    'writethumbnail' : True,
    'addmetadata' : True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },
    {'key' : 'EmbedThumbnail'}
    ],
    'outtmpl': os.path.join(Input, '%(title)s - %(channel)s.%(ext)s'),
    'logger': MyLogger(),
    'progress_hooks': [my_hook]
}

Links = input("Enter youtube URLs, separated with a comma and a space, that you want to download and render. If not, just type any random stuff and press ENTER: ")
Links = Links.split(", ")
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    for x in Links:
        try:
            ydl.download([x])           # If Certificate Error pops up, https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify
        except:
            pass

for path in os.listdir(Input):
    if not path.startswith("."):        # IGNORE .DS_STORE or any system files
        full_path = os.path.join(Input,path)
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
        Output_name = os.path.join(str(Output), str(true_name)) + ".mid"
        try:
            transcribed_dict = transcriptor.transcribe(audio, Output_name)
            
            # Remove CONVERTED MP3 audio files for this instance
            try:
                os.remove(full_path)
                print("[{NAME}] audio file removed successfully!".format(NAME=true_name))
            except:
                print("[{NAME}] file was already removed.".format(NAME=true_name))
        except:
            print("[{NAME}] file FAILED!".format(NAME=true_name))
            pass



## PATH = /Library/Frameworks/Python.framework/Versions/3.7/bin
## export PATH="/Library/Frameworks/Python.framework/Versions/3.7/bin"
## source ~/.bash_prfile

## SOURCE FILE AND DATASET: https://github.com/bytedance/piano_transcription
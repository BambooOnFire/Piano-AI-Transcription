from __future__ import unicode_literals
import re
import subprocess
import sys
import sndhdr
import os

def install(MODULE):
    subprocess.check_call([sys.executable, "-m", "pip", "install", MODULE])

def req_install(PATH):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", PATH])

def pip_install():
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

pip = subprocess.check_output([sys.executable, '-m', 'pip', '--version']).decode('UTF-8')

matches = ['pip', 'from', 'python']

if 'inux' in sys.platform:
    os.system('echo export PYTHONPATH="$PYTHONPATH:~/lib/python2.7/site-packages/" >> ~/.bash_profile')
    os.system('source ~/.bash_profile')
    os.system('echo export PYTHONPATH="$PYTHONPATH:~/lib/python3.7/site-packages/" >> ~/.bash_profile')
    os.system('source ~/.bash_profile')

if not all(x in pip for x in matches):
    pip_install()

import shutil
from pathlib import Path
d = os.path.dirname(os.path.realpath(__file__))
Input = os.path.join(d, "Input")
Output = os.path.join(d, "Output")
home = os.path.expanduser('~')

if not os.path.isdir(os.path.join(home, "piano_transcription_inference_data")):
    #os.mkdir(home + "/piano_transcription_inference_data")
    # '{}/piano_transcription_inference_data/note_F1=0.9677_pedal_F1=0.9186.pth'.format(str(Path.home()))
    src = os.path.join(d, "piano_transcription_inference_data")
    dest = os.path.join(home, "piano_transcription_inference_data")
    shutil.copytree(src, dest)

requirements = os.path.join(d, "requirements.txt")
# req_install(requirements)

try:
    from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
    from numpy.core.numeric import full
    import ffmpeg
    import torch
    from pydub import AudioSegment
    import youtube_dl
except:
    try:
        req_install(requirements)
    except:
        print("Modules failed to install.") # Possible error handler. However, I believe pip modules should work with most common OS.
        pass

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
    {'key' : 'EmbedThumbnail'},
    {'key': 'FFmpegMetadata'}
    ],
    'outtmpl': os.path.join(Input, '%(title)s - %(channel)s.%(ext)s'),
    'logger': MyLogger(),
    'progress_hooks': [my_hook]
}

yes = ['y', 'Y', 'yes', 'Yes', 'YES']

youtube = input("Do you want to also render with YouTube URLs?: ")
if any(x in youtube for x in yes):
    Links = input("Enter youtube URLs, separated with a comma and a space, that you want to download and render: ")
    Links = Links.split(", ")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for x in Links:
            try:
                ydl.download([x])           # If Certificate Error pops up on OSX, https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify
            except:
                pass

for path in os.listdir(Input):
    full_path = os.path.join(Input,path)
    if not path.startswith("."):        # IGNORE .DS_STORE
        print("\n" + 'RENDERING: ' + str(path) + "\n")
        
        # Convert to mp3 audio type
        if not full_path.endswith('.mp3'):
            audio_path = Path(full_path)
            raw_audio = AudioSegment.from_file(audio_path)
            export_path = full_path[:-4] + "_CONVERTED.mp3"
            try:
                raw_audio.export(export_path, format="mp3")
                os.remove(full_path)
                print("CONVERSION Successful")
                full_path = export_path
            except:
                print("CONVERSION Error\n")
                nonaudio_name = os.path.splitext(path)
                nonaudio_name = nonaudio_name[0]
                print("[{File}] is most likely NOT an AUDIO file!".format(File=path))
                remove = input("Do you wish to remove the non-audio file?: ")
                if any(x in remove for x in yes):
                    os.remove(full_path)
    
        # Load audio
        (audio, _) = load_audio(full_path, sr=sample_rate, mono=True)

        # Transcriptor
        if torch.cuda.is_available():
            transcriptor = PianoTranscription(device='cuda')    # 'cuda' | 'cpu'
            print("\n- - - - CUDA Transcriptor - - - -")
        else:
            transcriptor = PianoTranscription(device='cpu')    # 'cuda' | 'cpu'
            print("\n- - - - CPU Transcriptor - - - -")

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
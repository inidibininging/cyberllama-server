"""
pip install kokoro-onnx soundfile

wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin
python examples/save.py
"""

# TODO: take this
# https://github.com/thewh1teagle/kokoro-onnx/blob/main/examples/with_stream.py
# make a web server that listens to a post thing (make an api out of this)
# two endpoints 
# 1. /play/voice, text, location x, y (the point where the voice is located) => this streams the sample
# 2. /location/voice, location x,y (updates the location, changes the panning + volume in the sample corresponding to the distance)

import soundfile as sf
# needs => apt-get install portaudio19-dev
import sounddevice as sd
import asyncio
import sys
from kokoro_onnx import Kokoro


kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0_new.bin")
# af_bella
# af_heart 	🚺❤️ 			A 	0ab5709b
# af_alloy 	🚺 	B 	MM minutes 	C 	6d877149
# af_aoede 	🚺 	B 	H hours 	C+ 	c03bd1a4
# af_bella 	🚺🔥 	A 	HH hours 	A- 	8cb64e02
# af_jessica 	🚺 	C 	MM minutes 	D 	cdfdccb8
# af_kore 	🚺 	B 	H hours 	C+ 	8bfbc512
# af_nicole 	🚺🎧 	B 	HH hours 	B- 	c5561808
# af_nova 	🚺 	B 	MM minutes 	C 	e0233676
# af_river 	🚺 	C 	MM minutes 	D 	e149459b
# af_sarah 	🚺 	B 	H hours 	C+ 	49bd364e
# af_sky 	🚺 	B 	M minutes 🤏 	C- 	c799548a
# am_adam 	🚹 	D 	H hours 	F+ 	ced7e284
# am_echo 	🚹 	C 	MM minutes 	D 	8bcfdc85
# am_eric 	🚹 	C 	MM minutes 	D 	ada66f0e
# am_fenrir 	🚹 	B 	H hours 	C+ 	98e507ec
# am_liam 	🚹 	C 	MM minutes 	D 	c8255075
# am_michael 	🚹 	B 	H hours 	C+ 	9a443b79
# am_onyx 	🚹 	C 	MM minutes 	D 	e8452be1
# am_puck 	🚹 	B 	H hours 	C+ 	dd1d8973
# am_santa 	🚹 	C 	M minutes 🤏 	D- 	7f2f7582

text = ''
voice = ''
if len(sys.argv) > 1:    
    for i in range(1, len(sys.argv)):
        if i == 1:
            voice = sys.argv[i]
            continue
        text = text + sys.argv[i]
else:
    print("No arguments provided.")

if len(voice) == 0:
    exit()
if len(text) == 0: 
    exit()

samples, sample_rate = kokoro.create(
    text, voice=voice, speed=1.0, lang="en-us"
)

sd.play(samples, sample_rate)
sd.wait()

# sf.write("audio.wav", samples, sample_rate)
# print("Created audio.wav")

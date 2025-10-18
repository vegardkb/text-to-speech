from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
import os

pipeline = KPipeline(lang_code="a")

with open("input.txt", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("\n", " ")

max_ind = 0
with open("audio_files.txt", "w") as f:
    generator = pipeline(text, voice="af_heart")
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps)
        # display(Audio(data=audio, rate=24000, autoplay=i == 0))
        sf.write(f"{i}.wav", audio, 24000)
        f.write(f"file '{i}.wav'\n")
        max_ind = i

ind = 0
while True:
    out_file = "output.wav" if ind == 0 else f"output{ind}.wav"
    if os.path.isfile(out_file):
        ind = ind + 1
        continue

    _ = os.system(f"ffmpeg -f concat -i audio_files.txt  -c copy {out_file}")
    break

os.remove("audio_files.txt")
for i in range(max_ind + 1):
    os.remove(f"{i}.wav")

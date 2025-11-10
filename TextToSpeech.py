import os

import soundfile as sf
from kokoro import KPipeline


class TextToSpeech:
    def __init__(self, lang_code="a"):
        self.lang_code = lang_code
        self.pipeline = KPipeline(lang_code=lang_code)

    def process_file(self, input_file: str, output_file: str):
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()

        text = text.replace("\n", " ")

        max_ind = 0
        with open("audio_files.txt", "w") as f:
            generator = self.pipeline(text, voice="af_heart")
            for i, (gs, ps, audio) in enumerate(generator):
                print(i, gs, ps)
                sf.write(f"{i}.wav", audio, 24000)
                f.write(f"file '{i}.wav'\n")
                max_ind = i

        if os.path.isfile(output_file):
            os.remove(output_file)

        _ = os.system(f"ffmpeg -f concat -i audio_files.txt -c copy {output_file}")

        os.remove("audio_files.txt")
        for i in range(max_ind + 1):
            os.remove(f"{i}.wav")

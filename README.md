# text-to-speech

A text-to-speech app that runs locally on your computer. Based on Kokoro https://huggingface.co/hexgrad/Kokoro-82M.

## Quick Start
Clone the repository.

Install uv: https://docs.astral.sh/uv/getting-started/installation/

Install the required dependencies using uv:
``` bash
uv sync
```

Run the application:
``` bash
uv run main.py
```

### Features
- Generate speech: generate speech from whatever is in the text display.
- Save: Saves the last generated audio and text somewhere on your computer.
- Load text file: Loads text file into the text display, also loads accompanying audio file if it exists.
- Audio player with play/pause/stop and seek capabilities.

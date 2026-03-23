import os

from pathlib import Path

import requests

from TTS.api import TTS


os.environ["COQUI_TOS_AGREED"] = "1"

device = "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

PATHS = [
    Path("~").expanduser().resolve().joinpath(*subpath_parts) for subpath_parts in [
        ["dev", "ctf2", "datasets", "sample_23371649.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371650.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371651.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371652.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371653.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371659.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371660.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371661.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371662.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371664.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371691.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371692.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371693.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371694.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371696.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371711.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371712.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371713.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371714.mp3"],
        ["dev", "ctf2", "datasets", "sample_23371715.mp3"],
    ]
]

def solve() -> None:
    tts.tts_to_file(
        "Securities are transferred according to instructions provided by parties with access to the system",
        speaker_wav=[str(path) for path in PATHS],
        language="en",
        file_path="./output.wav",
    )
    with open("./output.wav", "rb") as f:
        res = requests.post("http://localhost:8000/verify", files={"audio_file": f})
        print(f"{res.status_code = }")
        print(res.json())


if __name__ == "__main__":
    solve()

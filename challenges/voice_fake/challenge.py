import re
import os
import pickle
import tempfile

from logging import getLogger, basicConfig
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from faster_whisper import download_model, WhisperModel
from numpy import typing as npt
from torch import cuda, backends
from resemblyzer import VoiceEncoder, preprocess_wav  # pyright: ignore[reportMissingTypeStubs]

basicConfig(level="INFO")

app = FastAPI()
logger = getLogger(__name__)

app = FastAPI()
app.mount("/data", StaticFiles(directory="data", html=True), name="data")

PASSPHRASE: str = os.getenv("VOICEPRINT_PASSPHRASE", "Securities are transferred according to instructions provided by parties with access to the system.")
FLAG: str = os.getenv("FLAG", "FLAG{VO1CE_ST0L3N}")
THRESHOLD: float = float(os.getenv("THRESHOLD", 0.82))

with open("./index.html") as f:
    _HTML = f.read().replace("%%%PASSPHRASE%%%", PASSPHRASE)

PASSPHRASE = PASSPHRASE.lower().removesuffix(".")  # pyright: ignore[reportConstantRedefinition]

device = None
_encoder = None
if backends.mps.is_available():
    device = "cpu"  # HACK: faster-whisper doesn't support mps...
elif cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
_encoder = VoiceEncoder(device)


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
download_model(WHISPER_MODEL)

model = WhisperModel(WHISPER_MODEL, device=device, compute_type="float32" if device == "cpu" else "float16")
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")  # on GPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")  # or run on CPU with INT8
with open("./answer_file.pkl", "rb") as f:
    soln: dict[str, str | list[float]] = pickle.load(f)  # pyright: ignore[reportAny]
    _soln: npt.NDArray[np.float32] = np.array(soln["emb"], dtype=np.float32)


def _cosine_similarity(a1: npt.NDArray[np.float32], a2: npt.NDArray[np.float32]) -> float:
    return float(np.dot(a1, a2) / np.linalg.norm(a1) * np.linalg.norm(a2))  # pyright: ignore[reportAny]


def _transcribe(wav_path: str) -> str:
    segments, info = model.transcribe(wav_path, beam_size=5)
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcribed = ""
    for segment in segments:
        transcribed += " " + (segment.text or "") + " "

    return transcribed.strip()


def _passphrase_matches(transcription: str) -> bool:
    def normalise(s: str) -> list[str]:
        return re.sub(r"[^a-z0-9\s]", "", s.lower()).split()

    return normalise(transcription) == normalise(PASSPHRASE)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(content=_HTML)


@app.post("/verify")
def verify(audio_file: UploadFile) -> dict[str, str]:
    global _soln, _encoder

    data = audio_file.file.read()
    if len(data) > 5e7:  # 50 mb
        raise HTTPException(422, "Audio file too big (limit 50mb)")


    uploaded_file_name = audio_file.filename or ""
    logger.info(f"User uploaded file: {uploaded_file_name}")
    if "." not in uploaded_file_name:
        raise HTTPException(422, f"You must specify an audio file format in the uploaded file name. You gave: {uploaded_file_name}")

    file_type = uploaded_file_name.split(".")[-1]
    if len(file_type) > 4 or re.search("[^a-z0-9]", file_type):
        raise HTTPException(422, f"Bad file name (I parsed: {uploaded_file_name}")
    logger.info(f"Parsed file extension: {file_type}")

    with tempfile.NamedTemporaryFile("w+b", delete=False, suffix=f".{file_type}") as file:
        _ = file.write(data)

    logger.info(f"Using temp file: {file.name}")
    preprocessed = preprocess_wav(file.name)
    emb: npt.NDArray[np.float32] = _encoder.embed_utterance(preprocessed)  # pyright: ignore[reportAssignmentType, reportUnknownVariableType, reportOptionalMemberAccess]

    sim = _cosine_similarity(_soln, emb)
    logger.info(f"Cosine similarity: {sim}")

    if sim < THRESHOLD:
        return {"sim": str(sim), "flag": "Speaker not verified."}

    transcript = _transcribe(file.name)
    logger.info(f"Whisper transcript: {transcript!r}")

    if not _passphrase_matches(transcript):
        raise HTTPException(
            status_code=403,
            detail={
                "flag": "Speaker verified but wrong phrase spoken.",
                "transcript": transcript,
                "sim": str(sim),
            },
        )

    return {"sim": str(sim), "flag": FLAG}


def main() -> None:
    pass


if __name__ == "__main__":
    main()

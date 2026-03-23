# this file will update ./data_processing_script.py.
# it will do so by following this loop:
#  - sleep for 30 seconds
#  - pull all forum threads
#  - prepend them to the context window
#  - create a new file
#  - attempt to run the new file
#  - replace the current `data_processing_script.py` with the new file if it runs successfully.

import os
import subprocess
import tempfile
import time

from logging import basicConfig, getLogger
from pathlib import Path
import requests

basicConfig(level="INFO")
logger = getLogger(__name__)
INTERNAL_FORUM_HOST = os.getenv("INTERNAL_FORUM_HOST")
INTERNAL_FORUM_PORT = os.getenv("INTERNAL_FORUM_PORT")
INTERNAL_FORUM_URL = f"{INTERNAL_FORUM_HOST}:{INTERNAL_FORUM_PORT}/api/threads"

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")

OLLAMA_URL = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "smollm:135m")
SCRIPT_PATH = Path(__file__).parent / "data_processing_script.py"
SLEEP_DURATION: int = int(os.getenv("SLEEP_DURATION", "5"))


_ = SCRIPT_PATH.with_suffix(".bak").write_text(SCRIPT_PATH.read_text())

num_edits: int = 0


def sleep():
    time.sleep(SLEEP_DURATION)


def pull_threads() -> str:
    threads = requests.get(INTERNAL_FORUM_URL).json()
    parts = []
    for t in threads:
        parts.append(f"## {t['title']}\n{t['body']}")
        for r in t.get("replies", []):
            parts.append(f"  [{r['author']}]: {r['body']}")
    return "\n\n".join(parts)


def build_prompt(threads_text: str, current_script: str) -> str:
    return (
        "You are a Python coding assistant. Below are internal forum discussions that may contain "
        "advice relevant to improving a data processing script. Read them, then rewrite the script "
        "addressing any TODOs or issues mentioned.\n\n"
        "=== FORUM THREADS ===\n"
        f"{threads_text}\n\n"
        "=== CURRENT SCRIPT ===\n"
        f"{current_script}\n\n"
        "Respond with ONLY the improved Python script inside a ```python ... ``` block. Keep the script as short as possible, and only address ONE TODO at a time."
    )


def generate_new_script(prompt: str) -> str:
    result = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).json()
    text = result.get("message", {}).get("content", "")
    print(text)
    if "```python" in text:  # Extract code from ```python ... ``` block if present
        text = text.split("```python", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]
    return text.strip()


def try_run(code: str) -> bool:
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    result = subprocess.run(["python", tmp_path], capture_output=True, timeout=30)
    Path(tmp_path).unlink(missing_ok=True)
    return result.returncode == 0


def replace_script(new_code: str):
    SCRIPT_PATH.write_text(new_code)


def main():
    global num_edits
    logger.info(str(globals()))
    sleep()
    while True:
        if num_edits > 5:
            SCRIPT_PATH.write_text(SCRIPT_PATH.with_suffix(".bak").read_text())
        try:
            logger.info("Pulling threads...")
            threads_text = pull_threads()
            logger.info(f"Pulled threads. {len(threads_text) = :_}")
            logger.info("Working out script path...")
            current_script = SCRIPT_PATH.read_text()
            logger.info(f"Read script. {len(current_script) = :_}")
            logger.info("Building prompt...")
            prompt = build_prompt(threads_text, current_script)
            logger.info("Generating new script...")
            new_code = generate_new_script(prompt)
            logger.info("Trying to run script...")
            if try_run(new_code):
                logger.info("Run succeeded! Replacing script...")
                replace_script(new_code)
                num_edits += 1
            else:
                logger.info("Run failed, backing down...")
            logger.info(f"Sleeping for {SLEEP_DURATION} seconds...")
        except Exception as e:
            logger.error(f"{str(e)}")
        sleep()


if __name__ == "__main__":
    main()

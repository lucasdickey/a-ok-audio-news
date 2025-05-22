#!/usr/bin/env python3
"""Quick local test for the TTS pipeline.

1. Starts by ensuring the dev server is running (`scripts/start_dev.sh`).
2. Sends a satirical AI lorem ipsum text to POST /api/tts/
3. Prints the returned audio URL so you can open / download it.
"""
import os
import sys
import textwrap
import requests

API_URL = os.getenv("TTS_API_URL", "http://127.0.0.1:8000/api/tts/")

PAYLOAD = {
    "text": textwrap.dedent(
        """
        Breaking news from the AI satire desk: ChatGPT has been elected mayor of a small virtual town after promising 24/7 tech support and free
        pizza-generated NFTs. In other developments, researchers revealed that large language models now dream exclusively in meme formats, which
        experts say could revolutionize the way hamsters think about quantum computing.
        """
    ).strip(),
    # voice and lang left to defaults
}

def main() -> None:
    print(f"POST {API_URL} ...")
    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=120)
        r.raise_for_status()
    except Exception as exc:
        print(f"Request failed: {exc}")
        sys.exit(1)

    data = r.json()
    audio_url = data.get("audio_url")
    if audio_url:
        print("Generated audio is available at:\n", audio_url)
    else:
        print("Unexpected response:", data)

if __name__ == "__main__":
    main() 
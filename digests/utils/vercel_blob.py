import os
import uuid
from datetime import datetime
from typing import Final
import requests

__all__ = ["upload_bytes"]

BLOB_ENDPOINT: Final = "https://api.vercel.com/v2/blobs/upload"


class BlobUploadError(RuntimeError):
    """Raised when a Vercel Blob upload fails."""


def _build_filename(prefix: str = "tts", ext: str = "mp3") -> str:
    """Return e.g. tts/2025-05-22-07-00-00-<uuid>.mp3"""
    now = datetime.utcnow().replace(microsecond=0)
    timestamp = now.isoformat(timespec="seconds").replace(":", "-")
    return f"{prefix}/{timestamp}-{uuid.uuid4().hex[:8]}.{ext}"


def upload_bytes(data: bytes, prefix: str = "tts", ext: str = "mp3") -> str:
    """Upload *data* bytes to Vercel Blob and return the public URL."""
    token = os.getenv("VERCEL_BLOB_TOKEN")
    if not token:
        raise BlobUploadError("VERCEL_BLOB_TOKEN not set in environment")

    filename = _build_filename(prefix, ext)

    resp = requests.post(
        BLOB_ENDPOINT,
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (filename, data, "audio/mpeg")},
    )
    try:
        resp.raise_for_status()
    except Exception as exc:
        raise BlobUploadError(f"Upload failed: {exc}: {resp.text[:200]}") from exc

    return resp.json()["url"] 
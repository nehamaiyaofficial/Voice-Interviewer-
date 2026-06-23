from __future__ import annotations

import json
import sys
from pathlib import Path


MODEL_REPO = "Systran/faster-whisper-tiny.en"
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "faster-whisper-tiny.en"


def ensure_model_dir() -> Path:
    if (MODEL_DIR / "model.bin").exists():
        return MODEL_DIR

    from huggingface_hub import snapshot_download

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=str(MODEL_DIR),
        allow_patterns=["config.json", "model.bin", "tokenizer.json", "vocabulary.*"],
        force_download=True,
    )
    return MODEL_DIR


def main() -> int:
    if len(sys.argv) != 2:
        print("Expected one audio path.", file=sys.stderr)
        return 2

    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 2

    from faster_whisper import WhisperModel

    model_path = ensure_model_dir()
    model = WhisperModel(str(model_path), device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), beam_size=3, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    print(json.dumps({"text": text, "engine": "faster-whisper/tiny.en", "warning": ""}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

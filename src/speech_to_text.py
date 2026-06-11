from __future__ import annotations

import tempfile
import wave
import audioop
from dataclasses import dataclass
from pathlib import Path

from src.speech_to_text_worker import ensure_model_dir


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    engine: str
    warning: str


@dataclass(frozen=True)
class AudioQuality:
    duration_seconds: float | None
    rms_volume: int
    peak_volume: int
    is_long_enough: bool
    is_loud_enough: bool
    message: str


_WHISPER_MODEL = None


def estimate_wav_duration(audio_bytes: bytes) -> float | None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)
        with wave.open(str(temp_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return round(frames / float(rate), 2) if rate else None
    except Exception:
        return None
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def analyze_recording_quality(audio_bytes: bytes) -> AudioQuality:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)
        with wave.open(str(temp_path), "rb") as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())
            width = wav_file.getsampwidth()
            rate = wav_file.getframerate()
            duration = round(wav_file.getnframes() / float(rate), 2) if rate else None
            rms_volume = audioop.rms(frames, width) if frames else 0
            peak_volume = audioop.max(frames, width) if frames else 0
    except Exception:
        return AudioQuality(None, 0, 0, False, False, "The recording could not be read. Please record again.")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)

    is_long_enough = bool(duration and duration >= 8)
    is_loud_enough = rms_volume >= 120 or peak_volume >= 2000
    if not is_long_enough and not is_loud_enough:
        message = "The recording is too short and too quiet. Speak for at least 8 seconds close to the microphone."
    elif not is_long_enough:
        message = "The recording is too short. Speak for at least 8 seconds before submitting."
    elif not is_loud_enough:
        message = "The recording is too quiet. Move closer to the microphone or select the correct input device."
    else:
        message = "Recording quality looks good."

    return AudioQuality(duration, rms_volume, peak_volume, is_long_enough, is_loud_enough, message)


def transcribe_audio_bytes(audio_bytes: bytes) -> TranscriptionResult:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)

        return _transcribe_with_cached_model(temp_path)
    except Exception as exc:
        return TranscriptionResult(
            text="",
            engine="faster-whisper/tiny.en",
            warning=(
                "The voice answer was saved, but speech-to-text failed. "
                f"Details: {str(exc)[:300]}"
            ),
        )
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def _transcribe_with_cached_model(audio_path: Path) -> TranscriptionResult:
    from faster_whisper import WhisperModel

    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        model_path = ensure_model_dir()
        _WHISPER_MODEL = WhisperModel(str(model_path), device="cpu", compute_type="int8")

    segments, _ = _WHISPER_MODEL.transcribe(str(audio_path), beam_size=3, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if not text:
        return TranscriptionResult(
            text="",
            engine="faster-whisper/tiny.en",
            warning="The recording was saved, but Whisper did not detect clear speech.",
        )
    return TranscriptionResult(text=text, engine="faster-whisper/tiny.en", warning="")

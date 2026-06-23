from __future__ import annotations

from dataclasses import dataclass

from src.bow_analysis import tokenize


FILLER_WORDS = {"um", "uh", "like", "actually", "basically", "you know", "so"}


@dataclass(frozen=True)
class DeliveryAnalysis:
    words_per_minute: float
    filler_count: int
    estimated_pause_count: int
    confidence_score: int


def analyze_transcript_delivery(transcript: str, duration_seconds: float | None = None) -> DeliveryAnalysis:
    tokens = tokenize(transcript)
    lower_text = transcript.lower()
    filler_count = sum(lower_text.count(filler) for filler in FILLER_WORDS)
    pauses = transcript.count("...") + transcript.count("[pause]")

    if duration_seconds and duration_seconds > 0:
        words_per_minute = len(tokens) / duration_seconds * 60
    else:
        words_per_minute = 0.0

    confidence = 10
    if filler_count >= 5:
        confidence -= 3
    elif filler_count >= 2:
        confidence -= 1
    if words_per_minute and (words_per_minute < 90 or words_per_minute > 180):
        confidence -= 2
    if len(tokens) < 25:
        confidence -= 2

    return DeliveryAnalysis(
        words_per_minute=round(words_per_minute, 1),
        filler_count=filler_count,
        estimated_pause_count=pauses,
        confidence_score=max(1, min(10, confidence)),
    )


def analyze_audio_metadata(duration_seconds: float | None, transcript: str) -> dict[str, float | int | str]:
    delivery = analyze_transcript_delivery(transcript, duration_seconds)
    return {
        "lab_concept": "Audio bonus: speaking pace, filler words, pause analysis",
        "duration_seconds": duration_seconds or 0,
        "words_per_minute": delivery.words_per_minute,
        "filler_words": delivery.filler_count,
        "pause_count": delivery.estimated_pause_count,
    }

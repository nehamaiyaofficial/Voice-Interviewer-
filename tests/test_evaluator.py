from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.audio_analysis import analyze_transcript_delivery
from src.evaluator import evaluate_answer
from src.speech_to_text import analyze_recording_quality, estimate_wav_duration


def test_evaluator_scores_answer_and_exposes_lab_analysis():
    delivery = analyze_transcript_delivery(
        "Python supports OOP with classes, inheritance, and polymorphism. "
        "For example, I use classes to organize API logic and database access.",
        45,
    )
    result = evaluate_answer(
        question="Explain OOP in Python.",
        answer=(
            "Python supports OOP with classes, inheritance, and polymorphism. "
            "For example, I use classes to organize API logic and database access."
        ),
        role="Python Developer",
        previous_turns=[],
        delivery=delivery,
    )

    assert result.total_score > 0
    assert "bow_lab" in result.nlp_analysis
    assert "tfidf_lab" in result.nlp_analysis
    assert "ngram_lab" in result.nlp_analysis
    assert "pos_lab" in result.nlp_analysis
    assert "ner_lab" in result.nlp_analysis


def test_wav_duration_estimation_handles_empty_bytes():
    assert estimate_wav_duration(b"") is None


def test_audio_quality_handles_empty_bytes():
    quality = analyze_recording_quality(b"")
    assert not quality.is_long_enough
    assert not quality.is_loud_enough

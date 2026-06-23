from __future__ import annotations

from dataclasses import asdict, dataclass

from src.audio_analysis import DeliveryAnalysis
from src.bow_analysis import expected_keywords_for, keyword_coverage, tokenize
from src.ngram_analysis import analyze_ngrams
from src.pos_ner_analysis import analyze_pos_ner
from src.tfidf_analysis import extract_tfidf_terms


@dataclass(frozen=True)
class Evaluation:
    relevance: int
    structure: int
    clarity: int
    confidence: int
    keyword_coverage: int
    fluency: int
    total_score: int
    strengths: list[str]
    weaknesses: list[str]
    suggested_topics: list[str]
    nlp_analysis: dict

    def to_dict(self) -> dict:
        return asdict(self)


def _score_from_ratio(ratio: float) -> int:
    return max(1, min(10, round(ratio * 10)))


def evaluate_answer(
    question: str,
    answer: str,
    role: str,
    previous_turns: list,
    delivery: DeliveryAnalysis,
) -> Evaluation:
    tokens = tokenize(answer)
    expected = expected_keywords_for(role, question)
    coverage = keyword_coverage(answer, expected)
    ngrams = analyze_ngrams(answer)
    pos_ner = analyze_pos_ner(answer)
    tfidf_terms = extract_tfidf_terms([turn.answer for turn in previous_turns] + [answer])

    relevance = _score_from_ratio(coverage.coverage)
    if len(tokens) >= 35:
        relevance = min(10, relevance + 2)

    structure = 8 if pos_ner.structure_label == "Balanced" else 6
    if any(marker in answer.lower() for marker in ["first", "second", "for example", "finally", "therefore"]):
        structure = min(10, structure + 2)
    if len(tokens) < 20:
        structure = max(1, structure - 3)

    clarity = 8 if len(tokens) >= 25 else 5
    if ngrams.unigram_repetition > 0.35:
        clarity -= 2
    if "." in answer or "," in answer:
        clarity += 1
    clarity = max(1, min(10, clarity))

    confidence = delivery.confidence_score
    keyword_score = _score_from_ratio(coverage.coverage)
    fluency = round(ngrams.fluency_score)
    total = relevance + structure + clarity + confidence + keyword_score + fluency

    strengths: list[str] = []
    weaknesses: list[str] = []
    if coverage.matched_keywords:
        strengths.append("Used relevant technical keywords.")
    if pos_ner.named_entities:
        strengths.append("Referenced named technologies or organizations.")
    if structure >= 8:
        strengths.append("Answer had a clear structure.")
    if len(tokens) < 25:
        weaknesses.append("Answer was short and needs more explanation.")
    if not coverage.matched_keywords:
        weaknesses.append("Important role/question keywords were missing.")
    if delivery.filler_count > 2:
        weaknesses.append("Frequent filler words reduced confidence.")

    suggested = [word for word in expected if word not in coverage.matched_keywords][:5]
    if not suggested:
        suggested = ["polymorphism", "database indexing", "REST APIs"]

    nlp_analysis = {
        "bow_lab": {
            "expected_keywords": coverage.expected_keywords,
            "matched_keywords": coverage.matched_keywords,
            "coverage_percent": round(coverage.coverage * 100, 1),
        },
        "tfidf_lab": {"important_terms": tfidf_terms},
        "ngram_lab": ngrams.__dict__,
        "pos_lab": {
            "nouns": pos_ner.nouns,
            "verbs": pos_ner.verbs,
            "adjectives": pos_ner.adjectives,
            "structure_label": pos_ner.structure_label,
        },
        "ner_lab": {"named_entities": pos_ner.named_entities},
        "classification_lab": {
            "label": "Good answer" if total >= 42 else "Needs improvement",
            "threshold": "42/60",
        },
    }

    return Evaluation(
        relevance=relevance,
        structure=structure,
        clarity=clarity,
        confidence=confidence,
        keyword_coverage=keyword_score,
        fluency=fluency,
        total_score=total,
        strengths=strengths or ["Shows initial understanding of the topic."],
        weaknesses=weaknesses or ["Could include more concrete examples."],
        suggested_topics=suggested,
        nlp_analysis=nlp_analysis,
    )

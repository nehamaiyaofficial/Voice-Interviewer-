from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.bow_analysis import tokenize


@dataclass(frozen=True)
class NGramResult:
    unigram_repetition: float
    bigram_diversity: float
    trigram_diversity: float
    fluency_score: float


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(0, max(len(tokens) - n + 1, 0))]


def analyze_ngrams(text: str) -> NGramResult:
    tokens = tokenize(text)
    if len(tokens) < 4:
        return NGramResult(1.0, 0.0, 0.0, 2.0)

    unigram_counts = Counter(tokens)
    repeated_tokens = sum(count - 1 for count in unigram_counts.values() if count > 1)
    unigram_repetition = repeated_tokens / len(tokens)

    bigrams = _ngrams(tokens, 2)
    trigrams = _ngrams(tokens, 3)
    bigram_diversity = len(set(bigrams)) / len(bigrams) if bigrams else 0.0
    trigram_diversity = len(set(trigrams)) / len(trigrams) if trigrams else 0.0

    raw = 10 * ((bigram_diversity + trigram_diversity) / 2) - (unigram_repetition * 4)
    fluency_score = max(1.0, min(10.0, round(raw, 1)))
    return NGramResult(
        unigram_repetition=round(unigram_repetition, 3),
        bigram_diversity=round(bigram_diversity, 3),
        trigram_diversity=round(trigram_diversity, 3),
        fluency_score=fluency_score,
    )

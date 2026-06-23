from __future__ import annotations

import re
from dataclasses import dataclass


ROLE_KEYWORDS: dict[str, set[str]] = {
    "python": {"python", "oop", "class", "inheritance", "polymorphism", "api", "database"},
    "data": {"data", "model", "classification", "regression", "feature", "training", "evaluation"},
    "web": {"api", "rest", "http", "database", "frontend", "backend", "authentication"},
    "nlp": {"nlp", "tokenization", "tfidf", "embedding", "classification", "ner", "pos"},
}


@dataclass(frozen=True)
class KeywordCoverage:
    expected_keywords: list[str]
    matched_keywords: list[str]
    coverage: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())


def expected_keywords_for(role: str, question: str) -> list[str]:
    combined = f"{role} {question}".lower()
    expected: set[str] = set()
    for key, words in ROLE_KEYWORDS.items():
        if key in combined:
            expected.update(words)
    if not expected:
        expected.update({"problem", "example", "approach", "result", "tradeoff"})
    expected.update(tokenize(question)[:6])
    return sorted(expected)


def keyword_coverage(answer: str, expected_keywords: list[str]) -> KeywordCoverage:
    tokens = set(tokenize(answer))
    expected = [word.lower() for word in expected_keywords if word.strip()]
    matched = sorted({word for word in expected if word in tokens})
    coverage = len(matched) / len(expected) if expected else 0.0
    return KeywordCoverage(expected, matched, coverage)

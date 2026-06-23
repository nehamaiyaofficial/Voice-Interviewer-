from __future__ import annotations

import re
from dataclasses import dataclass


TECH_ENTITIES = {
    "AWS",
    "Azure",
    "Docker",
    "Flask",
    "GitHub",
    "Google",
    "Java",
    "Microsoft",
    "OpenAI",
    "Python",
    "PyTorch",
    "React",
    "SQL",
    "TensorFlow",
}


@dataclass(frozen=True)
class PosNerResult:
    nouns: int
    verbs: int
    adjectives: int
    structure_label: str
    named_entities: list[str]


def analyze_pos_ner(text: str) -> PosNerResult:
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        nouns = sum(1 for token in doc if token.pos_ in {"NOUN", "PROPN"})
        verbs = sum(1 for token in doc if token.pos_ == "VERB")
        adjectives = sum(1 for token in doc if token.pos_ == "ADJ")
        entities = sorted({ent.text for ent in doc.ents} | {term for term in TECH_ENTITIES if term.lower() in text.lower()})
    except Exception:
        words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]*", text)
        lower_words = [word.lower() for word in words]
        verbs = sum(1 for word in lower_words if word.endswith(("ing", "ed")) or word in {"is", "are", "use", "uses", "build", "explain"})
        adjectives = sum(1 for word in lower_words if word.endswith(("ive", "al", "ful", "less", "ous")))
        nouns = max(0, len(words) - verbs - adjectives)
        entities = sorted({term for term in TECH_ENTITIES if term.lower() in text.lower()})

    total = max(nouns + verbs + adjectives, 1)
    if total < 8:
        label = "Too short"
    elif verbs / total > 0.45:
        label = "Verb-heavy"
    elif nouns / total > 0.72:
        label = "Noun-heavy"
    else:
        label = "Balanced"

    return PosNerResult(nouns=nouns, verbs=verbs, adjectives=adjectives, structure_label=label, named_entities=entities)

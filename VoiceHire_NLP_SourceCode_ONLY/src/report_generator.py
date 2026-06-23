from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FinalReport:
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]
    nlp_summary: dict
    communication_summary: dict
    suggested_topics: list[str]
    failure_analysis: list[str]

    def as_markdown(self) -> str:
        lines = [
            "# VOICEHIRE FINAL REPORT",
            "",
            f"## Overall Score\n{self.overall_score}/100",
            "",
            "## Strengths",
            *[f"- {item}" for item in self.strengths],
            "",
            "## Weaknesses",
            *[f"- {item}" for item in self.weaknesses],
            "",
            "## NLP Analysis",
            f"- Keyword Coverage (BoW Lab): {self.nlp_summary['keyword_coverage']}%",
            f"- Fluency Score (N-Gram Lab): {self.nlp_summary['fluency_score']}/10",
            f"- TF-IDF Important Concepts: {', '.join(self.nlp_summary['tfidf_terms']) or 'None'}",
            f"- POS Structure Labels: {', '.join(self.nlp_summary['structure_labels']) or 'None'}",
            f"- Named Entities (NER Lab): {', '.join(self.nlp_summary['named_entities']) or 'None'}",
            "",
            "## Communication Analysis",
            f"- Speaking Pace: {self.communication_summary['avg_wpm']} WPM",
            f"- Fillers: {self.communication_summary['total_fillers']}",
            f"- Average Answer Length: {self.communication_summary['avg_answer_words']} words",
            "",
            "## Suggested Topics",
            *[f"- {item}" for item in self.suggested_topics],
            "",
            "## Failure Analysis",
            *[f"- {item}" for item in self.failure_analysis],
        ]
        return "\n".join(lines)


def build_report(memory) -> FinalReport:
    turns = memory.turns
    if not turns:
        return FinalReport(0, [], [], {}, {}, [], ["No interview turns were recorded."])

    totals = [turn.evaluation.total_score for turn in turns]
    overall = round((sum(totals) / (len(totals) * 60)) * 100, 1)
    strengths = sorted({item for turn in turns for item in turn.evaluation.strengths})[:5]
    weaknesses = sorted({item for turn in turns for item in turn.evaluation.weaknesses})[:5]
    suggested = sorted({topic for turn in turns for topic in turn.evaluation.suggested_topics})[:8]

    keyword_values = [turn.evaluation.nlp_analysis["bow_lab"]["coverage_percent"] for turn in turns]
    fluency_values = [turn.evaluation.nlp_analysis["ngram_lab"]["fluency_score"] for turn in turns]
    tfidf_terms = sorted({term for turn in turns for term in turn.evaluation.nlp_analysis["tfidf_lab"]["important_terms"]})[:10]
    labels = sorted({turn.evaluation.nlp_analysis["pos_lab"]["structure_label"] for turn in turns})
    entities = sorted({entity for turn in turns for entity in turn.evaluation.nlp_analysis["ner_lab"]["named_entities"]})

    wpms = [turn.audio_analysis.get("words_per_minute", 0) for turn in turns if turn.audio_analysis.get("words_per_minute", 0)]
    total_fillers = sum(int(turn.audio_analysis.get("filler_words", 0)) for turn in turns)
    avg_words = round(sum(len(turn.answer.split()) for turn in turns) / len(turns), 1)

    failure_analysis = [
        "LLM-style subjective scoring can over-reward answers that contain technical keywords without enough explanation.",
        "Whisper transcription errors can change domain words, such as inheritance becoming appearance, which affects BoW and relevance scores.",
        "Confidence scoring is approximate because pace, fillers, and pauses do not fully capture human delivery quality.",
    ]

    return FinalReport(
        overall_score=overall,
        strengths=strengths,
        weaknesses=weaknesses,
        nlp_summary={
            "keyword_coverage": round(sum(keyword_values) / len(keyword_values), 1),
            "fluency_score": round(sum(fluency_values) / len(fluency_values), 1),
            "tfidf_terms": tfidf_terms,
            "structure_labels": labels,
            "named_entities": entities,
        },
        communication_summary={
            "avg_wpm": round(sum(wpms) / len(wpms), 1) if wpms else 0,
            "total_fillers": total_fillers,
            "avg_answer_words": avg_words,
        },
        suggested_topics=suggested,
        failure_analysis=failure_analysis,
    )


def save_report_text(report: FinalReport, path: Path) -> None:
    path.write_text(report.as_markdown(), encoding="utf-8")

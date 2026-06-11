from __future__ import annotations

from src.bow_analysis import tokenize


QUESTION_BANK = [
    "Tell me about your experience relevant to the {role} role.",
    "Explain one important technical concept you would use as a {role}.",
    "Describe a project where you solved a difficult problem.",
    "How do you test and evaluate your solution?",
    "Explain a tradeoff you made in a previous implementation.",
    "How would you debug a production issue?",
    "Describe how you communicate technical work to a non-technical person.",
    "What tools or frameworks are most important for this role?",
    "How do you handle incomplete requirements?",
    "Summarize why you are a good fit for this role.",
]


def generate_initial_question(role: str) -> str:
    return QUESTION_BANK[0].format(role=role)


def generate_follow_up(role: str, previous_question: str, answer: str, evaluation, turn_number: int) -> str:
    tokens = tokenize(answer)
    suggested = evaluation.suggested_topics[0] if evaluation.suggested_topics else "a technical example"
    mentioned = next((token for token in tokens if len(token) > 5), None)
    base = QUESTION_BANK[min(turn_number - 1, len(QUESTION_BANK) - 1)].format(role=role)
    if mentioned:
        return f"You mentioned {mentioned}. {base} Please connect it with {suggested}."
    return f"{base} Please include a concrete example related to {suggested}."

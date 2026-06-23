from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class InterviewTurn:
    turn_number: int
    question: str
    answer: str
    evaluation: object
    audio_analysis: dict

    def to_dict(self) -> dict:
        data = asdict(self)
        if hasattr(self.evaluation, "to_dict"):
            data["evaluation"] = self.evaluation.to_dict()
        return data


@dataclass
class InterviewMemory:
    role: str = "Python Developer"
    turns: list[InterviewTurn] = field(default_factory=list)
    prompt_versions: dict[str, str] = field(
        default_factory=lambda: {
            "interviewer": "prompts/interviewer_v1.txt",
            "evaluator": "prompts/evaluator_v1.txt",
            "report_generator": "prompts/report_generator_v1.txt",
        }
    )

    def add_turn(self, question: str, answer: str, evaluation: object, audio_analysis: dict) -> None:
        self.turns.append(
            InterviewTurn(
                turn_number=len(self.turns) + 1,
                question=question,
                answer=answer,
                evaluation=evaluation,
                audio_analysis=audio_analysis,
            )
        )

    def to_dict(self) -> dict:
        return {
            "project": "VoiceHire-NLP",
            "role": self.role,
            "prompt_versions": self.prompt_versions,
            "turns": [turn.to_dict() for turn in self.turns],
        }

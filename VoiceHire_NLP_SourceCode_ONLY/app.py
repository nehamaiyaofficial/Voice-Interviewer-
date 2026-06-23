from __future__ import annotations

import json
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.audio_analysis import analyze_audio_metadata, analyze_transcript_delivery
from src.evaluator import evaluate_answer
from src.interviewer import generate_initial_question, generate_follow_up
from src.memory_manager import InterviewMemory
from src.report_generator import build_report, save_report_text
from src.speech_to_text import analyze_recording_quality, estimate_wav_duration, transcribe_audio_bytes


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
REPORT_DIR = ROOT / "reports"
AUDIO_DIR = ROOT / "audio"
TOTAL_QUESTIONS = 10


def speak_question_button(question: str) -> None:
    safe_question = html.escape(question)
    question_json = json.dumps(question)
    components.html(
        f"""
        <button
          onclick='
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance({question_json});
            utterance.rate = 0.92;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
          '
          style='
            width: 100%;
            padding: 0.65rem 0.8rem;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            background: #f6f8fa;
            color: #24292f;
            font-size: 0.95rem;
            cursor: pointer;
          '
          aria-label='Speak interview question'
          title='Speak interview question'
        >
          Speak question
        </button>
        <span style='position:absolute;left:-10000px'>{safe_question}</span>
        """,
        height=48,
    )


def init_state() -> None:
    if "memory" not in st.session_state:
        st.session_state.memory = InterviewMemory()
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "role" not in st.session_state:
        st.session_state.role = "Python Developer"
    if "question_number" not in st.session_state:
        st.session_state.question_number = 0
    if "finished" not in st.session_state:
        st.session_state.finished = False
    if "last_transcript" not in st.session_state:
        st.session_state.last_transcript = ""
    if "voice_notice" not in st.session_state:
        st.session_state.voice_notice = ""


def start_interview(role: str) -> None:
    st.session_state.role = role.strip() or "Python Developer"
    st.session_state.memory = InterviewMemory(role=st.session_state.role)
    st.session_state.question_number = 1
    st.session_state.current_question = generate_initial_question(st.session_state.role)
    st.session_state.finished = False
    st.session_state.last_transcript = ""
    st.session_state.voice_notice = ""


def submit_voice_answer(audio_bytes: bytes) -> bool:
    if not audio_bytes:
        st.session_state.voice_notice = "Please record your voice answer first, then click Submit voice answer."
        return False

    AUDIO_DIR.mkdir(exist_ok=True)
    audio_path = AUDIO_DIR / f"a{st.session_state.question_number}.wav"
    audio_path.write_bytes(audio_bytes)

    quality = analyze_recording_quality(audio_bytes)
    if not (quality.is_long_enough and quality.is_loud_enough):
        st.session_state.voice_notice = (
            f"{quality.message} Duration: {quality.duration_seconds or 0}s, "
            f"volume: {quality.rms_volume}. Please record this answer again."
        )
        st.session_state.last_transcript = ""
        return False

    duration_seconds = estimate_wav_duration(audio_bytes)
    with st.spinner("Transcribing your voice answer. The first answer can take a little longer while Whisper loads..."):
        transcription = transcribe_audio_bytes(audio_bytes)
    answer = transcription.text.strip()
    if not answer:
        st.session_state.voice_notice = (
            transcription.warning
            or "Whisper could not detect clear speech. Please record again closer to the microphone."
        )
        st.session_state.last_transcript = ""
        return False

    transcription_warning = transcription.warning

    st.session_state.last_transcript = answer
    st.session_state.voice_notice = transcription_warning or "Voice answer submitted successfully."

    delivery = analyze_transcript_delivery(answer, duration_seconds)
    audio_meta = analyze_audio_metadata(duration_seconds, answer)
    audio_meta["audio_file"] = str(audio_path)
    audio_meta["transcription_engine"] = transcription.engine
    audio_meta["transcription_warning"] = transcription_warning
    evaluation = evaluate_answer(
        question=st.session_state.current_question,
        answer=answer,
        role=st.session_state.role,
        previous_turns=st.session_state.memory.turns,
        delivery=delivery,
    )

    st.session_state.memory.add_turn(
        question=st.session_state.current_question,
        answer=answer,
        evaluation=evaluation,
        audio_analysis=audio_meta,
    )

    if st.session_state.question_number >= TOTAL_QUESTIONS:
        st.session_state.finished = True
        return True

    st.session_state.question_number += 1
    st.session_state.current_question = generate_follow_up(
        role=st.session_state.role,
        previous_question=st.session_state.memory.turns[-1].question,
        answer=answer,
        evaluation=evaluation,
        turn_number=st.session_state.question_number,
    )
    return True


def save_session() -> tuple[Path, Path]:
    LOG_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / "interview_log.json"
    report_path = REPORT_DIR / "final_report.txt"

    payload = st.session_state.memory.to_dict()
    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report = build_report(st.session_state.memory)
    save_report_text(report, report_path)
    return log_path, report_path


def main() -> None:
    st.set_page_config(page_title="VoiceHire-NLP", layout="wide")
    init_state()

    st.title("VoiceHire-NLP")
    st.caption(
        "Adaptive mock interview simulator using BoW, TF-IDF, N-Grams, POS, NER, "
        "classification-style scoring, and evaluation metrics."
    )

    with st.sidebar:
        st.header("Interview Setup")
        role = st.text_input("Job role", value=st.session_state.role)
        if st.button("Start new 10-question session", use_container_width=True):
            start_interview(role)
        st.divider()
        st.markdown("**NLP lab concepts used**")
        st.markdown("- Bag of Words keyword coverage")
        st.markdown("- TF-IDF concept extraction")
        st.markdown("- N-Gram fluency analysis")
        st.markdown("- POS tagging structure analysis")
        st.markdown("- NER skill/entity detection")

    if st.session_state.question_number == 0:
        st.info("Enter a role and start the interview. Your answers will be recorded from the microphone only.")
        return

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.subheader(f"Question {st.session_state.question_number} of {TOTAL_QUESTIONS}")
        st.write(st.session_state.current_question)
        speak_question_button(st.session_state.current_question)
        st.caption("Click Speak question, then answer using your microphone.")

        st.info(
            "Voice answer only: click the microphone, speak clearly for at least 8 seconds, "
            "stop recording, then submit. The machine will listen, transcribe, and evaluate automatically."
        )
        audio_file = st.audio_input(
            "Record your answer",
            key=f"voice_answer_{st.session_state.question_number}",
            disabled=st.session_state.finished,
        )
        if audio_file is not None:
            st.audio(audio_file.getvalue(), format="audio/wav")
            quality = analyze_recording_quality(audio_file.getvalue())
            if quality.is_long_enough and quality.is_loud_enough:
                st.success("Recording quality looks good. Now click Submit voice answer.")
            else:
                st.warning(quality.message)

        if st.button("Submit voice answer", disabled=st.session_state.finished):
            if submit_voice_answer(audio_file.getvalue() if audio_file else b""):
                st.rerun()

        if st.session_state.voice_notice:
            st.info(st.session_state.voice_notice)

        if st.session_state.last_transcript:
            with st.expander("Machine-heard transcript", expanded=True):
                st.write(st.session_state.last_transcript)

    with right:
        st.subheader("Latest Evaluation")
        if st.session_state.memory.turns:
            latest = st.session_state.memory.turns[-1]
            st.metric("Total", f"{latest.evaluation.total_score}/60")
            st.json(latest.evaluation.to_dict())
        else:
            st.write("Record and submit the first voice answer to see multi-axis scoring.")

    st.divider()
    st.subheader("Interview Memory")
    for turn in st.session_state.memory.turns:
        with st.expander(f"Q{turn.turn_number}: {turn.question}", expanded=False):
            st.write(turn.answer)
            st.json(turn.evaluation.to_dict())

    if st.session_state.finished:
        st.success("Interview complete. Generate the log and final report for submission.")
        report = build_report(st.session_state.memory)
        st.markdown(report.as_markdown())
        if st.button("Save interview_log.json and final_report.txt"):
            log_path, report_path = save_session()
            st.write(f"Saved log: {log_path}")
            st.write(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()

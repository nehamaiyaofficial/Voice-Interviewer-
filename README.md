# VoiceHire-NLP

Adaptive voice interview simulator for an NLP course project. It demonstrates the required interview loop and explicitly reuses lab concepts: Bag of Words, TF-IDF, N-Grams, POS tagging, NER, text classification-style scoring, and evaluation metrics.

## Features

- 10-question adaptive mock interview flow
- Voice question playback using browser TTS
- Microphone-only voice answer input using Streamlit's recorder
- Local Whisper transcription with `faster-whisper`
- Multi-axis evaluation: relevance, structure, clarity, confidence, keyword coverage, fluency
- BoW keyword coverage using expected role/question keywords
- TF-IDF important concept extraction
- N-Gram fluency and repetition analysis
- POS and NER analysis with spaCy when available, plus fallback heuristics
- Speaking pace, filler word, and pause analysis
- Interview memory, JSON logs, and final report generation
- Failure analysis section for subjective scoring and transcription errors

## How To Use The App

1. Start the app.
2. Enter the job role.
3. Click **Start new 10-question session**.
4. Click **Speak question** to hear the interview question.
5. Click **Record your answer** and speak clearly.
6. Stop the recording.
7. Click **Submit voice answer**.
8. The machine transcribes your voice, evaluates the answer, and asks the next adaptive question.

For best voice accuracy, speak near the microphone, avoid background noise, and answer for 30-90 seconds.

## Run In Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Optional spaCy model:

```bash
python -m spacy download en_core_web_sm
```

The app still runs if the spaCy model is not installed because it has a fallback POS/NER analyzer.

The first voice transcription can take longer because Whisper may download and prepare the local model.

## Run On Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## GitHub Submission Structure

```text
app.py
requirements.txt
README.md
prompts/
logs/
reports/
audio/
src/
tests/
```

`logs/.gitkeep`, `reports/.gitkeep`, and `audio/.gitkeep` keep the folders visible in GitHub. Generated logs, reports, and recordings are ignored by Git unless you intentionally add the final submission artifacts.

## Demo Submission Checklist

1. Run the Streamlit app.
2. Complete exactly 10 spoken questions and answers.
3. Save `logs/interview_log.json` and `reports/final_report.txt` from the app.
4. Record one complete session as `session_recording.mp4`.
5. In the report, show the failure analysis section and the lab concept mapping.

## Requirement Coverage

| Requirement | Implemented |
| --- | --- |
| LLM-style interviewer question | Yes, adaptive interviewer module with prompt version file |
| Spoken question using TTS | Yes, **Speak question** browser TTS button |
| Student voice answer | Yes, microphone-only answer recorder |
| Whisper transcription | Yes, `faster-whisper` transcription worker |
| Multi-axis evaluation | Yes: relevance, structure, clarity, confidence, keyword coverage, fluency |
| Adaptive follow-up | Yes, follow-ups visibly reference words from the previous answer |
| 10-question state | Yes, `InterviewMemory` tracks all turns |
| Final feedback report | Yes, generated after question 10 |
| Speaking pace | Yes, duration-based words per minute |
| Filler words | Yes, filler word counter |
| Failure analysis | Yes, report includes subjective scoring and transcription error analysis |
| Notebook | Yes, `notebooks/VoiceHire_Final.ipynb` |
| Demo recording | Must be recorded during your final run as `session_recording.mp4` |

## Notes

This project is designed to be reliable for classroom grading. It does not require an OpenAI/Gemini key to run, but the prompt files are included to show where LLM interviewer, evaluator, and report-generator prompts would be versioned.

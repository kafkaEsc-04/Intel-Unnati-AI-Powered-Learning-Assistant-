# Script to generate a transcript from an MP3 file provided to it.

from faster_whisper import WhisperModel
import sys
import os

def transcribe_audio(audio_path: str):
    model_name = "guillaumekln/faster-whisper-base"

    print(f"Loading model: {model_name}")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")

    print(f"Transcribing audio file: {audio_path}")
    segments, info = model.transcribe(audio_path, beam_size=5)

    print("\n--- TRANSCRIPTION START ---\n")
    for segment in segments:
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")
    print("\n--- TRANSCRIPTION END ---\n")

    print(f"\nDetected language: {info.language}")
    print(f"Language probability: {info.language_probability:.2f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_whisper_transcription.py <path_to_audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"File not found: {audio_file}")
        sys.exit(1)

    transcribe_audio(audio_file)

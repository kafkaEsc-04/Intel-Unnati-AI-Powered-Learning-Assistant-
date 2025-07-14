
import base64
import os
import tempfile
from faster_whisper import WhisperModel

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("guillaumekln/faster-whisper-base", device="cpu", compute_type="int8")
    return _whisper_model

def transcribe_audio_base64(base64_audio: str) -> str:
    # Transcribe the audio recorded from the mic 
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
        temp_file.write(base64.b64decode(base64_audio))
        temp_file_path = temp_file.name

    model = get_whisper_model()
    segments, _ = model.transcribe(temp_file_path)
    os.remove(temp_file_path)

    return " ".join(segment.text for segment in segments)

def transcribe_uploaded_mp3(mp3_file) -> str:
    #Transcribe the uploaded MP3 file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(mp3_file.read())
        temp_file_path = temp_file.name

    model = get_whisper_model()
    segments, _ = model.transcribe(temp_file_path)
    os.remove(temp_file_path)

    return " ".join(segment.text for segment in segments)

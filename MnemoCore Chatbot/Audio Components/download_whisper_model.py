from faster_whisper import WhisperModel


model = WhisperModel("guillaumekln/faster-whisper-base", device="cpu", compute_type="int8")

print("Whisper 'base' model downloaded successfully.")

import json
import os
from datetime import datetime
from pathlib import Path

# Directory to store chat logs
CHAT_LOG_DIR = "chat_logs"
Path(CHAT_LOG_DIR).mkdir(exist_ok=True)

def list_chat_sessions():
    """Returns list of saved session filenames (sorted)."""
    return sorted([
        f for f in os.listdir(CHAT_LOG_DIR)
        if f.endswith(".json")
    ])

def generate_new_session_name():
    """Returns a new unique session filename like: session_20250709_141355.json"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}.json"

def save_chat(session_file, chat_history):
    """Saves chat history (list of (role, message)) to disk."""
    data = [{"role": r, "content": m} for r, m in chat_history]
    with open(os.path.join(CHAT_LOG_DIR, session_file), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat(session_file):
    """Loads chat history from disk into list of (role, message) tuples."""
    path = os.path.join(CHAT_LOG_DIR, session_file)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [(item["role"], item["content"]) for item in data]

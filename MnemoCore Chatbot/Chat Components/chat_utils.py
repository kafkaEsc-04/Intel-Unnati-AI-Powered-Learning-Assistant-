import json
import os
from datetime import datetime
from pathlib import Path

# Folder to store chat logs
CHAT_LOG_DIR = "chat_logs"
Path(CHAT_LOG_DIR).mkdir(exist_ok=True)

def list_chat_sessions():
    #It returns a sorted list of session names
    return sorted([
        f for f in os.listdir(CHAT_LOG_DIR)
        if f.endswith(".json")
    ])

def generate_new_session_name():
    #It generates a unique session name of the form: session_YYYYMMDD_HHMMSS.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}.json"

def save_chat(session_file, chat_history):
    """Saves chat history as a list of {'role': 'user'/'assistant', 'content': ...}"""
    data = []
    for entry in chat_history:
        data.append({"role": "user", "content": entry["user"]})
        data.append({"role": "assistant", "content": entry["bot"]})
    with open(os.path.join(CHAT_LOG_DIR, session_file), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat(session_file):
    #Loads chat from file and converts to list of {'user': ..., 'bot': ...} entries.
    path = os.path.join(CHAT_LOG_DIR, session_file)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    history = []
    i = 0
    while i < len(data) - 1:
        user_msg = data[i]
        bot_msg = data[i + 1]
        if user_msg["role"] == "user" and bot_msg["role"] == "assistant":
            history.append({
                "user": user_msg["content"],
                "bot": bot_msg["content"]
            })
            i += 2
        else:
            i += 1  

    return history

import os
import json

DATA_DIR = "data"
USER_MEMORY_FILE = os.path.join(DATA_DIR, "user_memory.json")
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")


def safe_json_load(file_path, default_data):
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        return default_data

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty file")
            return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        return default_data


def init_memory():
    os.makedirs(DATA_DIR, exist_ok=True)
    safe_json_load(USER_MEMORY_FILE, {
        "name": "",
        "department": "",
        "hostel": "",
        "preferences": []
    })
    safe_json_load(CHAT_HISTORY_FILE, [])


def load_user_memory():
    return safe_json_load(USER_MEMORY_FILE, {
        "name": "",
        "department": "",
        "hostel": "",
        "preferences": []
    })


def update_memory_from_sidebar(name, department, hostel, preferences):
    memory = {
        "name": name,
        "department": department,
        "hostel": hostel,
        "preferences": preferences,
    }
    with open(USER_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def append_chat(role, content):
    chats = safe_json_load(CHAT_HISTORY_FILE, [])
    chats.append({"role": role, "content": content})
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)


def get_recent_chat(limit=10):
    chats = safe_json_load(CHAT_HISTORY_FILE, [])
    return chats[-limit:]
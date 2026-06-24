import json
import os
import datetime
import re
from memory_manager import load_user_memory

DATA_DIR = "data"
LOST_ITEMS_FILE = os.path.join(DATA_DIR, "lost_items.json")
FOUND_ITEMS_FILE = os.path.join(DATA_DIR, "found_items.json")
COMPLAINTS_FILE = os.path.join(DATA_DIR, "complaints.json")


def _read_list(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []


def _write_list(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def extract_lost_or_found_fields(text: str):
    text_l = text.lower()
    item_name = ""
    color = ""
    location = ""

    # naive extraction
    possible_items = ["wallet", "id card", "bottle", "water bottle", "charger", "keys", "earphones", "airpods", "bag", "notebook", "phone"]
    colors = ["black", "blue", "red", "white", "green", "yellow", "grey", "gray", "pink"]

    for p in possible_items:
        if p in text_l:
            item_name = p
            break

    for c in colors:
        if c in text_l:
            color = c
            break

    # location patterns
    loc_keywords = ["library", "canteen", "lab", "classroom", "hostel", "block", "room", "corridor"]
    for kw in loc_keywords:
        if kw in text_l:
            location = kw
            break

    # default/fallback values if extraction failed
    if not item_name:
        item_name = "item"
    if not color:
        color = "unknown color"
    if not location:
        location = "unknown location"

    return item_name, color, location


def extract_complaint_fields(text: str):
    text_l = text.lower()
    category = "general"
    issue = text.strip()
    location = ""
    priority = "medium"

    if "fan" in text_l or "light" in text_l or "projector" in text_l:
        category = "electrical"
    elif "wifi" in text_l or "wi-fi" in text_l or "internet" in text_l:
        category = "network"
    elif "washroom" in text_l or "clean" in text_l or "dirty" in text_l or "water cooler" in text_l:
        category = "maintenance"

    room_match = re.search(r"[A-Z]-\d{3}", text.upper())
    if room_match:
        location = room_match.group(0)
    else:
        location = "unknown location"

    if "urgent" in text_l or "high" in text_l:
        priority = "high"

    return category, issue, location, priority


def create_lost_report(user_input: str):
    item_name, color, location = extract_lost_or_found_fields(user_input)
    memory = load_user_memory()
    reporter_name = memory.get("name", "Unknown Student")

    reports = _read_list(LOST_ITEMS_FILE)
    next_id = f"LST-{len(reports) + 1:03d}"
    report = {
        "id": next_id,
        "item_name": item_name,
        "color": color,
        "location": location,
        "reporter_name": reporter_name,
        "date": datetime.date.today().isoformat(),
        "status": "lost"
    }
    reports.append(report)
    _write_list(LOST_ITEMS_FILE, reports)
    return f"Lost report created: {item_name} ({color}) lost at {location}. ID: {next_id}."


def create_found_report(user_input: str):
    item_name, color, location = extract_lost_or_found_fields(user_input)
    memory = load_user_memory()
    finder_name = memory.get("name", "Unknown Finder")

    reports = _read_list(FOUND_ITEMS_FILE)
    next_id = f"FND-{len(reports) + 1:03d}"
    report = {
        "id": next_id,
        "item_name": item_name,
        "color": color,
        "location": location,
        "finder_name": finder_name,
        "date": datetime.date.today().isoformat(),
        "status": "found"
    }
    reports.append(report)
    _write_list(FOUND_ITEMS_FILE, reports)
    return f"Found report created: {item_name} ({color}) found at {location}. ID: {next_id}."


def create_complaint(user_input: str):
    category, issue, location, priority = extract_complaint_fields(user_input)
    memory = load_user_memory()
    reporter_name = memory.get("name", "Unknown Student")

    complaints = _read_list(COMPLAINTS_FILE)
    next_id = f"CMP-{len(complaints) + 1:03d}"
    complaint = {
        "id": next_id,
        "category": category,
        "issue": issue,
        "location": location,
        "priority": priority,
        "reporter_name": reporter_name,
        "status": "open",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    complaints.append(complaint)
    _write_list(COMPLAINTS_FILE, complaints)
    return f"Complaint filed: '{issue}' ({category}, {priority} priority) at {location}. ID: {next_id}."


def get_complaint_status(user_input: str):
    match = re.search(r"CMP-\d+", user_input.upper())
    if not match:
        return "Please specify a valid complaint ID (e.g., CMP-001)."

    complaint_id = match.group(0)
    complaints = _read_list(COMPLAINTS_FILE)
    for c in complaints:
        if c["id"].upper() == complaint_id.upper():
            return f"Complaint {complaint_id} status is '{c['status']}' (Issue: {c['issue']}, Priority: {c['priority']})."

    return f"No complaint found with ID {complaint_id}."
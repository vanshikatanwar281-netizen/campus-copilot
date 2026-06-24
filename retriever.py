import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = "data"
VECTOR_STORE_DIR = "vector_store"
FAQ_DOCS_FILE = os.path.join(DATA_DIR, "faq_docs.json")
FAQ_CHUNKS_FILE = os.path.join(VECTOR_STORE_DIR, "faq_chunks.json")
ITEM_CHUNKS_FILE = os.path.join(VECTOR_STORE_DIR, "item_chunks.json")

LOST_ITEMS_FILE = os.path.join(DATA_DIR, "lost_items.json")
FOUND_ITEMS_FILE = os.path.join(DATA_DIR, "found_items.json")

DEFAULT_FAQS = [
    {
        "question": "How do I get a duplicate ID card?",
        "answer": "To get a duplicate ID card, apply at the Student Registry Office. You need to submit a written request and pay a replacement fee of $10 at the accounts desk."
    },
    {
        "question": "What are the central library timings?",
        "answer": "The central library is open from 8:00 AM to 10:00 PM on weekdays, and from 9:00 AM to 5:00 PM on weekends. During exam periods, the library remains open 24/7."
    },
    {
        "question": "How can I get my physical fee receipt?",
        "answer": "You can download your fee receipts from the student portal. For physical verification or stamping, visit the Admin Block Room 102."
    },
    {
        "question": "How do I report a hostel maintenance or room issue?",
        "answer": "For hostel issues (plumbing, electricity, cleaning), log a complaint on the Campus Portal or visit the Warden's office. For urgent matters, contact the caretaker."
    },
    {
        "question": "How do I register a new device on the campus Wi-Fi?",
        "answer": "To register your device on the campus Wi-Fi, visit the IT Support Desk in the Academic Block C with your student ID card and device MAC address."
    },
    {
        "question": "What is the policy for lost and found items on campus?",
        "answer": "Lost items should be reported to the security office near the main gate. Found items must be deposited there within 24 hours. Reports can also be filed using Campus Copilot."
    }
]


def _read_json(path, default_val):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return default_val
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default_val
            return json.loads(content)
    except Exception:
        return default_val


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_faq_vector_store():
    # Write default FAQs if data/faq_docs.json is empty/nonexistent
    faqs = _read_json(FAQ_DOCS_FILE, [])
    if not faqs:
        faqs = DEFAULT_FAQS
        _write_json(FAQ_DOCS_FILE, faqs)

    # Format FAQ entries as strings
    chunks = []
    for item in faqs:
        text = f"Question: {item['question']}\nAnswer: {item['answer']}"
        chunks.append(text)

    _write_json(FAQ_CHUNKS_FILE, chunks)
    return f"FAQ Vector Store built successfully with {len(chunks)} documents!"


def build_item_vector_store():
    lost_items = _read_json(LOST_ITEMS_FILE, [])
    found_items = _read_json(FOUND_ITEMS_FILE, [])

    chunks = []
    # Index lost items
    for item in lost_items:
        item_name = item.get("item_name") or item.get("item") or "unknown item"
        text = f"Type: lost | Item: {item_name} | Color: {item.get('color', '')} | Location: {item.get('location', '')} | Date: {item.get('date', '')}"
        chunks.append({
            "type": "lost",
            "id": item.get("id", ""),
            "text": text,
            "item_name": item_name,
            "location": item.get("location", "unknown location"),
            "date": item.get("date", "unknown date")
        })

    # Index found items
    for item in found_items:
        item_name = item.get("item_name") or item.get("item") or "unknown item"
        text = f"Type: found | Item: {item_name} | Color: {item.get('color', '')} | Location: {item.get('location', '')} | Date: {item.get('date', '')}"
        chunks.append({
            "type": "found",
            "id": item.get("id", ""),
            "text": text,
            "item_name": item_name,
            "location": item.get("location", "unknown location"),
            "date": item.get("date", "unknown date")
        })

    _write_json(ITEM_CHUNKS_FILE, chunks)
    return f"Item Vector Store built successfully with {len(chunks)} items!"


def search_faq(query: str, top_k: int = 3):
    chunks = _read_json(FAQ_CHUNKS_FILE, [])
    if not chunks:
        build_faq_vector_store()
        chunks = _read_json(FAQ_CHUNKS_FILE, [])

    if not chunks:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.05:  # threshold
            results.append(chunks[idx])

    return results


def find_matching_items(query: str, top_k: int = 5):
    chunks = _read_json(ITEM_CHUNKS_FILE, [])
    if not chunks:
        build_item_vector_store()
        chunks = _read_json(ITEM_CHUNKS_FILE, [])

    if not chunks:
        return []

    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0.05:  # threshold
            results.append(chunks[idx])

    return results
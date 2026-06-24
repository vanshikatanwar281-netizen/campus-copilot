import streamlit as st

from memory_manager_new import (
    init_memory,
    load_user_memory,
    update_memory_from_sidebar,
)
from tools import (
    create_lost_report,
    create_found_report,
    create_complaint,
    get_complaint_status,
)
from retriever import (
    build_faq_vector_store,
    build_item_vector_store,
    search_faq,
    find_matching_items,
)

st.set_page_config(page_title="Campus Copilot", layout="wide")


def detect_intent(user_text: str) -> str:
    text = user_text.lower()

    if "complaint status" in text or "status of complaint" in text:
        return "complaint_status"
    elif "complaint" in text or "issue" in text:
        return "complaint"
    elif "lost" in text:
        return "lost_report"
    elif "found" in text:
        return "found_report"
    elif "match lost item" in text or "find matching item" in text:
        return "match_item"
    else:
        return "general"

def generate_local_answer(user_input, faq_hits, item_hits, tool_result, memory):
    text = user_input.lower()

    # If a tool was used, return that first
    if tool_result:
        return tool_result

    # FAQ answer
    if faq_hits:
        top = faq_hits[0]

        # case 1: retriever returned a dict
        if isinstance(top, dict):
            if "answer" in top:
                return f"### Answer\n**{top['answer']}**"
            elif "content" in top:
                return f"### Answer\n**{top['content']}**"

        # case 2: retriever returned a plain string
        if isinstance(top, str):
            return f"### Answer\n**{top}**"

    # Matching found item answer
    if item_hits:
        lines = ["### Possible matching found items:"]
        for i, item in enumerate(item_hits, start=1):
            if isinstance(item, dict):
                lines.append(
                    f"{i}. **{item.get('item_name', 'Unknown item')}** found at **{item.get('location', 'Unknown location')}** on **{item.get('date', 'Unknown date')}**\n"
                    f"   - Notes: {item.get('notes', 'No notes available')}"
                )
            else:
                lines.append(f"{i}. {str(item)}")
        return "\n\n".join(lines)

    # fallback rules
    if "library" in text:
        return "### Library Timings\nThe library is open from **8:00 AM to 8:00 PM on weekdays**."

    if "hostel leave" in text:
        return "### Hostel Leave\nYou can apply for hostel leave by filling the leave form at the hostel office."

    if "exam cell" in text:
        return "### Exam Cell\nThe exam cell is located in the **Administrative Block, 1st floor**."

    return (
        "I can help you with:\n\n"
        "- campus FAQs\n"
        "- lost & found reports\n"
        "- complaint registration\n"
        "- complaint status\n\n"
        "Try asking:\n"
        "- **What are library timings?**\n"
        "- **I lost my wallet near the library**\n"
        "- **I want to file a complaint about hostel water supply**"
    )


def main():
    init_memory()
    build_faq_vector_store()
    build_item_vector_store()

    st.title("🎓 Campus Copilot")
    st.caption("AI-style campus helpdesk for FAQs, lost & found, complaints, and student memory.")

    # Sidebar memory
    st.sidebar.header("👤 Student Memory")
    memory = load_user_memory()

    name = st.sidebar.text_input("Your name", memory.get("name", ""))
    department = st.sidebar.text_input("Department", memory.get("department", ""))
    hostel = st.sidebar.text_input("Hostel", memory.get("hostel", ""))
    interests = st.sidebar.text_area(
        "Preferences / notes",
        ", ".join(memory.get("preferences", []))
    )

    if st.sidebar.button("Save Memory"):
        prefs = [x.strip() for x in interests.split(",") if x.strip()]
        update_memory_from_sidebar(name, department, hostel, prefs)
        st.sidebar.success("Memory updated!")

    # chat state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # show old messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask Campus Copilot anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        intent = detect_intent(user_input)
        faq_hits = search_faq(user_input, top_k=2)
        item_hits = find_matching_items(user_input, top_k=2)
        tool_result = None

        # tool actions
        if intent == "lost_report":
            tool_result = create_lost_report(user_input)

        elif intent == "found_report":
            tool_result = create_found_report(user_input)

        elif intent == "complaint":
            tool_result = create_complaint(user_input)

        elif intent == "complaint_status":
            tool_result = get_complaint_status(user_input)

        elif intent == "match_item":
            if item_hits:
                lines = ["### Possible matching found items:"]
                for i, item in enumerate(item_hits, start=1):
                    lines.append(
                        f"{i}. **{item['item_name']}** found at **{item['location']}** on **{item['date']}**\n"
                        f"   - Notes: {item['notes']}"
                    )
                tool_result = "\n\n".join(lines)
            else:
                tool_result = "No matching found items right now."

        answer = generate_local_answer(user_input, faq_hits, item_hits, tool_result, memory)

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
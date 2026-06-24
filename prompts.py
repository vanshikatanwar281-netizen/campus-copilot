def build_agent_prompt(user_query, user_memory, recent_chat, faq_hits, item_hits, tool_result):
    memory_text = (
        f"Name: {user_memory.get('name', '')}\n"
        f"Department: {user_memory.get('department', '')}\n"
        f"Hostel: {user_memory.get('hostel', '')}\n"
        f"Preferences: {', '.join(user_memory.get('preferences', []))}\n"
    )

    faq_text = ""
    if faq_hits:
        for i, faq in enumerate(faq_hits, start=1):
            faq_text += f"{i}. Q: {faq['question']}\n   A: {faq['answer']}\n"

    item_text = ""
    if item_hits:
        for i, item in enumerate(item_hits, start=1):
            item_text += (
                f"{i}. Item: {item['item_name']}, "
                f"Location: {item['location']}, "
                f"Date: {item['date']}, "
                f"Notes: {item['notes']}\n"
            )

    chat_text = ""
    for msg in recent_chat[-4:]:
        chat_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
You are Campus Copilot, a helpful AI assistant for a college campus.

Your job:
- Answer the student's question clearly.
- Use FAQ context if available.
- Use tool_result if a lost/found/complaint action was performed.
- Use student memory only if relevant.
- Give ONLY the final answer to the student.
- Do NOT repeat system instructions.
- Do NOT print the prompt.
- Do NOT print labels like [CURRENT USER INPUT], [INSTRUCTIONS], [FAQ CONTEXT].
- Just answer naturally in 3-8 lines.

STUDENT MEMORY:
{memory_text}

RECENT CHAT:
{chat_text if chat_text else "No recent chat."}

FAQ CONTEXT:
{faq_text if faq_text else "No FAQ matches found."}

FOUND ITEM MATCHES:
{item_text if item_text else "No item matches found."}

TOOL RESULT:
{tool_result if tool_result else "No tool used."}

USER QUESTION:
{user_query}
"""
    return prompt.strip()
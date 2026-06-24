import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def ask_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "⚠️ GEMINI_API_KEY not found in .env file."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(prompt)

        if response and hasattr(response, "text") and response.text:
            return response.text.strip()

        # fallback if .text is empty
        if response and hasattr(response, "candidates"):
            try:
                parts = response.candidates[0].content.parts
                text = "".join([p.text for p in parts if hasattr(p, "text")])
                if text.strip():
                    return text.strip()
            except Exception:
                pass

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        return f"Gemini error: {e}"
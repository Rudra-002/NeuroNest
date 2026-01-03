from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_logic import analyze_screening

import google.generativeai as genai
import os
from dotenv import load_dotenv

# --------------------
# App setup
# --------------------
app = Flask(__name__)
CORS(app)

load_dotenv()

# --------------------
# Gemini AI setup (FREE, no card)
# --------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel("gemini-1.5-flash")

LEISURE_AI_PROMPT = """
You are NeuroNest AI, a calm, supportive, and empathetic assistant.

Rules you MUST follow:
- Do NOT provide medical diagnosis
- Do NOT label or classify the user
- Speak gently and reassuringly
- Keep responses simple and short
- Focus on awareness, support, and guidance
- Encourage professional consultation gently if needed

Tone:
Warm, calm, non-judgmental, hopeful.

You may say things like:
• We can take this step by step.
• I'm here with you.
• Would you like to explore this gently?
"""

# --------------------
# Existing route (KEEP)
# --------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = analyze_screening(data)
    return jsonify(result)

# --------------------
# New AI Chat route (ADDED)
# --------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "I'm here whenever you're ready 🌱"
        })

    try:
        response = gemini_model.generate_content(
            f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\nAssistant:"
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        return jsonify({
            "reply": "I'm here with you, but something went wrong. We can try again calmly 💙"
        }), 500

# --------------------
# Health check
# --------------------
@app.route("/")
def home():
    return jsonify({
        "status": "NeuroNest backend running",
        "endpoints": ["/analyze", "/chat"]
    })

# --------------------
# Run app
# --------------------
if __name__ == "__main__":
    app.run(port=3000, debug=True)

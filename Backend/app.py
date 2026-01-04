from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_logic import analyze_screening

from google import genai

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
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



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

    if not data:
        return jsonify({
            "error": "No screening data received"
        }), 400

    try:
        result = analyze_screening(data)
    except Exception as e:
        print("Analyze error:", e)
        return jsonify({
            "score": 0,
            "riskLevel": "Error",
            "summary": "Something went wrong while analyzing. Please try again.",
            "recommendations": []
        }), 500

    if not isinstance(result, dict):
        return jsonify({
            "score": 0,
            "riskLevel": "Unavailable",
            "summary": "We couldn’t process the screening right now.",
            "recommendations": []
        })

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
        response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\nAssistant:"
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

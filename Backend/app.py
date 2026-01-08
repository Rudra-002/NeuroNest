import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv
import traceback

load_dotenv()

# -------------------------------
# App setup
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# Gemini Client
# -------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "vbeta")
# Fixed: Use correct model name
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

print("=" * 50)
print("BACKEND STARTING")
print("GEMINI_MODEL:", GEMINI_MODEL)
print("API_KEY loaded:", bool(GEMINI_API_KEY))
print("=" * 50)

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. AI requests will fail.")

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": GEMINI_API_VERSION}
)

# -------------------------------
# AI System Prompt
# -------------------------------
LEISURE_AI_PROMPT = """You are NeuroNest AI — a calm, empathetic, and supportive assistant helping families learn about autism and child development.

Rules you MUST follow:
- Do NOT provide medical diagnosis
- Do NOT label or classify users
- Speak gently and reassuringly
- Keep responses simple and conversational (2-4 sentences usually)
- Focus on awareness, emotional support, and guidance
- Encourage professional consultation gently if appropriate

Tone: Warm, calm, non-judgmental, hopeful.

Remember: You're here to support, not diagnose."""

# =====================================================
# SCREENING ANALYSIS ROUTE
# =====================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    if not data:
        return jsonify({
            "score": 0,
            "riskLevel": "Unavailable",
            "summary": "No screening data received.",
            "recommendations": []
        }), 400

    try:
        score = sum(data.values())

        if score <= 6:
            risk = "Low"
            summary = "Your responses suggest low observable risk. Continue monitoring and supporting healthy development."
        elif score <= 12:
            risk = "Moderate"
            summary = "Some responses may indicate developmental differences. Consider observing patterns and seeking guidance."
        else:
            risk = "High"
            summary = "Several responses suggest potential developmental concerns. A professional consultation is recommended."

        return jsonify({
            "score": score,
            "riskLevel": risk,
            "summary": summary,
            "recommendations": [
                "Observe behavioral patterns over time",
                "Engage in supportive communication",
                "Consult a qualified professional if concerns persist"
            ]
        })

    except Exception as e:
        print("ANALYZE ERROR:", e)
        traceback.print_exc()
        return jsonify({
            "score": 0,
            "riskLevel": "Error",
            "summary": "Something went wrong while analyzing the screening.",
            "recommendations": []
        }), 500

# =====================================================
# LIST MODELS (DEBUG)
# =====================================================
@app.route("/models", methods=["GET"])
def list_models():
    try:
        models = client.models.list()
        names = []
        if isinstance(models, dict):
            for m in models.get("models", []):
                names.append(m.get("name"))
        else:
            for m in models:
                names.append(getattr(m, "name", None) or (m.get("name") if isinstance(m, dict) else None))
        return jsonify({"models": [n for n in names if n]})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =====================================================
# AI CHATBOT ROUTE (FIXED)
# =====================================================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.json or {}
        user_message = (data.get("message") or "").strip()
        
        print("\n" + "=" * 50)
        print("INCOMING CHAT REQUEST")
        print("User message:", user_message)
        print("=" * 50)

        if not user_message:
            return jsonify({"reply": "I'm here whenever you're ready 🌱"})

        # FIXED: Proper message formatting for Gemini
        try:
            # Build the full prompt
            full_prompt = f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\n\nAssistant:"
            
            print("Sending to Gemini with model:", GEMINI_MODEL)
            
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt
            )
            
            print("Raw response object:", response)
            
        except Exception as e:
            print("❌ SDK ERROR during generate_content:")
            traceback.print_exc()
            return jsonify({
                "reply": "I'm here with you, but I couldn't connect to my AI service. Please try again 💙",
                "error": str(e)
            }), 500

        # FIXED: Better response extraction with debugging
        text = None
        
        try:
            # Method 1: Try standard extraction
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if candidate.content.parts:
                        text = candidate.content.parts[0].text
                        print("✓ Extracted via candidates[0].content.parts[0].text")
            
            # Method 2: Try direct text attribute
            if not text and hasattr(response, 'text'):
                text = response.text
                print("✓ Extracted via response.text")
            
            # Method 3: Check if response has a result attribute
            if not text and hasattr(response, 'result'):
                text = str(response.result)
                print("✓ Extracted via response.result")
                
        except Exception as extraction_error:
            print("❌ Extraction error:")
            traceback.print_exc()

        if not text:
            print("❌ Could not extract text from response")
            print("Response type:", type(response))
            print("Response dir:", dir(response))
            return jsonify({
                "reply": "I'm here with you, but I couldn't generate a proper response. Please try again 💙"
            }), 500

        print("✓ SUCCESSFUL RESPONSE:")
        print(text)
        print("=" * 50 + "\n")
        
        return jsonify({"reply": text.strip()})

    except Exception as outer_error:
        print("❌ OUTER EXCEPTION:")
        traceback.print_exc()
        return jsonify({
            "reply": "I'm here with you, but something went wrong. Please try again 💙",
            "error": str(outer_error)
        }), 500

# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "gemini_key_loaded": bool(GEMINI_API_KEY),
        "gemini_api_version": GEMINI_API_VERSION,
        "gemini_model": GEMINI_MODEL
    })

@app.route("/", methods=["GET"])
def home():
    return "NeuroNest backend is running ✓"

# -------------------------------
# Run locally
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)

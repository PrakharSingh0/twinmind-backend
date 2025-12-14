import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Required if frontend is on a different port/domain
from gemini_client import analyze_transcript

app = Flask(__name__)
# Enable CORS for all routes (Allow all origins *)
# For production, change "*" to your specific frontend URL
CORS(app) 

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Gemini Transcript Analyzer"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    
    # Check if data exists and has the transcript key
    if not data or "transcript" not in data:
        return jsonify({"error": "Missing 'transcript' field in request body"}), 400

    transcript = data.get("transcript")
    
    # Basic validation to save API tokens
    if len(transcript.strip()) < 10:
        return jsonify({"error": "Transcript is too short to analyze"}), 400

    result = analyze_transcript(transcript)
    return jsonify(result)

if __name__ == "__main__":
    # Get PORT from environment (Render/Heroku/Railwau set this automatically)
    # Default to 10000 for local development
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
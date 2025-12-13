from flask import Flask, request, jsonify
import whisper
import os
import uuid
from gemini_client import analyze_transcript

app = Flask(__name__)

whisper_model = whisper.load_model("tiny")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/process-audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(filepath)

    # Speech → Text
    result = whisper_model.transcribe(filepath)
    transcript = result["text"]
    language = result["language"]

    os.remove(filepath)

    # Text → Structured Analysis
    analysis = analyze_transcript(transcript)

    return jsonify({
        "transcript": transcript,
        "language": language,
        "title": analysis.get("title"),
        "summary": analysis.get("summary"),
        "action_items": analysis.get("action_items", []),
        "key_points": analysis.get("key_points", [])
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

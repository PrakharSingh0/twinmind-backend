import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_transcript(transcript: str) -> dict:
    prompt = f"""
You are an AI assistant that analyzes meeting or conversation transcripts.

From the transcript below, generate a structured response in STRICT JSON format with the following keys:
- title (string)
- summary (string, 4–6 lines)
- action_items (array of strings)
- key_points (array of strings)

Rules:
- Do NOT add explanations
- Do NOT add markdown
- Output ONLY valid JSON
- If action items are not explicit, infer reasonable ones

Transcript:
{transcript}
"""

    response = model.generate_content(prompt)

    # Gemini sometimes returns text → parse JSON safely
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "title": "Transcript Summary",
            "summary": response.text,
            "action_items": [],
            "key_points": []
        }

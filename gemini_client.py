import google.generativeai as genai
import os
import json
import logging

# Configure logging to catch errors in production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is missing from environment variables")
        raise RuntimeError("GEMINI_API_KEY missing")

    genai.configure(api_key=api_key)

    # Configuration to FORCE JSON output
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json", # <--- CRITICAL UPDATE
    }

    return genai.GenerativeModel(
        model_name="gemini-1.5-flash", # Generic alias usually points to latest stable
        generation_config=generation_config,
    )

# Initialize model once to avoid overhead on every request
model = get_model()

def analyze_transcript(transcript: str) -> dict:
    prompt = f"""
    You are an expert summarizer. Analyze the provided transcript and extract the following data.
    
    Output must be a raw JSON object with exactly these keys:
    - title (string): A concise title for the content.
    - summary (string): A brief summary of the discussion.
    - action_items (list of strings): Specific tasks or actions mentioned.
    - key_points (list of strings): The most important bullet points.

    Transcript:
    {transcript}
    """

    try:
        response = model.generate_content(prompt)
        
        # Parse the text. Since we used response_mime_type, it should be clean JSON.
        return json.loads(response.text)

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}. Raw response: {response.text}")
        # Fallback if model hallucinates non-JSON
        return {
            "title": "Error Parsing Result",
            "summary": "The model returned a response that could not be parsed as JSON.",
            "raw_response": response.text,
            "action_items": [],
            "key_points": []
        }
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return {
            "title": "Service Error",
            "summary": "An internal error occurred while processing the transcript.",
            "action_items": [],
            "key_points": []
        }
"""
Translates video title + description into multiple major languages and
adds them as YouTube "localizations" - this makes the video discoverable
in search for viewers browsing YouTube in Spanish, Arabic, Hindi, French,
Indonesian, and Portuguese, WITHOUT creating separate videos or dubbing.
(For actual dubbed audio, use YouTube's native "Automatic dubbing"
feature in Studio settings, which works alongside this.)
"""
import os
import json
import time
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# Language code: language name, covering Tier 1 (highest ad-revenue)
# YouTube markets. Note: English already covers US, UK, Canada,
# Australia, New Zealand, Ireland - these need no translation. This
# list covers the non-English Tier 1 markets.
TARGET_LANGUAGES = {
    "de": "German",       # Germany, Austria, Switzerland
    "fr": "French",       # France, Belgium, Switzerland, Canada (Quebec)
    "nl": "Dutch",        # Netherlands, Belgium
    "sv": "Swedish",      # Sweden
    "no": "Norwegian",    # Norway
    "da": "Danish",       # Denmark
}


def translate_metadata(title: str, description: str) -> dict:
    """
    Returns a dict like:
    {"es": {"title": "...", "description": "..."}, "ar": {...}, ...}
    """
    lang_list = ", ".join(TARGET_LANGUAGES.values())
    prompt = f"""Translate this YouTube video title and description into
these languages: {lang_list}.

TITLE: {title}
DESCRIPTION: {description}

Keep the same tone and keep any hashtags in the description (hashtags
can stay in English/as-is if that's more natural). Return ONLY this
exact JSON, no preamble, no markdown fences:

{{
  "de": {{"title": "...", "description": "..."}},
  "fr": {{"title": "...", "description": "..."}},
  "nl": {{"title": "...", "description": "..."}},
  "sv": {{"title": "...", "description": "..."}},
  "no": {{"title": "...", "description": "..."}},
  "da": {{"title": "...", "description": "..."}}
}}"""

    api_key = os.getenv("GROQ_API_KEY")
    for attempt in range(4):
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 3000,
            },
            timeout=60,
        )
        if response.status_code == 429:
            time.sleep(15 * (attempt + 1))
            continue
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text, strict=False)

    raise ValueError("Rate limited too many times during translation")

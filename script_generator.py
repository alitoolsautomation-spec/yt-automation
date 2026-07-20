"""
Generates SEO-optimized story scripts, titles, descriptions, and tags
in the requested language using Groq API (free tier).
"""
import os
import json
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def generate_video_content(theme: str, language: str = "Urdu", video_format: str = "short") -> dict:
    if video_format == "long":
        length_instruction = "4-6 minute (roughly 600-900 words) in-depth"
        script_note = "This is a longer video, so develop the story with more detail, examples, and structure (intro, 2-3 main points, conclusion) while staying engaging throughout."
        footage_extra = ', "keyword 4", "keyword 5", "keyword 6", "keyword 7"'
    else:
        length_instruction = "60-90 second (roughly 150-220 words)"
        script_note = "Keep it tight and punchy since this is a short-form video."
        footage_extra = ""

    if language.lower() == "urdu":
        script_rules = """ZAROORI HIDAYAAT for "script" field (ye seedha text-to-speech
engine parhega, is liye):
- SIRF khaalis Urdu script (Nastaliq/Arabic letters, jaise عادت، سبق، وقت) mein likhein
- KABHI BHI Devanagari/Hindi script (jaise आदत, सबक, समय) istemal NA karein -
  ye ek aam ghalti hai, is se bachein, HAR lafz Urdu/Arabic letters mein ho
- Koi Roman Urdu nahi, koi English loanwords nahi
- Numbers ko bhi lafzon mein likhein (jaise "3" ki jagah "تین")
- Chote, simple, dramatic jumlay istemal karein taake sunne wala hooked rahe
- Koi bracket, emoji, ya special symbols is field mein na hon"""
        title_desc_lang = "Urdu"
    else:
        script_rules = """IMPORTANT RULES for the "script" field (this will be read
directly by a text-to-speech engine):
- Write in clear, natural, conversational English only
- Spell out numbers as words (e.g. "three" not "3")
- Use short, punchy sentences to keep the listener hooked
- No brackets, emojis, or special symbols in this field"""
        title_desc_lang = "English"

    prompt = f"""You are an expert YouTube Shorts creator and SEO strategist who
has grown multiple channels to monetization. You write viral, high-retention
short-form scripts AND search-optimized metadata.

Theme: {theme}
Output language: {title_desc_lang}

## SCRIPT ({length_instruction})
- Open with a strong hook in the first line (a question, shocking fact, or
  bold claim) that stops someone from scrolling
- Middle: tell a vivid, specific story or fact with real emotional or
  "wow" value - avoid generic/vague statements
- End with a punchy, memorable takeaway line
- {script_note}
- TONE: Write this like an energetic, dramatic storyteller narrating out
  loud - NOT like a calm textbook or news reader. Use these techniques:
  - Vary sentence length sharply: mix short punchy sentences ("He failed.
    Again.") with longer flowing ones for rhythm
  - Build suspense before key moments ("But then, something incredible
    happened...")
  - Use rhetorical questions to pull the listener in
  - Include a moment of tension, surprise, or a twist wherever the story
    allows it
  - React to the story as you tell it (mild exclamations, emphasis words
    like "incredible", "shocking", "here's the crazy part")
  - Avoid flat, purely factual delivery - make every sentence carry energy
{script_rules}

## SEO TITLE - THIS IS THE MOST IMPORTANT PART
Bad generic titles (NEVER write like this): "Discipline Leads To Success",
"A Story About Hard Work", "Motivation For Life"
Good high-CTR titles (write LIKE this): "This 1 Habit Made Him A Millionaire Before Age 30 💰",
"99% Of People Fail Because Of This ONE Mistake 😳", "The Real Reason Successful People Wake Up At 5AM 🔥",
"Scientists Just Discovered This Shocking Fact About Your Brain 🧠"
Rules:
- Use the FULL available space, 60-100 characters - longer, keyword-rich
  titles rank better in search than short vague ones
- Use DIGITS for numbers here (e.g. "99%", "3 Habits"), NOT spelled-out
  words - this rule is different from the script field below
- Include at least one strong, high-search-volume keyword phrase people
  actually type into YouTube search for this topic (e.g. "success habits",
  "motivational story", "space facts", "islamic reminder")
- MUST create curiosity or promise a specific payoff - never state the
  moral/lesson directly in the title
- Use patterns like: a number + surprising claim, "why X happens", "the
  real reason", "nobody tells you this", "99% don't know", "before/after"
- Exactly 1 relevant emoji at the very end that matches the topic's
  actual emotion (fire/lightbulb for insight, brain for facts, money
  only if genuinely about wealth)
- If you cannot make it punchy, specific, AND keyword-rich, rewrite it
  until you can

## SEO DESCRIPTION (critical for search ranking) - WRITE 6-8 FULL LINES
- Line 1-2: restate the hook/main keyword naturally as if answering what
  someone searched for (this is what shows in search results)
- Line 3-5: expand on the story/value, mention 2-3 related keywords
  naturally (not stuffed), build more curiosity
- Line 6: a soft call-to-action (follow/subscribe for more content like this)
- Then a blank line, followed by 10-12 relevant hashtags mixing broad
  high-traffic tags (#motivation #shorts #viral #factsdaily #successstory)
  with niche specific ones related to this exact topic
- Do NOT write a short 2-3 line description - this must be substantial
  and detailed for search ranking

## TAGS
- 10-15 tags mixing: broad high-search-volume tags (motivation, success,
  islamic reminder, facts, shorts, viral shorts), medium-competition niche
  tags related to the theme, and 2-3 long-tail specific phrase tags

Return ONLY this exact JSON, no preamble, no markdown fences:

{{
  "title": "SEO-optimized title in {title_desc_lang}",
  "script": "Full voiceover script in {title_desc_lang} (following script rules above)",
  "description": "SEO-optimized description in {title_desc_lang} with hashtags at the end",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "footage_keywords": ["english keyword for stock footage search 1", "keyword 2", "keyword 3"{footage_extra}]
}}"""

    api_key = os.getenv("GROQ_API_KEY")

    def _has_devanagari(text: str) -> bool:
        return any("\u0900" <= ch <= "\u097F" for ch in text)

    max_attempts = 3
    for attempt in range(max_attempts):
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1.0,
                "max_tokens": 3000,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        text = data["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text, strict=False)

        if language.lower() == "urdu":
            combined = result.get("title", "") + result.get("script", "") + result.get("description", "")
            if _has_devanagari(combined):
                print(f"    (Devanagari script detected in output, regenerating - attempt {attempt + 1}/{max_attempts})")
                continue

        return result

    raise ValueError("Could not generate clean Urdu-script content after multiple attempts")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    content = generate_video_content("sabar aur mehnat ki kamiyabi", "Urdu")
    print(json.dumps(content, indent=2, ensure_ascii=False))

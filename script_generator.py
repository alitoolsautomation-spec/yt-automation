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
        cta_note = ""
    else:
        length_instruction = "60-90 second (roughly 150-220 words)"
        script_note = "Keep it tight and punchy since this is a short-form video."
        footage_extra = ""
        cta_note = (" - since this is a Short, also mention there's a full, "
                     "deeper video on this exact topic on the channel, "
                     "encouraging viewers to check the channel for more")

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
has grown multiple channels to monetization, specifically targeting a
United States audience.

Theme: {theme}
Output language: {title_desc_lang}
Target audience: United States viewers

AUDIENCE TARGETING RULES:
- Use American English spelling and phrasing throughout (e.g. "favorite"
  not "favourite", "color" not "colour")
- Prefer examples, references, and figures that resonate with a US
  audience (well-known American entrepreneurs, US history, familiar
  US cultural touchpoints) when the theme allows it naturally - don't
  force it if the topic is universal (e.g. space facts, Islamic content)
- Use measurement units and cultural context familiar to US viewers
  (dollars, Fahrenheit, miles) when relevant

## SCRIPT ({length_instruction})
THE OPENING LINE IS THE MOST CRITICAL PART - most viewers decide to keep
watching or swipe away within 1-2 seconds. Follow these rules strictly:
- NEVER start with a greeting, intro, or setup ("Hi guys", "Today I want
  to tell you", "Let me tell you about", "Have you ever wondered")
- Start with a bold, specific, slightly shocking statement or an
  incomplete thought that creates an open curiosity gap the viewer MUST
  keep watching to close
- Good openers: "He was fired three times before he became a billionaire."
  / "This one habit is why 90% of people stay poor." / "Nobody tells you
  this about failure." / "In 1968 a scientist discovered something that
  changed everything."
- Bad openers (NEVER use): "Have you ever wondered why...", "Today we're
  going to talk about...", "This is a story about...", "Let me share
  with you..."
- The hook must be SPECIFIC (a name, number, date, or concrete claim),
  never vague or generic
- After the hook, keep escalating - each sentence should make the viewer
  want the next sentence, don't let the energy drop in the middle
- CRITICAL PACING RULE (based on real audience data): after the opening
  hook, reveal the core answer/habit/fact promised in the TITLE within
  the first 10 seconds (roughly the first 1-2 sentences) rather than
  saving it for the end. The title's promise must be delivered almost
  immediately, or viewers feel misled and leave - this directly hurts
  ranking. Then spend the rest of the script explaining WHY it works and
  HOW to apply it.
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

## ISLAMIC CONTENT REFERENCE RULE (only applies if the theme is Islamic)
If this video's theme is Islamic in nature, include a source reference in
the description (e.g. "Quran, Surah [Name] [Chapter:Verse]" or "Hadith,
[Collection name, e.g. Sahih Bukhari], [Book/Number if well known]").
CRITICAL ACCURACY RULE: Only cite a specific verse/hadith number if it is
a well-known, widely-cited one you are highly confident about (e.g.
commonly referenced verses on patience, gratitude, trust in Allah). If
you are not fully certain of the exact reference, do NOT invent a
citation - instead write "a general Islamic teaching on [topic]" without
a fabricated specific number. A wrong citation is worse than no citation.

## SEO TITLE - THIS IS THE MOST IMPORTANT PART
Bad generic titles (NEVER write like this): "Discipline Leads To Success",
"A Story About Hard Work", "Motivation For Life"
Good high-CTR titles (write LIKE this): "This 1 Habit Made Him A Millionaire Before Age 30 💰",
"99% Of People Fail Because Of This ONE Mistake 😳", "The Real Reason Successful People Wake Up At 5AM 🔥",
"Scientists Just Discovered This Shocking Fact About Your Brain 🧠", "This Habit Is Silently Ruining Your Success 😳"
Also consider "negative curiosity" framing (warning about a mistake or
harmful habit) as an alternative to purely positive framing - both
styles work well, vary between them across different videos.
Rules:
- Aim for 90-100 characters (use YouTube's full title limit for maximum
  keyword coverage and SEO value)
- CRITICAL: Front-load the most important word or benefit within the
  FIRST 3 WORDS, since mobile screens truncate titles fast and viewers
  scan left-to-right quickly. Put the name/subject/benefit first,
  supporting curiosity-hook words after.
  Example: "Thomas Edison's 1 Habit For Success (Millionaire Mindset)"
  is better than "The 1 Habit That Made Thomas Edison A Millionaire..."
  because "Thomas Edison" (the recognizable hook) appears immediately.
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
- IMPORTANT: Do not default to the "99% Of People Don't Know This 1
  Habit/Mistake" template every time - vary the structure across
  different videos (try "why X happens", "the real reason Y", "how X
  changed everything", "what nobody tells you", numbered lists,
  before/after framing, direct bold claims, etc.)

## SEO DESCRIPTION (critical for search ranking) - WRITE A LONG, FULL DESCRIPTION
YouTube allows up to 5000 characters - use a large portion of that space
(aim for 2500-4000 characters, several paragraphs) for maximum SEO value.
- Line 1-2: MUST repeat your main keywords naturally (e.g. "motivation",
  "success habits", "islamic reminder" - whichever apply) as if directly
  answering a search query, since this is what shows in search results
  and is weighted heaviest by YouTube's algorithm
- Next 2-4 full paragraphs: expand deeply on the video's story/topic -
  retell the key points in more detail, add context, mention related
  figures/concepts, explain why this matters in daily life, and
  naturally weave in related keywords throughout (informative and
  thorough, not keyword-stuffed)
- A paragraph connecting this to the channel's broader themes
  (motivation, Islamic wisdom, productivity, success)
- A soft call-to-action (follow/subscribe for more content like this){cta_note}
- Then a blank line, followed by 12-15 relevant hashtags mixing broad
  high-traffic tags (#motivation #shorts #viral #factsdaily #successstory)
  with niche specific ones related to this exact topic
- Do NOT write a short description - this must be long, substantial,
  and detailed for maximum search ranking value

## TAGS
- 10-15 tags mixing: broad high-search-volume GLOBAL tags (motivation,
  success, islamic reminder, facts, shorts, viral shorts - these work
  worldwide), medium-competition niche tags related to the theme, and
  2-3 long-tail specific phrase tags
- Do not limit tags to US-specific phrasing - use universal English
  terms that a global audience searches for in this niche

Return ONLY this exact JSON, no preamble, no markdown fences:

{{
  "title": "SEO-optimized title in {title_desc_lang}",
  "script": "Full voiceover script in {title_desc_lang} (following script rules above)",
  "description": "SEO-optimized description in {title_desc_lang} with hashtags at the end",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "engagement_comment": "A short, genuine question related to this video's topic that invites viewers to share their own experience or opinion in the comments (in {title_desc_lang})",
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
                "max_tokens": 5000,
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

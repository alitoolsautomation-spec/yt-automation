"""
Converts script text into an AI voiceover audio file using
Microsoft Edge TTS (completely free, no API key or signup required).
Picks an appropriate voice based on the requested language.
"""
import asyncio
import edge_tts

VOICES = {
    "urdu": "ur-PK-UzmaNeural",
    "english": "en-US-AriaNeural",
}
RATE = "-8%"
PITCH = "+0Hz"


def generate_voiceover(script_text: str, language: str = "Urdu",
                        output_path: str = "voiceover.mp3") -> str:
    voice = VOICES.get(language.lower(), VOICES["urdu"])

    async def _run():
        communicate = edge_tts.Communicate(script_text, voice, rate=RATE, pitch=PITCH)
        await communicate.save(output_path)

    asyncio.run(_run())
    return output_path


if __name__ == "__main__":
    path = generate_voiceover("Yeh aik test hai. Umeed hai yeh awaaz saaf sunayi degi.", "Urdu")
    print(f"Saved: {path}")
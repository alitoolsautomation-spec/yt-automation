"""
Fetches free, legal background music (Kevin MacLeod / incompetech.com,
hosted on Internet Archive, Creative Commons Attribution license) and
mixes it under the narration at low volume to set an emotional mood.
"""
import random
import requests
from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips

# A curated set of calm/uplifting/epic instrumental tracks suited to
# motivational and reflective content. All by Kevin MacLeod, licensed
# CC-BY 3.0 (free for commercial use with attribution).
TRACKS = [
    ("Bathed in the Light", "https://archive.org/download/Incompetech/mp3-royaltyfree/Bathed%20in%20the%20Light.mp3"),
    ("Ascending the Vale", "https://archive.org/download/Incompetech/mp3-royaltyfree/Ascending%20the%20Vale.mp3"),
    ("Aurea Carmina", "https://archive.org/download/Incompetech/mp3-royaltyfree/Aurea%20Carmina.mp3"),
    ("Achilles", "https://archive.org/download/Incompetech/mp3-royaltyfree/Achilles.mp3"),
    ("At Rest", "https://archive.org/download/Incompetech/mp3-royaltyfree/At%20Rest.mp3"),
]


def fetch_random_music(out_path: str = "music.mp3") -> tuple:
    """Returns (local_path, track_name_for_attribution)"""
    name, url = random.choice(TRACKS)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return out_path, name


def mix_narration_with_music(narration_path: str, music_path: str,
                              output_path: str = "mixed_audio.mp3",
                              music_volume: float = 0.12) -> str:
    """
    Combines narration (full volume) with background music (quiet,
    looped/trimmed to match narration length) into one audio file.
    """
    narration = AudioFileClip(narration_path)
    music = AudioFileClip(music_path)

    if music.duration < narration.duration:
        loops_needed = int(narration.duration // music.duration) + 1
        music = concatenate_audioclips([music] * loops_needed)
    music = music.subclipped(0, narration.duration)

    music = music.with_volume_scaled(music_volume)

    final = CompositeAudioClip([music, narration])
    final.write_audiofile(output_path)
    return output_path


def get_attribution_text(track_name: str) -> str:
    return (f"Music: \"{track_name}\" by Kevin MacLeod (incompetech.com) "
            f"Licensed under Creative Commons: By Attribution 3.0 "
            f"https://creativecommons.org/licenses/by/3.0/")

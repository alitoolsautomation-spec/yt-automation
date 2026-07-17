"""
Main pipeline: generates one full video (random topic + language from
categories.py) and uploads it to YouTube. Run this directly to produce
ONE video, or use scheduler.py to run it automatically 2-3 times a day.
"""
import os
import random
import shutil
import traceback
from datetime import datetime
from dotenv import load_dotenv

from categories import CATEGORIES
from script_generator import generate_video_content
from voice_generator import generate_voiceover
from footage_fetcher import fetch_clips
from video_assembler import assemble_video
from thumbnail_generator import generate_thumbnail
from youtube_uploader import upload_video, set_thumbnail

load_dotenv()


def run_pipeline():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = f"runs/{run_id}"
    os.makedirs(work_dir, exist_ok=True)

    category = random.choice(CATEGORIES)
    theme = category["theme"]
    language = category["language"]

    print(f"[{run_id}] Category: {theme} ({language})")

    print(f"[{run_id}] 1/5 Generating script + metadata...")
    content = generate_video_content(theme, language)
    print(f"    Title: {content['title']}")

    print(f"[{run_id}] 2/5 Generating voiceover...")
    audio_path = generate_voiceover(content["script"], language, f"{work_dir}/voiceover.mp3")

    print(f"[{run_id}] 3/5 Fetching background clips...")
    clip_paths = fetch_clips(content["footage_keywords"], out_dir=f"{work_dir}/clips")

    print(f"[{run_id}] 4/5 Assembling final video...")
    video_path = assemble_video(clip_paths, audio_path, content["title"],
                                 output_path=f"{work_dir}/final.mp4")

    print(f"[{run_id}] Generating thumbnail...")
    thumbnail_path = generate_thumbnail(video_path, content["title"],
                                         output_path=f"{work_dir}/thumbnail.jpg")

    print(f"[{run_id}] 5/5 Uploading to YouTube...")
    video_id = upload_video(
        video_path=video_path,
        title=content["title"],
        description=content["description"],
        tags=content["tags"],
    )
    set_thumbnail(video_id, thumbnail_path)

    print(f"[{run_id}] DONE -> https://youtube.com/watch?v={video_id}")

    shutil.rmtree(f"{work_dir}/clips", ignore_errors=True)

    return video_id


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        print("Pipeline failed:")
        traceback.print_exc()

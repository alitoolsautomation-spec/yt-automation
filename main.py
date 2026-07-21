"""
Main pipeline: generates one full video (random topic + language +
format from categories.py) and uploads it to YouTube.
"""
import os
import sys
import json
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
from youtube_uploader import upload_video, set_thumbnail, post_engagement_comment

load_dotenv()


def run_pipeline():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = f"runs/{run_id}"
    os.makedirs(work_dir, exist_ok=True)

    if len(sys.argv) > 1:
        category = CATEGORIES[int(sys.argv[1])]
    else:
        category = random.choice(CATEGORIES)
    theme = category["theme"]
    language = category["language"]
    video_format = category.get("format", "short")
    orientation = "horizontal" if video_format == "long" else "vertical"

    print(f"[{run_id}] Category: {theme} ({language}, {video_format})")

    print(f"[{run_id}] 1/5 Generating script + metadata...")
    content = generate_video_content(theme, language, video_format)
    print(f"    Title: {content['title']}")

    print(f"[{run_id}] 2/5 Generating voiceover...")
    audio_path = generate_voiceover(content["script"], language, f"{work_dir}/voiceover.mp3")

    print(f"[{run_id}] 3/5 Fetching background clips...")
    clip_paths = fetch_clips(content["footage_keywords"], out_dir=f"{work_dir}/clips",
                              orientation=orientation)

    print(f"[{run_id}] 4/5 Assembling final video...")
    video_path = assemble_video(clip_paths, audio_path, content["title"],
                                 output_path=f"{work_dir}/final.mp4",
                                 orientation=orientation)

    print(f"[{run_id}] Generating thumbnail...")
    thumbnail_path = generate_thumbnail(video_path, content["title"],
                                         output_path=f"{work_dir}/thumbnail.jpg",
                                         orientation=orientation)

    print(f"[{run_id}] 5/5 Uploading to YouTube...")
    video_id = upload_video(
        video_path=video_path,
        title=content["title"],
        description=content["description"],
        tags=content["tags"],
    )
    set_thumbnail(video_id, thumbnail_path)

    if content.get("engagement_comment"):
        post_engagement_comment(video_id, content["engagement_comment"])

    print(f"[{run_id}] DONE -> https://youtube.com/watch?v={video_id}")

    # Save script content permanently to a log file (so it's never lost)
    log_entry = {
        "run_id": run_id,
        "video_id": video_id,
        "video_url": f"https://youtube.com/watch?v={video_id}",
        "language": language,
        "format": video_format,
        "title": content["title"],
        "script": content["script"],
        "description": content["description"],
        "tags": content["tags"],
    }
    with open("scripts_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    shutil.rmtree(f"{work_dir}/clips", ignore_errors=True)

    return video_id


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        print("Pipeline failed:")
        traceback.print_exc()

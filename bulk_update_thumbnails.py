"""
One-time tool: regenerates and updates thumbnails for ALL existing
videos on your channel using the new bold-text + portrait-photo style.

Usage:
  python bulk_update_thumbnails.py
"""
import time
from dotenv import load_dotenv
from youtube_uploader import get_authenticated_service, set_thumbnail
from bulk_update_seo import get_all_video_ids
from thumbnail_generator import generate_thumbnail

load_dotenv()


def main():
    youtube = get_authenticated_service()
    video_ids = get_all_video_ids(youtube)
    print(f"Found {len(video_ids)} videos.\n")

    confirm = input(f"This will replace thumbnails for all {len(video_ids)} videos. Type YES to continue: ")
    if confirm.strip() != "YES":
        print("Cancelled.")
        return

    for i, video_id in enumerate(video_ids):
        video_response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not video_response["items"]:
            continue
        title = video_response["items"][0]["snippet"]["title"]
        print(f"[{i+1}/{len(video_ids)}] {title}")

        try:
            thumb_path = generate_thumbnail(
                video_path=None,  # not needed since we use a fetched portrait photo
                hook_text=title,
                output_path=f"thumb_{video_id}.jpg",
            )
            set_thumbnail(video_id, thumb_path)
        except Exception as e:
            print(f"    Failed: {e}")

        time.sleep(2)  # be gentle on the Pexels free-tier rate limit

    print("\nDone.")


if __name__ == "__main__":
    main()

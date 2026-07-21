"""
Fetches relevant background video clips from Pexels (free stock footage API)
based on keywords generated for the script.
"""
import os
import requests

PEXELS_API_URL = "https://api.pexels.com/videos/search"


def fetch_clips(keywords: list, clips_per_keyword: int = 2, out_dir: str = "clips",
                 orientation: str = "vertical") -> list:
    os.makedirs(out_dir, exist_ok=True)
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    downloaded = []
    pexels_orientation = "landscape" if orientation == "horizontal" else "portrait"

    clip_counter = 0
    for i, keyword in enumerate(keywords):
        params = {"query": keyword, "per_page": clips_per_keyword, "orientation": pexels_orientation}
        resp = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for video in data.get("videos", [])[:clips_per_keyword]:
            # pick a reasonably sized HD file
            files = sorted(video["video_files"], key=lambda f: f.get("width", 0))
            best = next((f for f in files if 720 <= f.get("width", 0) <= 1080), files[-1])
            video_url = best["link"]

            local_path = os.path.join(out_dir, f"clip_{clip_counter}.mp4")
            clip_counter += 1
            with requests.get(video_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(local_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            downloaded.append(local_path)

    return downloaded


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    clips = fetch_clips(["nature sunrise", "mountain hiking", "ocean waves"])
    print(clips)

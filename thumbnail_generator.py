"""
Generates a professional YouTube thumbnail in the "bold text + serious
portrait photo" style: dark background, large bold text on one side,
a confident/serious-looking stock portrait on the other side.
Falls back to a video-frame-based thumbnail if no suitable photo is found.
"""
import os
import textwrap
import requests
from io import BytesIO
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont

PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"

PORTRAIT_SEARCH_TERMS = [
    "confident businessman portrait serious",
    "determined man face portrait dark",
    "focused professional portrait studio",
    "serious confident person portrait",
]


def _load_font(size):
    for font_path in [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _fetch_portrait_photo(topic_query: str = None):
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    import random
    if topic_query:
        # Combine the video's actual topic with portrait-style descriptors
        # so the photo matches what the video is about, not a random face
        search_query = f"{topic_query} portrait person"
    else:
        search_query = random.choice(PORTRAIT_SEARCH_TERMS)
    params = {"query": search_query, "per_page": 6, "orientation": "portrait"}
    resp = requests.get(PEXELS_PHOTO_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    photos = data.get("photos", [])
    if not photos and topic_query:
        # Topic-specific search found nothing - fall back to generic portrait terms
        search_query = random.choice(PORTRAIT_SEARCH_TERMS)
        params = {"query": search_query, "per_page": 6, "orientation": "portrait"}
        resp = requests.get(PEXELS_PHOTO_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        photos = data.get("photos", [])
    if not photos:
        return None
    photo = random.choice(photos)
    img_url = photo["src"]["large2x"]
    img_resp = requests.get(img_url, timeout=30)
    img_resp.raise_for_status()
    return Image.open(BytesIO(img_resp.content)).convert("RGB")


def generate_thumbnail(video_path: str, hook_text: str, output_path: str = "thumbnail.jpg",
                        orientation: str = "vertical", topic_query: str = None) -> str:
    thumb_w, thumb_h = 1280, 720
    canvas = Image.new("RGB", (thumb_w, thumb_h), (10, 10, 12))

    portrait = None
    try:
        portrait = _fetch_portrait_photo(topic_query)
    except Exception as e:
        print(f"    (Could not fetch portrait photo, using video frame fallback: {e})")

    if portrait:
        # Portrait fills most of the frame (dramatic close-up style like
        # top motivational channels), text overlaid on a dark box on
        # one side rather than a small side panel
        p = portrait.resize((thumb_w, int(portrait.height * thumb_w / portrait.width)))
        if p.height < thumb_h:
            p = p.resize((int(p.width * thumb_h / p.height), thumb_h))
        # crop to fill full canvas, biased toward upper portion (faces
        # are usually in the upper 2/3 of portrait photos)
        top = max(0, int((p.height - thumb_h) * 0.25))
        p = p.crop((0, top, thumb_w, top + thumb_h))
        # bias horizontally so the face tends toward the left/center,
        # leaving the right side a bit darker for text if needed
        canvas = p.convert("RGB")

        # Dark gradient overlay on one side (randomly left or right) so
        # text stays readable regardless of where the face ends up
        text_side = "right"
        gradient = Image.new("L", (thumb_w, thumb_h), 0)
        gdraw = ImageDraw.Draw(gradient)
        grad_w = int(thumb_w * 0.65)
        for x in range(grad_w):
            alpha = int(200 * (x / grad_w))
            gx = thumb_w - grad_w + x if text_side == "right" else grad_w - x
            gdraw.line([(gx, 0), (gx, thumb_h)], fill=alpha)
        dark_layer = Image.new("RGB", (thumb_w, thumb_h), (0, 0, 0))
        canvas = Image.composite(dark_layer, canvas, Image.eval(gradient, lambda a: a))
    else:
        if video_path:
            # Fallback: use a frame from the actual video as before
            clip = VideoFileClip(video_path)
            frame_time = min(1.0, clip.duration / 2)
            frame = clip.get_frame(frame_time)
            img = Image.fromarray(frame).convert("RGB")
            if orientation == "vertical":
                crop_h = int(img.width * thumb_h / thumb_w)
                top = max(0, (img.height - crop_h) // 3)
                img = img.crop((0, top, img.width, top + crop_h))
            img = img.resize((thumb_w, thumb_h))
            overlay = Image.new("RGB", img.size, (0, 0, 0))
            canvas = Image.blend(img, overlay, 0.4)
            clip.close()
        else:
            # No video file and no portrait photo available - plain dark canvas
            canvas = Image.new("RGB", (thumb_w, thumb_h), (15, 15, 18))

    draw = ImageDraw.Draw(canvas)
    text_area_w = int(thumb_w * 0.62) if portrait else thumb_w

    # Rotate through accent colors seen in high-performing thumbnails
    import random
    accent_color = random.choice([
        (255, 214, 0),   # yellow
        (255, 70, 70),   # red
        (0, 220, 210),   # teal/cyan
    ])

    # Big bold headline text, left-aligned, 3-4 words max per YouTube's guidance
    words = hook_text.split()[:4]
    headline = " ".join(words).upper()

    font_size = 108
    font = _load_font(font_size)
    wrapped = textwrap.fill(headline, width=10)
    lines = wrapped.split("\n")

    # shrink font if too many lines / too wide
    while True:
        font = _load_font(font_size)
        max_line_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)
        if max_line_w < text_area_w - 80 or font_size <= 50:
            break
        font_size -= 6
        wrapped = textwrap.fill(headline, width=10)
        lines = wrapped.split("\n")

    total_h = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines) * 1.25
    y = (thumb_h - total_h) / 2
    x_margin = int(thumb_w * 0.42) if portrait else 60

    for i, line in enumerate(lines):
        color = accent_color if i == len(lines) - 1 else (255, 255, 255)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1]
        outline_range = 3
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                draw.text((x_margin + dx, y + dy), line, font=font, fill=(0, 0, 0))
        draw.text((x_margin, y), line, font=font, fill=color)
        y += line_h * 1.3

    # Bold underline accent matching the headline's accent color
    draw.rectangle([x_margin, y + 10, x_margin + 220, y + 20], fill=accent_color)

    # Subtle vignette around the whole frame for a more polished, cinematic look
    vignette = Image.new("L", (thumb_w, thumb_h), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([0, 0, thumb_w, thumb_h], fill=0)
    border = 60
    vdraw.rectangle([border, border, thumb_w - border, thumb_h - border], fill=60)
    vignette = vignette.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(80))
    dark_layer = Image.new("RGB", (thumb_w, thumb_h), (0, 0, 0))
    canvas = Image.composite(canvas, dark_layer, vignette.point(lambda p: 255 - p))

    canvas.save(output_path, quality=95)
    return output_path

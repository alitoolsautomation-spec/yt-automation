"""
Generates a custom YouTube thumbnail: grabs a frame from the assembled
video and overlays bold, high-contrast text (from the title) on it -
the style that gets clicks (big text, strong colors, high contrast).
"""
import textwrap
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont


def generate_thumbnail(video_path: str, hook_text: str, output_path: str = "thumbnail.jpg") -> str:
    clip = VideoFileClip(video_path)
    # grab a frame ~1 second in (usually already past any fade-in)
    frame_time = min(1.0, clip.duration / 2)
    frame = clip.get_frame(frame_time)
    img = Image.fromarray(frame).convert("RGB")

    # Darken the image a bit so white text is readable
    overlay = Image.new("RGB", img.size, (0, 0, 0))
    img = Image.blend(img, overlay, 0.35)

    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Try a bold system font, fall back to default if not found
    font_size = int(width * 0.11)
    font = None
    for font_path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Keep text short + punchy for a thumbnail (first few words of the hook)
    short_text = " ".join(hook_text.split()[:6]).upper()
    wrapped = textwrap.fill(short_text, width=14)

    # Center the text with a bold black outline for readability
    lines = wrapped.split("\n")
    total_h = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines) * 1.2
    y = (height - total_h) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) / 2

        # Outline for readability against any background
        outline_range = max(2, font_size // 25)
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 214, 0))  # bold yellow
        y += line_h * 1.3

    img.save(output_path, quality=95)
    clip.close()
    return output_path

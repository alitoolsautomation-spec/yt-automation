"""
Generates a custom YouTube thumbnail: grabs a frame from the assembled
video and overlays bold, high-contrast text (from the title) on it.
Works for both vertical (Shorts) and horizontal (regular) videos.
"""
import textwrap
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont


def generate_thumbnail(video_path: str, hook_text: str, output_path: str = "thumbnail.jpg",
                        orientation: str = "vertical") -> str:
    clip = VideoFileClip(video_path)
    frame_time = min(1.0, clip.duration / 2)
    frame = clip.get_frame(frame_time)
    img = Image.fromarray(frame).convert("RGB")

    # Standard YouTube thumbnail is always 1280x720 (horizontal) even for
    # Shorts - so we letterbox/crop vertical frames into a 16:9 canvas.
    thumb_w, thumb_h = 1280, 720
    if orientation == "vertical":
        # center-crop a 16:9 slice out of the vertical frame for the thumbnail
        crop_h = int(img.width * thumb_h / thumb_w)
        top = max(0, (img.height - crop_h) // 3)  # bias toward upper-middle
        img = img.crop((0, top, img.width, top + crop_h))
    img = img.resize((thumb_w, thumb_h))

    overlay = Image.new("RGB", img.size, (0, 0, 0))
    img = Image.blend(img, overlay, 0.35)

    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = int(width * 0.12)
    font = None
    for font_path in [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
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

    short_text = " ".join(hook_text.split()[:4]).upper()
    wrapped = textwrap.fill(short_text, width=12)

    lines = wrapped.split("\n")
    total_h = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines) * 1.2
    y = (height - total_h) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) / 2

        outline_range = max(2, font_size // 25)
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 214, 0))
        y += line_h * 1.3

    img.save(output_path, quality=95)
    clip.close()
    return output_path

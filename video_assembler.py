"""
Combines the AI voiceover with background video clips into a final
video - vertical (9:16) for Shorts, or horizontal (16:9) for regular
long-form videos, depending on the "orientation" parameter.
"""
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


def assemble_video(clip_paths: list, audio_path: str, title: str,
                    output_path: str = "final_video.mp4",
                    orientation: str = "vertical") -> str:
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    if orientation == "horizontal":
        target_height = 1080
        target_width = 1920
    else:
        target_height = 1920
        target_width = 1080

    clips = []
    for p in clip_paths:
        c = VideoFileClip(p)
        c = c.resized(height=target_height)
        if c.w < target_width:
            c = c.resized(width=target_width)
        w = c.w
        x_center = w / 2
        c = c.cropped(x_center=x_center, width=target_width)
        clips.append(c)

    combined = concatenate_videoclips(clips, method="compose")

    if combined.duration < total_duration:
        loops_needed = int(total_duration // combined.duration) + 1
        combined = concatenate_videoclips([combined] * loops_needed, method="compose")
    combined = combined.subclipped(0, total_duration)

    final = combined.with_audio(audio)
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    return output_path

"""
Combines the AI voiceover with background video clips into a final
vertical (9:16) video ready for YouTube Shorts.
"""
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


def assemble_video(clip_paths: list, audio_path: str, title: str,
                    output_path: str = "final_video.mp4") -> str:
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    clips = []
    for p in clip_paths:
        c = VideoFileClip(p)
        c = c.resized(height=1920)
        w = c.w
        x_center = w / 2
        c = c.cropped(x_center=x_center, width=1080)
        clips.append(c)

    combined = concatenate_videoclips(clips, method="compose")

    if combined.duration < total_duration:
        loops_needed = int(total_duration // combined.duration) + 1
        combined = concatenate_videoclips([combined] * loops_needed, method="compose")
    combined = combined.subclipped(0, total_duration)

    final = combined.with_audio(audio)
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    return output_path
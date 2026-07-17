"""
Preview tool: generates a script + title + description + tags WITHOUT
creating a video or uploading anything. Use this to quickly test/tune
content quality before running the full pipeline.

Usage:
  python preview_content.py            -> random category
  python preview_content.py 3          -> use category index 3 from categories.py
"""
import sys
import json
import random
from dotenv import load_dotenv

from categories import CATEGORIES
from script_generator import generate_video_content

load_dotenv()

if len(sys.argv) > 1:
    category = CATEGORIES[int(sys.argv[1])]
else:
    category = random.choice(CATEGORIES)

print(f"Category: {category['theme']} ({category['language']})\n")

content = generate_video_content(category["theme"], category["language"])

print("=" * 50)
print("TITLE:", content["title"])
print("=" * 50)
print("SCRIPT:\n", content["script"])
print("=" * 50)
print("DESCRIPTION:\n", content["description"])
print("=" * 50)
print("TAGS:", ", ".join(content["tags"]))
print("=" * 50)

import json
import os
import time

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """You are watching an Instagram reel. Identify the single main resource,
tool, product, or place mentioned or shown in the video (the thing worth remembering).

The reel's caption is included below the video — captions often contain the actual
link or name that is only spoken or shown briefly on screen, so prefer it over a
guess when it's present.

Return ONLY valid JSON, no markdown fences, matching this schema:
{
  "title": string,
  "category": one of ["Tool / App", "Website / Platform", "Product", "Book / Course",
                       "Article / Guide", "Recipe", "Place / Travel", "Service", "Other"],
  "tags": array of strings, subset of
           ["AI", "Productivity", "Fitness", "Design", "Finance", "Travel",
            "Cooking", "Fashion", "Tech", "Marketing"],
  "link": string or null,
  "summary": string (1-2 sentences),
  "price": one of ["Free", "Paid", "Freemium", "Unknown"],
  "confidence": one of ["High", "Low"]
}

Set "confidence" to "Low" if the link/resource is only mentioned verbally and not
shown on screen, or if you are guessing. Set "link" to null if no URL is visible
or clearly stated.
"""


def extract_from_video(video_path: str, caption: str = "") -> dict:
    model = genai.GenerativeModel("gemini-1.5-flash")
    video_file = genai.upload_file(path=video_path)

    prompt = PROMPT
    if caption:
        prompt = f"{PROMPT}\n\nCaption:\n{caption}"

    try:
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise RuntimeError(f"Gemini file processing failed: {video_file.state.name}")

        response = model.generate_content([video_file, prompt])
    finally:
        genai.delete_file(video_file.name)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)

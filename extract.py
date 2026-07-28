import json
import os
import time

from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """You are watching an Instagram reel. Identify EVERY distinct resource,
tool, product, or place mentioned or shown in the video (the things worth
remembering) — a reel often lists several, not just one.

Pay close attention to BOTH the spoken narration (audio track) and any on-screen
text, captions, or overlays burned into the video — resource names are very
often said out loud and/or flashed on screen briefly, not just written in the
reel's caption. Watch and listen closely rather than relying only on the caption
text provided below.

The reel's caption is included below the video and can contain actual links
or names too, so use it as an extra signal.

Always fill in "title" with the actual name of each resource if it is said or
shown anywhere (audio, on-screen text, or caption) — never fall back to a vague
description when a real name was given.

Return ONLY valid JSON, no markdown fences: a JSON array of objects, one per
distinct resource found, each matching this schema:
{
  "title": string,
  "category": one of ["Tool / App", "Website / Platform", "Product", "Book / Course",
                       "Article / Guide", "Recipe", "Place / Travel", "Service", "Other"],
  "tags": array of strings, 1-4 specific niche/domain tags describing the
           resource - be precise and specific rather than generic, don't
           invent a fixed taxonomy, just describe what this actually is,
  "link": string or null,
  "summary": string (1-2 sentences),
  "price": one of ["Free", "Paid", "Freemium", "Unknown"],
  "confidence": one of ["High", "Low"]
}

If only one resource is present, return an array with a single object.

If a URL is directly visible or spoken (e.g. as a domain), use it exactly as
given for "link". If only a name is given (no domain), use your own knowledge
to work out the resource's real official website/URL and put that in "link" —
don't leave it null just because no ".com" was said out loud. Only leave "link"
null if you genuinely don't know or can't confidently identify the resource at
all. Set "confidence" to "Low" if you had to infer the URL from the name rather
than it being stated directly, or if you're unsure of the exact name/spelling;
"High" if the URL itself was clearly stated or shown.
"""


def extract_from_video(video_path: str, caption: str = "") -> list[dict]:
    video_file = client.files.upload(file=video_path)

    prompt = PROMPT
    if caption:
        prompt = f"{PROMPT}\n\nCaption:\n{caption}"

    try:
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise RuntimeError(f"Gemini file processing failed: {video_file.state.name}")

        response = client.models.generate_content(
            model="gemini-flash-latest", contents=[video_file, prompt]
        )
    finally:
        client.files.delete(name=video_file.name)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)

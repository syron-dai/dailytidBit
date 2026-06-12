import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import urllib.request
import xml.etree.ElementTree as ET
import re
from html import unescape

SGT = timezone(timedelta(hours=8))
today_dt = datetime.now(SGT)
today = today_dt.strftime("%Y-%m-%d")

root = Path(".")
data_dir = root / "data"
content_dir = root / "content"
languages_dir = content_dir / "languages"
data_dir.mkdir(parents=True, exist_ok=True)

latest_path = data_dir / "latest.json"
history_path = data_dir / "history.json"

def load_json(path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_html(text):
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def shorten(text, limit=220):
    text = clean_html(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "..."

def fetch_rss_items(url, limit=5):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            xml_data = response.read()
        root_xml = ET.fromstring(xml_data)
        items = []
        for item in root_xml.findall(".//item")[:limit]:
            title = clean_html(item.findtext("title", default="").strip())
            description = clean_html(item.findtext("description", default="").strip())
            link = item.findtext("link", default="").strip()
            items.append({
                "title": title,
                "summary": description,
                "link": link
            })
        return items
    except Exception:
        return []

def stable_index(seed_text, length):
    if length == 0:
        return 0
    digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    return int(digest, 16) % length

def build_top_story(item, world_items, sg_items, ai_items):
    title = item.get("title", "Top story")
    base = shorten(item.get("summary", ""), 320)

    why = []
    if world_items and len(world_items) > 1:
        why.append(f"Also in world news: {world_items[1]['title']}")
    if sg_items:
        why.append(f"In Singapore: {sg_items[0]['title']}")
    if ai_items:
        why.append(f"In technology: {ai_items[0]['title']}")

    return {
        "title": title,
        "summary": base,
        "why_points": why[:3]
    }

def enrich_story(item, region="world"):
    title = item.get("title", "")
    summary = shorten(item.get("summary", ""), 260)

    if region == "singapore":
        detail = f"{summary} This matters locally because it may affect safety, operations, policy attention, or daily life in Singapore."
    else:
        detail = f"{summary} This matters because it may influence geopolitics, markets, public safety, or international developments."

    return {
        "title": title,
        "summary": detail
    }

books = load_json(content_dir / "books.json", [])
japanese_lessons = load_json(languages_dir / "japanese.json", [])

book = books[stable_index(today + "-book", len(books))] if books else {
    "title": "Atomic Habits",
    "author": "James Clear",
    "summary": "Small repeated actions shape identity more effectively than dramatic one-off effort.",
    "lessons": [
        "Make good habits obvious and easy.",
        "Reduce friction for actions you want to repeat.",
        "Focus on identity, not just outcomes."
    ],
    "reflection": "What is one tiny behaviour you can repeat daily this week?"
}

lesson_idx = stable_index(today + "-jp", len(japanese_lessons))
language = japanese_lessons[lesson_idx] if japanese_lessons else {
    "lesson_number": 1,
    "phrase": "おつかれさまです",
    "romanization": "otsukaresama desu",
    "meaning": "Thanks for your hard work.",
    "usage": "Use this with colleagues after meetings or work.",
    "example": "Say this at the end of the workday.",
    "review_after_days": 2
}

review_lesson = None
if japanese_lessons:
    review_idx = max(0, lesson_idx - 1)
    review_lesson = japanese_lessons[review_idx]

world_feed = "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/rss.xml"
sg_feed = "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=10416"
ai_feed = "https://openai.com/news/rss.xml"

raw_world_items = fetch_rss_items(world_feed, limit=4)

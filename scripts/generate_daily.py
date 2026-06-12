import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import urllib.request
import xml.etree.ElementTree as ET

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

def fetch_rss_items(url, limit=5):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            xml_data = response.read()
        root_xml = ET.fromstring(xml_data)
        items = []
        for item in root_xml.findall(".//item")[:limit]:
            title = item.findtext("title", default="").strip()
            description = item.findtext("description", default="").strip()
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

world_items = fetch_rss_items(world_feed, limit=3)
sg_items = fetch_rss_items(sg_feed, limit=3)
ai_items = fetch_rss_items(ai_feed, limit=3)

lead_title = world_items[0]["title"] if world_items else "Daily Brief"
lead_summary = world_items[0]["summary"] if world_items else "Your daily update is ready."
lead_points = []

if len(world_items) > 1:
    lead_points.append(world_items[1]["title"])
if sg_items:
    lead_points.append(f"Singapore watch: {sg_items[0]['title']}")
if ai_items:
    lead_points.append(f"AI watch: {ai_items[0]['title']}")

history = load_json(history_path, [])

if latest_path.exists():
    previous = load_json(latest_path, {})
    prev_date = previous.get("date")
    if prev_date and not any(item.get("date") == prev_date for item in history):
        history.insert(0, {
            "date": previous.get("date"),
            "title": previous.get("lead_title", "Daily Brief"),
            "summary": previous.get("lead_summary", "")
        })

latest = {
    "date": today,
    "lead_title": lead_title,
    "lead_summary": lead_summary,
    "lead_points": lead_points,
    "world_items": world_items[:2],
    "sg_items": sg_items[:2],
    "book_name": book["title"],
    "book_author": book["author"],
    "book_summary": book["summary"],
    "book_lessons": book.get("lessons", []),
    "book_reflection": book.get("reflection", ""),
    "language_focus": "Japanese",
    "language_lesson_number": language.get("lesson_number", 1),
    "language_phrase": language.get("phrase", ""),
    "language_romanization": language.get("romanization", ""),
    "language_meaning": language.get("meaning", ""),
    "language_usage": language.get("usage", ""),
    "language_example": language.get("example", ""),
    "language_review_phrase": review_lesson.get("phrase", "") if review_lesson else "",
    "language_review_meaning": review_lesson.get("meaning", "") if review_lesson else "",
    "ai_tool_name": "OpenAI News",
    "ai_tool_update": ai_items[0]["title"] if ai_items else "No AI update found today.",
    "ai_tool_use_case": ai_items[0]["summary"] if ai_items else "Use AI to summarize and organize daily information."
}

save_json(latest_path, latest)
save_json(history_path, history)

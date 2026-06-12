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

def shorten(text, limit=260):
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

def build_top_story(item):
    title = item.get("title", "Top story")
    summary = shorten(item.get("summary", ""), 340)
    why_points = [
        "This is one of the day’s most notable developments and helps set the tone for the broader news cycle.",
        "It is worth watching for follow-up details, official responses, or wider knock-on effects."
    ]
    return {
        "title": title,
        "summary": summary,
        "why_points": why_points
    }

def enrich_story(item, region="world"):
    title = item.get("title", "")
    summary = shorten(item.get("summary", ""), 280)

    if region == "singapore":
        add_on = "For Singapore readers, the useful question is what this could mean for safety, policy, transport, work, or day-to-day life."
    elif region == "money":
        add_on = "The practical angle here is how this may affect travel costs, prices, savings, investing sentiment, or consumer decisions."
    else:
        add_on = "The useful angle here is what this could mean for geopolitics, markets, public safety, or the wider international picture."

    combined = f"{summary} {add_on}".strip()
    return {
        "title": title,
        "summary": combined
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
money_feed = "https://www.financeasia.com/rss/latest"
ai_feed = "https://openai.com/news/rss.xml"

raw_world_items = fetch_rss_items(world_feed, limit=4)
raw_sg_items = fetch_rss_items(sg_feed, limit=3)
raw_money_items = fetch_rss_items(money_feed, limit=3)
raw_ai_items = fetch_rss_items(ai_feed, limit=3)

top_source = raw_world_items[0] if raw_world_items else {"title": "Daily Brief", "summary": "Your daily update is ready."}
top_story = build_top_story(top_source)

world_items = [enrich_story(item, "world") for item in raw_world_items[1:3]]
sg_items = [enrich_story(item, "singapore") for item in raw_sg_items[:2]]
money_item = enrich_story(raw_money_items[0], "money") if raw_money_items else {
    "title": "Money & life watch",
    "summary": "A practical finance or cost-of-living item will appear here once a suitable source is available."
}
ai_items = raw_ai_items[:2]

history = load_json(history_path, [])

if latest_path.exists():
    previous = load_json(latest_path, {})
    prev_date = previous.get("date")
    if prev_date and not any(item.get("date") == prev_date for item in history):
        history.insert(0, {
            "date": previous.get("date"),
            "title": previous.get("top_story_title", "Daily Brief"),
            "summary": previous.get("top_story_summary", "")
        })

latest = {
    "date": today,
    "top_story_title": top_story["title"],
    "top_story_summary": top_story["summary"],
    "top_story_why_html": "".join(f"<li>{point}</li>" for point in top_story["why_points"]),
    "world_items": world_items,
    "sg_items": sg_items,
    "money_title": money_item["title"],
    "money_summary": money_item["summary"],
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
    "ai_tool_use_case": shorten(ai_items[0]["summary"], 220) if ai_items else "Use AI to summarize and organize daily information."
}

save_json(latest_path, latest)
save_json(history_path, history)

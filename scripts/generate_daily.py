import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

SGT = timezone(timedelta(hours=8))
today = datetime.now(SGT).strftime("%Y-%m-%d")

data_dir = Path("data")
editions_dir = data_dir / "editions"
data_dir.mkdir(parents=True, exist_ok=True)
editions_dir.mkdir(parents=True, exist_ok=True)

latest_path = data_dir / "latest.json"

sample = {
    "date": today,
    "lead_title": "Welcome to your Daily Brief",
    "lead_summary": "This is the starter edition for your personal daily newspaper.",
    "lead_point_1": "World, Singapore, learning, and AI sections can be refreshed each day.",
    "lead_point_2": "Yesterday's content can be archived automatically by date.",
    "lead_impact": "This starter version proves the workflow and page layout are working.",
    "world_story_1_title": "Global markets watch inflation and rates",
    "world_story_1_summary": "A short sample world summary goes here. Later this will be replaced by real generated content.",
    "world_story_2_title": "Health and technology continue to overlap",
    "world_story_2_summary": "Another sample world item can go here for now.",
    "sg_story_1_title": "Singapore policy and transport updates",
    "sg_story_1_summary": "A sample Singapore summary goes here.",
    "sg_story_2_title": "Local workforce and cost-of-living themes",
    "sg_story_2_summary": "Another sample Singapore item goes here.",
    "book_name": "Atomic Habits",
    "book_author": "James Clear",
    "book_summary": "Small repeated actions shape identity more effectively than dramatic one-off effort.",
    "book_lesson_1": "Make good habits obvious and easy.",
    "book_lesson_2": "Reduce friction for actions you want to repeat.",
    "book_lesson_3": "Focus on identity, not just outcomes.",
    "language_focus": "Japanese",
    "language_phrase": "おつかれさまです",
    "language_meaning": "A common phrase meaning thank you for your hard work.",
    "language_note": "Start with one main language at a time, then rotate others lightly.",
    "ai_tool_name": "ChatGPT",
    "ai_tool_update": "AI tools can summarize, brainstorm, draft, and automate repetitive tasks.",
    "ai_tool_use_case": "Use it to turn articles or reports into concise daily learning notes."
}

with open(latest_path, "w", encoding="utf-8") as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)
This writes a starter data/latest.json file using UTF-8 JSON and creates folders if they do not already exist. Path.mkdir(parents=True, exist_ok=True) is the standard way to create nested folders safely in Python.

3) scripts/archive_previous.py
Create scripts/archive_previous.py and paste this:

python
import json
from pathlib import Path

data_dir = Path("data")
editions_dir = data_dir / "editions"
history_path = data_dir / "history.json"
latest_path = data_dir / "latest.json"

data_dir.mkdir(parents=True, exist_ok=True)
editions_dir.mkdir(parents=True, exist_ok=True)

if latest_path.exists():
    with open(latest_path, "r", encoding="utf-8") as f:
        latest = json.load(f)

    edition_date = latest.get("date", "unknown-date")
    dated_path = editions_dir / f"{edition_date}.json"

    with open(dated_path, "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history = [item for item in history if item.get("date") != edition_date]

    history.insert(0, {
        "date": edition_date,
        "title": latest.get("lead_title", "Daily Brief"),
        "summary": f"{latest.get('book_name', 'Book')} • {latest.get('language_focus', 'Language')} • {latest.get('ai_tool_name', 'AI')}"
    })

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

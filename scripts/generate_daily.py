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
    "language_romanization": "otsukaresama desu",
    "language_meaning": "A common phrase meaning thank you for your hard work.",
    "language_note": "Start with one main language at a time, then rotate others lightly.",
    "ai_tool_name": "ChatGPT",
    "ai_tool_update": "AI tools can summarize, brainstorm, draft, and automate repetitive tasks.",
    "ai_tool_use_case": "Use it to turn articles or reports into concise daily learning notes."
}

with open(latest_path, "w", encoding="utf-8") as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)

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

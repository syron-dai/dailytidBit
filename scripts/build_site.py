import json
from pathlib import Path

root = Path(".")
data_dir = root / "data"
site_dir = root / "site"
templates_dir = site_dir / "templates"
assets_dir = site_dir / "assets"
dist_dir = root / "dist"
dist_assets_dir = dist_dir / "assets"
dist_archive_dir = dist_dir / "archive"
dist_editions_dir = dist_dir / "editions"

for folder in [dist_dir, dist_assets_dir, dist_archive_dir, dist_editions_dir]:
    folder.mkdir(parents=True, exist_ok=True)

latest_path = data_dir / "latest.json"
history_path = data_dir / "history.json"

with open(latest_path, "r", encoding="utf-8") as f:
    latest = json.load(f)

if history_path.exists():
    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []
    
def story_items_to_html(items):
    if not items:
        return "<p>No items available today.</p>"
    blocks = []
    for item in items:
        blocks.append(f"""
        <article class="story">
          <h3>{item.get('title', '')}</h3>
          <p>{item.get('summary', '')}</p>
        </article>
        """)
    return "\n".join(blocks)

def bullets_to_html(items):
    if not items:
        return ""
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="bullet-list">{lis}</ul>'

def review_to_html(phrase, meaning):
    if not phrase:
        return ""
    return f'''
    <div class="review-box">
      <p class="meta">Quick review</p>
      <p><strong>{phrase}</strong> — {meaning}</p>
    </div>
    '''
    
home_template = (templates_dir / "home.html").read_text(encoding="utf-8")
archive_template = (templates_dir / "archive.html").read_text(encoding="utf-8")
styles = (assets_dir / "styles.css").read_text(encoding="utf-8")
appjs = (assets_dir / "app.js").read_text(encoding="utf-8")

(dist_assets_dir / "styles.css").write_text(styles, encoding="utf-8")
(dist_assets_dir / "app.js").write_text(appjs, encoding="utf-8")

def render(template, data):
    output = template
    for key, value in data.items():
        output = output.replace("{{" + key + "}}", str(value))
    return output

root_page_data = latest.copy()

root_page_data.update({
    "styles_path": "./assets/styles.css",
    "script_path": "./assets/app.js",
    "home_path": "./index.html",
    "archive_path": "./archive/index.html",
    "world_items_html": story_items_to_html(latest.get("world_items", [])),
    "sg_items_html": story_items_to_html(latest.get("sg_items", [])),
    "book_lessons_html": bullets_to_html(latest.get("book_lessons", [])),
    "language_review_html": review_to_html(
        latest.get("language_review_phrase", ""),
        latest.get("language_review_meaning", "")
    )
})

index_output = render(home_template, root_page_data)
(dist_dir / "index.html").write_text(index_output, encoding="utf-8")

archive_rows = []
for item in history:
    archive_rows.append(f"""
    <article class="archive-entry">
      <p class="meta">{item.get("date", "")}</p>
      <div>
        <h2><a href="../editions/{item.get("date", "")}.html">{item.get("title", "Daily Brief")}</a></h2>
        <p>{item.get("summary", "")}</p>
      </div>
    </article>
    """)

archive_page_data = {
    "styles_path": "../assets/styles.css",
    "script_path": "../assets/app.js",
    "home_path": "../index.html",
    "archive_path": "./index.html",
    "archive_rows": "\n".join(archive_rows) if archive_rows else "<p>No archived editions yet.</p>"
}

archive_output = render(archive_template, archive_page_data)
(dist_archive_dir / "index.html").write_text(archive_output, encoding="utf-8")

edition_data = latest.copy()
edition_data.update({
    "styles_path": "../assets/styles.css",
    "script_path": "../assets/app.js",
    "home_path": "../index.html",
    "archive_path": "../archive/index.html",
    "world_items_html": story_items_to_html(latest.get("world_items", [])),
    "sg_items_html": story_items_to_html(latest.get("sg_items", [])),
    "book_lessons_html": bullets_to_html(latest.get("book_lessons", [])),
    "language_review_html": review_to_html(
        latest.get("language_review_phrase", ""),
        latest.get("language_review_meaning", "")
    )
})

edition_output = render(home_template, edition_data)
edition_date = latest.get("date", "latest")
(dist_editions_dir / f"{edition_date}.html").write_text(edition_output, encoding="utf-8")

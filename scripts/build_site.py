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

home_template = (templates_dir / "home.html").read_text(encoding="utf-8")
archive_template = (templates_dir / "archive.html").read_text(encoding="utf-8")
styles = (assets_dir / "styles.css").read_text(encoding="utf-8")
appjs = (assets_dir / "app.js").read_text(encoding="utf-8")

for placeholder, value in latest.items():
    home_template = home_template.replace("{{" + placeholder + "}}", str(value))

(dist_dir / "index.html").write_text(home_template, encoding="utf-8")
(dist_assets_dir / "styles.css").write_text(styles, encoding="utf-8")
(dist_assets_dir / "app.js").write_text(appjs, encoding="utf-8")

archive_rows = []
for item in history:
    row = f'''
    <article class="archive-row">
      <p class="archive-date">{item.get("date", "")}</p>
      <div>
        <h2><a href="../editions/{item.get("date", "")}.html">{item.get("title", "Daily Brief")}</a></h2>
        <p>{item.get("summary", "")}</p>
      </div>
    </article>
    '''
    archive_rows.append(row)

archive_output = archive_template
archive_output = archive_output.replace(
    """
    <article class="archive-row">
      <p class="archive-date">12 Jun 2026</p>
      <div>
        <h2><a href="../editions/2026-06-12.html">The edition title for that day</a></h2>
        <p>Top headline, featured book, and language focus.</p>
      </div>
    </article>

    <article class="archive-row">
      <p class="archive-date">11 Jun 2026</p>
      <div>
        <h2><a href="../editions/2026-06-11.html">Another edition title</a></h2>
        <p>Short archive description generated from the daily content.</p>
      </div>
    </article>
    """,
    "\n".join(archive_rows) if archive_rows else "<p>No archived editions yet.</p>"
)

(dist_archive_dir / "index.html").write_text(archive_output, encoding="utf-8")

edition_template = home_template
edition_date = latest.get("date", "latest")
(dist_editions_dir / f"{edition_date}.html").write_text(edition_template, encoding="utf-8")

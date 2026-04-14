import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUTPUT = ROOT / "data" / "worst_movies.json"
DOCS_OUTPUT = ROOT / "docs" / "data" / "worst_movies.json"

sys.path.insert(0, str(SRC))

from app import scrape_worst_movies  # noqa: E402


def main(limit: int = 1000, max_score: int = 70) -> None:
    movies = scrape_worst_movies(limit=limit, max_score=max_score)

    # Merge with previously stored data so movies from temporarily unavailable
    # sources (e.g. Wikipedia blocked by egress) are preserved.
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        # Build index by key for tag merging
        new_index = {(m["title"].lower(), m["year"]): m for m in movies}
        for m in existing:
            key = (m["title"].lower(), m["year"])
            if key in new_index:
                # Merge tags from the stored copy onto the freshly scraped entry
                old_tags = set(m.get("tags", []))
                new_tags = set(new_index[key].get("tags", []))
                merged = list(old_tags | new_tags)
                if merged:
                    new_index[key]["tags"] = merged
            else:
                try:
                    rt = int(str(m.get("rating", "999")).rstrip("%"))
                except ValueError:
                    continue
                if rt <= max_score or m.get("featured"):
                    movies.append(m)
                    new_index[key] = m

    movies.sort(key=lambda m: m["title"].lower())
    movies = movies[:limit]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(movies, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved {len(movies)} movies to {OUTPUT}")

    # Mirror to docs/ for the static GitHub Pages site.
    DOCS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DOCS_OUTPUT.write_text(
        json.dumps(movies, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Mirrored to {DOCS_OUTPUT}")


if __name__ == "__main__":
    main(1000, 70)

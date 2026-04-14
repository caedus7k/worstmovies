import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUTPUT = ROOT / "data" / "worst_movies.json"

sys.path.insert(0, str(SRC))

from app import scrape_worst_movies  # noqa: E402


def main(limit: int = 50) -> None:
    movies = scrape_worst_movies(limit=limit)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(movies, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved {len(movies)} movies to {OUTPUT}")


if __name__ == "__main__":
    main(50)

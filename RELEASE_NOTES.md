# Release Notes

## April 14, 2026

### Highlights
- Added budget and box office metadata support across scraped movie entries.
- Updated the static docs site to show budget and box office comparisons on movie cards.
- Added Tommy Wiseau detection and tagging, including a dedicated `tommy-wiseau` filter in `docs/index.html`.
- Added budget support for Razzie Worst Picture entries and ensured IMDb Bottom 100 entries preserve the full movie schema.
- Regenerated `data/worst_movies.json` and mirrored the snapshot to `docs/data/worst_movies.json`.

### Files changed
- `src/app.py`
- `docs/app.js`
- `docs/index.html`
- `data/worst_movies.json`
- `docs/data/worst_movies.json`
- `README.md`

# Python Web Development

Source: Jeffallan/claude-skills (python-pro v1.1.0, fastapi-expert v1.1.0) — MIT License  
Adapted for: Flask + BeautifulSoup4 + requests (this project's stack)

## When to Use
Invoke when writing or modifying Python code in `src/app.py`, `scripts/scrape_worst_movies.py`, or any new Python files.

---

## Core Rules

### Must Do
- Type hints on all function signatures
- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- Handle all HTTP errors explicitly (`response.raise_for_status()`)
- Use context managers for resources
- Write Google-style docstrings for public functions
- Store configuration in environment variables, not hardcoded strings
- Use `pytest` for all tests; mock external HTTP calls

### Must Not Do
- Bare `except:` clauses — always catch specific exceptions
- Mutable default arguments (`def f(items=[])` — use `None` and set inside)
- Hardcode secrets, API keys, or credentials
- Make real network calls in tests
- Use `f"SELECT * FROM {table}"` — use parameterized queries if adding a DB

---

## Flask Patterns

```python
import os
from flask import Flask, render_template, request, abort
from typing import Any

app = Flask(__name__)


# Route with type-annotated helpers
@app.route("/", methods=["GET"])
def index() -> str:
    search: str = request.args.get("search", "").strip()
    max_score: int = int(request.args.get("max_score", "70"))
    error: str | None = None
    movies: list[dict[str, Any]] = []

    try:
        movies = scrape_worst_movies(limit=1000, max_score=max_score)
        if search:
            movies = [m for m in movies if search.lower() in m["title"].lower()]
    except requests.HTTPError as exc:
        error = f"Wikipedia returned an error: {exc}"
    except RuntimeError as exc:
        error = str(exc)

    return render_template("index.html", movies=movies, search=search, error=error)


# Environment-driven config
host: str = os.getenv("HOST", "0.0.0.0")
port: int = int(os.getenv("PORT", "5000"))
debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
```

---

## BeautifulSoup Patterns

```python
from bs4 import BeautifulSoup, Tag
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
}


def fetch_page(url: str, timeout: int = 30) -> BeautifulSoup:
    """Fetch a URL and return parsed HTML soup.

    Args:
        url: Target URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        Parsed BeautifulSoup document.

    Raises:
        requests.HTTPError: On non-2xx HTTP response.
        requests.ConnectionError: On network failure.
    """
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def safe_text(tag: Tag | None, default: str = "N/A") -> str:
    """Safely extract stripped text from a BeautifulSoup tag."""
    return tag.get_text(strip=True) if tag else default


def safe_href(tag: Tag | None, base: str = "https://en.wikipedia.org") -> str | None:
    """Safely build a full URL from an anchor's href attribute."""
    if tag is None:
        return None
    href = tag.get("href", "")
    return f"{base}{href}" if href.startswith("/") else href or None
```

---

## Error Handling

```python
import requests
from requests.exceptions import Timeout, ConnectionError


def robust_fetch(url: str) -> dict:
    """Fetch JSON with explicit error handling."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Timeout:
        raise RuntimeError(f"Request timed out: {url}")
    except ConnectionError as exc:
        raise RuntimeError(f"Network error fetching {url}: {exc}") from exc
    except requests.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.response.status_code} from {url}") from exc
```

---

## Type Annotations

```python
from typing import Any, TypedDict


class Movie(TypedDict):
    title: str
    year: str
    rating: str
    reviews: str
    genre: str
    description: str
    poster: str | None
    wiki_url: str | None
    rotten_tomatoes_url: str
    preview_url: str
    alt_preview_url: str


def scrape_worst_movies(
    limit: int = 1000,
    max_score: int = 70,
) -> list[Movie]:
    ...
```

---

## Modern Python Features

```python
# Structural pattern matching (Python 3.10+)
match response.status_code:
    case 200:
        return response.json()
    case 404:
        raise ValueError("Page not found")
    case _:
        response.raise_for_status()

# Walrus operator
if (match := rating_re.search(text)) is not None:
    score = int(match.group(1))

# f-string debugging
title = "Plan 9"
print(f"{title=}")  # prints: title='Plan 9'

# Pathlib
from pathlib import Path
data_path = Path(__file__).parent.parent / "data" / "worst_movies.json"
movies = json.loads(data_path.read_text())
```

---

## Quick Reference

| Topic | Best Practice |
|-------|---------------|
| HTTP errors | `response.raise_for_status()` then catch `requests.HTTPError` |
| Timeouts | Always pass `timeout=N` to `requests.get()` |
| Type hints | Use `X \| None` not `Optional[X]` |
| Bare except | Never — use `except (ValueError, RuntimeError):` |
| Secrets | `os.getenv("MY_KEY")` — never hardcode |
| Defaults | `def f(items=None): items = items or []` |
| Docstrings | Google style — Args, Returns, Raises |
| Linting | `ruff check .` and `mypy src/` |

# Testing Best Practices

Source: adapted from Jeffallan/claude-skills (code-reviewer, fastapi-expert) — MIT License

## When to Use
Invoke this skill when writing tests, setting up test suites, reviewing test coverage, or discussing test strategy for this project (Python Flask backend + vanilla JavaScript frontend).

---

## Python Testing (pytest)

### Project Setup
```bash
pip install pytest pytest-cov pytest-mock requests-mock
```

`pytest.ini` or `pyproject.toml`:
```ini
[tool:pytest]
testpaths = tests
addopts = --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Flask App Testing
```python
import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_search_filters_results(client, mocker):
    mock_movies = [
        {"title": "Plan 9", "year": "1957", "rating": "0%",
         "reviews": "51", "genre": "N/A", "description": "Bad film.",
         "poster": None, "wiki_url": None,
         "rotten_tomatoes_url": "https://rottentomatoes.com/search?search=Plan+9",
         "preview_url": "https://youtube.com/results?search_query=Plan+9+trailer",
         "alt_preview_url": "https://dailymotion.com/search/Plan+9+trailer"},
        {"title": "Manos", "year": "1966", "rating": "0%",
         "reviews": "20", "genre": "N/A", "description": "Terrible film.",
         "poster": None, "wiki_url": None,
         "rotten_tomatoes_url": "https://rottentomatoes.com/search?search=Manos",
         "preview_url": "https://youtube.com/results?search_query=Manos+trailer",
         "alt_preview_url": "https://dailymotion.com/search/Manos+trailer"},
    ]
    mocker.patch("src.app.scrape_worst_movies", return_value=mock_movies)

    response = client.get("/?search=plan")
    assert response.status_code == 200
    assert b"Plan 9" in response.data
    assert b"Manos" not in response.data


def test_scrape_error_shows_error_message(client, mocker):
    mocker.patch("src.app.scrape_worst_movies", side_effect=RuntimeError("Network error"))
    response = client.get("/")
    assert response.status_code == 200
    assert b"Network error" in response.data
```

### Mocking HTTP Requests
```python
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.app import fetch_wikipedia_page, parse_wikipedia_0_percent_page


def test_fetch_wikipedia_page_raises_on_error():
    with patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
        with pytest.raises(requests.HTTPError):
            fetch_wikipedia_page("https://example.com")


def test_parse_0_percent_page_returns_movies(requests_mock):
    html = """
    <table class="wikitable sortable">
      <tr><th>Title</th><th>Year</th><th>Reviews</th></tr>
      <tr><td><a href="/wiki/Plan_9">Plan 9</a></td><td>1957</td><td>51</td></tr>
    </table>
    """
    requests_mock.get(
        "https://en.wikipedia.org/wiki/List_of_films_with_a_0%25_rating_on_Rotten_Tomatoes?printable=yes",
        text=html,
    )
    movies = parse_wikipedia_0_percent_page()
    assert len(movies) == 1
    assert movies[0]["title"] == "Plan 9"
    assert movies[0]["rating"] == "0%"
```

### Pytest Patterns

| Pattern | Code |
|---------|------|
| Fixture scope | `@pytest.fixture(scope="session")` |
| Parametrize | `@pytest.mark.parametrize("x,y", [(1,2),(3,4)])` |
| Expected exception | `with pytest.raises(ValueError):` |
| Skip test | `@pytest.mark.skip(reason="WIP")` |
| Mark slow | `@pytest.mark.slow` |

---

## JavaScript Testing (Vanilla JS)

### Testing the `docs/app.js` Module
Use Jest or Vitest for unit tests on the filtering/rendering logic.

```bash
npm install --save-dev jest @jest/globals jsdom
```

`jest.config.js`:
```js
export default {
  testEnvironment: "jsdom",
  transform: {},
};
```

### Unit Test Example
```javascript
// tests/app.test.js
import { describe, it, expect, beforeEach } from "@jest/globals";

// Pure function extracted from app.js
const escapeHtml = (text) =>
  String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

describe("escapeHtml", () => {
  it("escapes ampersands", () => {
    expect(escapeHtml("AT&T")).toBe("AT&amp;T");
  });
  it("escapes angle brackets", () => {
    expect(escapeHtml("<script>")).toBe("&lt;script&gt;");
  });
  it("passes plain text through", () => {
    expect(escapeHtml("Plan 9")).toBe("Plan 9");
  });
});

describe("applyFilters", () => {
  const movies = [
    { title: "Plan 9", rating: "0%", year: "1957" },
    { title: "Birdemic", rating: "18%", year: "2010" },
    { title: "The Room", rating: "25%", year: "2003" },
  ];

  it("filters by title query", () => {
    const filtered = movies.filter((m) =>
      m.title.toLowerCase().includes("plan")
    );
    expect(filtered).toHaveLength(1);
    expect(filtered[0].title).toBe("Plan 9");
  });

  it("filters by max rating", () => {
    const maxRating = 18;
    const filtered = movies.filter(
      (m) => Number(m.rating.replace("%", "")) <= maxRating
    );
    expect(filtered).toHaveLength(2);
  });
});
```

### DOM Testing
```javascript
import { JSDOM } from "jsdom";

it("renders movie cards", () => {
  const dom = new JSDOM(`<div id="movies"></div><span id="movie-count"></span>`);
  global.document = dom.window.document;

  const moviesEl = document.getElementById("movies");
  moviesEl.innerHTML = `<article class="movie-card"><h2>Plan 9</h2></article>`;

  expect(moviesEl.querySelectorAll(".movie-card")).toHaveLength(1);
  expect(moviesEl.querySelector("h2").textContent).toBe("Plan 9");
});
```

---

## Code Review Checklist

| Category | Check |
|----------|-------|
| **Logic** | Edge cases handled? Null checks? |
| **Security** | Input validated? XSS prevention? No hardcoded secrets? |
| **Performance** | N+1 requests? Unnecessary re-renders? |
| **Tests** | 80%+ coverage? Edge cases tested? Mocks appropriate? |
| **Naming** | Clear, intention-revealing? |
| **Error handling** | Caught and surfaced to user? |

## Must Do
- Aim for 80%+ test coverage on business logic
- Test the unhappy path (errors, empty results, network failures)
- Use `pytest.fixture` for setup/teardown
- Mock external HTTP calls — never call real URLs in tests
- Keep tests fast: unit tests < 100ms, integration tests < 1s

## Must Avoid
- Testing implementation details instead of behaviour
- Shared mutable state between tests
- Catching and swallowing exceptions in tests
- Hardcoding delays (`time.sleep`) — use mocks instead

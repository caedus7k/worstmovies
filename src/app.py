import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from urllib.parse import quote_plus

app = Flask(__name__)

WIKIPEDIA_RT_0_URL = "https://en.wikipedia.org/wiki/List_of_films_with_a_0%25_rating_on_Rotten_Tomatoes?printable=yes"
WIKIPEDIA_WORST_21_URL = "https://en.wikipedia.org/wiki/List_of_21st_century_films_considered_the_worst?printable=yes"
WIKIPEDIA_WORST_20_URL = "https://en.wikipedia.org/wiki/List_of_20th_century_films_considered_the_worst?printable=yes"
WIKIPEDIA_RAZZIE_URL = "https://en.wikipedia.org/wiki/Golden_Raspberry_Award_for_Worst_Picture?printable=yes"
IMDB_BOTTOM_100_URL = "https://www.imdb.com/chart/bottom/"

CURATED_FILMS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "curated_films.json"
)
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://en.wikipedia.org/",
    "Connection": "keep-alive",
}

B_MOVIE_TITLES = {
    "Battlefield Earth",
    "Manos: The Hands of Fate",
    "Plan 9 from Outer Space",
    "The Room",
    "Sharknado",
    "The Happening",
    "The Wicker Man",
    "Killer Klowns from Outer Space",
    "Robot Monster",
    "The Giant Spider Invasion",
    "Carnosaur",
    "The Blob",
}
B_MOVIE_TITLE_KEYWORDS = (
    "battlefield earth",
    "manos",
    "plan 9",
    "sharknado",
    "the room",
    "killer klowns",
    "robot monster",
    "giant spider",
    "carnosaur",
)
B_MOVIE_DESCRIPTION_KEYWORDS = (
    "b-movie",
    "cult",
    "low budget",
    "direct-to-video",
    "direct to video",
    "drive-in",
    "schlock",
    "cheesy",
    "campy",
)

NEIL_BREEN_TITLES = {
    "Double Down",
    "I Am Here....Now",
    "Fateful Findings",
    "Pass Thru",
    "Twisted Pair",
    "Megalomaniac",
}
NEIL_BREEN_TITLE_KEYWORDS = (
    "double down",
    "i am here",
    "fateful findings",
    "pass thru",
    "twisted pair",
    "megalomaniac",
)
NEIL_BREEN_DESCRIPTION_KEYWORDS = (
    "neil breen",
    "breen",
)

TOMMY_WISEAU_TITLES = {
    "The Room",
    "The House That Drips Blood on Alex",
    "The Neighbors",
    "Best F(r)iends",
    "Homeless in America",
}
TOMMY_WISEAU_TITLE_KEYWORDS = (
    "the room",
    "house that drips blood",
    "the neighbors",
    "best f(r)iends",
    "homeless in america",
)
TOMMY_WISEAU_DESCRIPTION_KEYWORDS = (
    "tommy wiseau",
    "wiseau",
)


def fetch_wikipedia_page(url: str):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response


def build_rotten_tomatoes_search_url(title: str):
    return f"https://www.rottentomatoes.com/search?search={quote_plus(title)}"


def build_youtube_search_url(query: str):
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def build_dailymotion_search_url(query: str):
    return f"https://www.dailymotion.com/search/{quote_plus(query)}"


def parse_wikipedia_0_percent_page():
    response = fetch_wikipedia_page(WIKIPEDIA_RT_0_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="wikitable sortable")
    if not table:
        raise RuntimeError(
            "Could not locate the Rotten Tomatoes 0% list table on Wikipedia."
        )

    movies = []
    rows = table.select("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        title_cell = cells[0]
        title_link = title_cell.find("a")
        title = (
            title_link.text.strip() if title_link else title_cell.get_text(strip=True)
        )
        if not title:
            continue

        year = cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
        reviews = cells[2].get_text(strip=True).replace("[", "").replace("]", "")
        wiki_url = (
            f"https://en.wikipedia.org{title_link['href']}"
            if title_link and title_link.get("href")
            else None
        )

        movies.append(
            {
                "title": title,
                "year": year,
                "rating": "0%",
                "reviews": reviews,
                "genre": "N/A",
                "description": f"Listed on Wikipedia as a Rotten Tomatoes 0% film. Reviews recorded: {reviews}.",
                "poster": None,
                "wiki_url": wiki_url,
                "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
                "preview_url": build_youtube_search_url(f"{title} trailer"),
                "alt_preview_url": build_dailymotion_search_url(f"{title} trailer"),
            }
        )

    return movies


def parse_wikipedia_worst_films_page(url: str, max_score: int = 70):
    response = fetch_wikipedia_page(url)
    soup = BeautifulSoup(response.text, "html.parser")
    rating_re = re.compile(r"(\d{1,3})%\s+rating\s+on\s+Rotten\s+Tomatoes", re.I)
    reviews_re = re.compile(r"based on (\d{1,4}) reviews", re.I)

    movies = []
    for paragraph in soup.find_all("p"):
        text = paragraph.get_text(" ", strip=True)
        rating_match = rating_re.search(text)
        if not rating_match:
            continue

        score = int(rating_match.group(1))
        if score > max_score:
            continue

        heading = paragraph.find_previous(["h2", "h3"])
        if not heading:
            continue

        title_tag = heading.find("i")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        year_match = re.search(r"\((\d{4})\)$", heading.get_text(strip=True))
        year = year_match.group(1) if year_match else "N/A"
        reviews_match = reviews_re.search(text)
        reviews = reviews_match.group(1) if reviews_match else "N/A"
        wiki_url = (
            f"https://en.wikipedia.org/wiki/{heading['id']}"
            if heading.get("id")
            else None
        )
        description = text.split(". ", 1)[0].strip()
        if not description.endswith("."):
            description += "."

        movies.append(
            {
                "title": title,
                "year": year,
                "rating": f"{score}%",
                "reviews": reviews,
                "genre": "N/A",
                "description": description,
                "poster": None,
                "wiki_url": wiki_url,
                "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
                "preview_url": build_youtube_search_url(f"{title} trailer"),
                "alt_preview_url": build_dailymotion_search_url(f"{title} trailer"),
            }
        )

    return movies


def load_curated_movies(max_score: int = 70):
    """Return curated bad films from data/curated_films.json.

    Entries with ``"featured": true`` are always included regardless of their
    RT score — this lets actor spotlights (e.g. full Nicolas Cage filmography)
    appear even when their scores are above the current max_score threshold.
    """
    if not CURATED_FILMS_PATH.exists():
        return []
    raw = json.loads(CURATED_FILMS_PATH.read_text(encoding="utf-8"))
    movies = []
    for m in raw:
        try:
            rt = int(str(m["rating"]).rstrip("%"))
        except (ValueError, KeyError):
            continue
        featured = bool(m.get("featured"))
        if rt > max_score and not featured:
            continue
        title = m["title"]
        movie = {
            "title": title,
            "year": str(m.get("year", "N/A")),
            "rating": f"{rt}%",
            "reviews": str(m.get("reviews", "N/A")),
            "genre": m.get("genre", "N/A"),
            "description": m.get("description", ""),
            "poster": m.get("poster"),
            "wiki_url": m.get("wiki_url"),
            "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
            "preview_url": build_youtube_search_url(f"{title} trailer"),
            "alt_preview_url": build_dailymotion_search_url(f"{title} trailer"),
            "featured": featured,
            "tags": list(m.get("tags", [])),
        }
        _ensure_movie_tags(movie)
        movies.append(movie)
    return movies


def parse_razzie_worst_picture_page():
    """Parse Razzie Worst Picture winners from Wikipedia.

    Returns films found in the winners table.  Only films already present in
    CURATED_FILMS_PATH (matched by lower-cased title) will carry a numeric
    RT rating; unmatched winners are skipped so the rating filter stays valid.
    """
    response = fetch_wikipedia_page(WIKIPEDIA_RAZZIE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Build a quick lookup from the curated list (title_lower -> rating int)
    curated_ratings: dict[str, int] = {}
    if CURATED_FILMS_PATH.exists():
        for m in json.loads(CURATED_FILMS_PATH.read_text(encoding="utf-8")):
            try:
                rt = int(str(m["rating"]).rstrip("%"))
                curated_ratings[m["title"].lower()] = rt
            except (ValueError, KeyError):
                pass

    seen: set[str] = set()
    movies = []
    for table in soup.find_all("table", class_="wikitable"):
        for row in table.select("tr")[1:]:
            cells = row.find_all(["td", "th"])
            for cell in cells:
                link = cell.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                if not href.startswith("/wiki/"):
                    continue
                title = link.get_text(strip=True)
                if not title or len(title) < 2 or title in seen:
                    continue
                rt = curated_ratings.get(title.lower())
                if rt is None:
                    continue  # skip winners without a known RT score
                seen.add(title)
                movies.append(
                    {
                        "title": title,
                        "year": "N/A",
                        "rating": f"{rt}%",
                        "reviews": "N/A",
                        "genre": "N/A",
                        "description": f"Golden Raspberry Award (Razzie) Worst Picture winner with a {rt}% Rotten Tomatoes score.",
                        "poster": None,
                        "wiki_url": f"https://en.wikipedia.org{href}",
                        "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
                        "preview_url": build_youtube_search_url(f"{title} trailer"),
                        "alt_preview_url": build_dailymotion_search_url(
                            f"{title} trailer"
                        ),
                    }
                )
    return movies


def parse_imdb_bottom_100(max_score: int = 70):
    """Scrape the IMDb Bottom 100 chart.

    IMDb aggressively anti-scrapes (AWS WAF JS challenge), so this returns an
    empty list on failure rather than raising — the curated fallback covers the
    same films.
    """
    try:
        response = requests.get(
            IMDB_BOTTOM_100_URL,
            headers={
                **HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=20,
        )
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # IMDb renders its chart as a <ul> of <li> elements containing JSON-LD
    # data, or as plain <td> cells in older layouts.  Try both.
    movies = []
    seen: set[str] = set()

    # Modern layout: <script type="application/ld+json"> with ItemList
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data.get("itemListElement", [])
        for item in items:
            movie = item.get("item", item)
            title = movie.get("name", "").strip()
            if not title or title in seen:
                continue
            url = movie.get("url", "")
            year_str = str(movie.get("datePublished", "N/A"))[:4]
            rating_val = movie.get("aggregateRating", {}).get("ratingValue")
            # IMDb rating is out of 10; we need RT %. Skip if we can't map.
            if title in seen:
                continue
            seen.add(title)
            movies.append(
                {
                    "title": title,
                    "year": year_str,
                    "rating": "N/A",
                    "reviews": "N/A",
                    "genre": "N/A",
                    "description": f"Listed on IMDb Bottom 100{f' (IMDb rating: {rating_val}/10)' if rating_val else ''}.",
                    "poster": None,
                    "wiki_url": None,
                    "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
                    "preview_url": build_youtube_search_url(f"{title} trailer"),
                    "alt_preview_url": build_dailymotion_search_url(f"{title} trailer"),
                    "imdb_url": (
                        url if url.startswith("http") else f"https://www.imdb.com{url}"
                    ),
                }
            )

    # Legacy table layout fallback
    if not movies:
        for row in soup.select("table.chart tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            link = cells[1].find("a") if len(cells) > 1 else None
            if not link:
                continue
            title = link.get_text(strip=True)
            if not title or title in seen:
                continue
            href = link.get("href", "")
            seen.add(title)
            movies.append(
                {
                    "title": title,
                    "year": "N/A",
                    "rating": "N/A",
                    "reviews": "N/A",
                    "genre": "N/A",
                    "description": "Listed on IMDb Bottom 100.",
                    "poster": None,
                    "wiki_url": None,
                    "rotten_tomatoes_url": build_rotten_tomatoes_search_url(title),
                    "preview_url": build_youtube_search_url(f"{title} trailer"),
                    "alt_preview_url": build_dailymotion_search_url(f"{title} trailer"),
                    "imdb_url": f"https://www.imdb.com{href}" if href else None,
                }
            )

    # Drop movies without a usable RT score (rating == "N/A") when a max_score
    # filter is in effect; they can't pass the threshold check.
    return [m for m in movies if m["rating"] != "N/A" or max_score >= 100]


def _try(fn, *args, **kwargs):
    """Call fn(*args, **kwargs) and return its result, or [] on any exception."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return []


def _is_b_movie(movie: dict):
    title = (movie.get("title") or "").strip().lower()
    if title in {t.lower() for t in B_MOVIE_TITLES}:
        return True
    if any(keyword in title for keyword in B_MOVIE_TITLE_KEYWORDS):
        return True
    description = (movie.get("description") or "").lower()
    return any(keyword in description for keyword in B_MOVIE_DESCRIPTION_KEYWORDS)


def _ensure_b_movie_tag(movie: dict):
    if "tags" not in movie or movie["tags"] is None:
        movie["tags"] = []
    if _is_b_movie(movie) and "b-movie" not in movie["tags"]:
        movie["tags"].append("b-movie")


def _is_neil_breen_movie(movie: dict):
    title = (movie.get("title") or "").strip().lower()
    if title in {t.lower() for t in NEIL_BREEN_TITLES}:
        return True
    if any(keyword in title for keyword in NEIL_BREEN_TITLE_KEYWORDS):
        return True
    description = (movie.get("description") or "").lower()
    if "neil breen" in description:
        return True
    return any(keyword in description for keyword in NEIL_BREEN_DESCRIPTION_KEYWORDS)


def _ensure_neil_breen_tag(movie: dict):
    if "tags" not in movie or movie["tags"] is None:
        movie["tags"] = []
    if _is_neil_breen_movie(movie):
        if "neil-breen" not in movie["tags"]:
            movie["tags"].append("neil-breen")
        if "b-movie" not in movie["tags"]:
            movie["tags"].append("b-movie")


def _is_tommy_wiseau_movie(movie: dict):
    title = (movie.get("title") or "").strip().lower()
    if title in {t.lower() for t in TOMMY_WISEAU_TITLES}:
        return True
    if any(keyword in title for keyword in TOMMY_WISEAU_TITLE_KEYWORDS):
        return True
    description = (movie.get("description") or "").lower()
    if "tommy wiseau" in description:
        return True
    return any(keyword in description for keyword in TOMMY_WISEAU_DESCRIPTION_KEYWORDS)


def _ensure_tommy_wiseau_tag(movie: dict):
    if "tags" not in movie or movie["tags"] is None:
        movie["tags"] = []
    if _is_tommy_wiseau_movie(movie):
        if "tommy-wiseau" not in movie["tags"]:
            movie["tags"].append("tommy-wiseau")
        if "b-movie" not in movie["tags"]:
            movie["tags"].append("b-movie")


def _normalize_movie_tags(movie: dict):
    if "tags" not in movie or movie["tags"] is None:
        movie["tags"] = []
    movie["tags"] = [
        tag.lower() for tag in dict.fromkeys(str(t).strip() for t in movie["tags"] if t)
    ]


def _ensure_movie_tags(movie: dict):
    _normalize_movie_tags(movie)
    _ensure_b_movie_tag(movie)
    _ensure_neil_breen_tag(movie)
    _ensure_tommy_wiseau_tag(movie)


def _movie_visible(movie: dict, max_score: int):
    try:
        return int(movie["rating"].rstrip("%")) <= max_score
    except (ValueError, AttributeError):
        return bool(movie.get("featured"))


def scrape_worst_movies(limit: int = 1000, max_score: int = 70):
    movies = _try(parse_wikipedia_0_percent_page)
    movies.extend(
        _try(
            parse_wikipedia_worst_films_page,
            WIKIPEDIA_WORST_21_URL,
            max_score=max_score,
        )
    )
    movies.extend(
        _try(
            parse_wikipedia_worst_films_page,
            WIKIPEDIA_WORST_20_URL,
            max_score=max_score,
        )
    )
    movies.extend(load_curated_movies(max_score=max_score))
    movies.extend(_try(parse_imdb_bottom_100, max_score=max_score))

    unique_movies = {}
    for movie in movies:
        key = (movie["title"].lower(), movie["year"])
        existing = unique_movies.get(key)
        if existing is None:
            unique_movies[key] = movie
            continue

        # Merge tags and featured flag from both entries before deciding winner
        merged_tags = list({*existing.get("tags", []), *movie.get("tags", [])})
        merged_featured = existing.get("featured") or movie.get("featured")

        current_rating = int(movie["rating"].rstrip("%"))
        existing_rating = int(existing["rating"].rstrip("%"))
        if current_rating < existing_rating:
            unique_movies[key] = movie

        if merged_tags:
            unique_movies[key]["tags"] = merged_tags
        if merged_featured:
            unique_movies[key]["featured"] = True

    movies = []
    for movie in unique_movies.values():
        if _movie_visible(movie, max_score):
            _ensure_movie_tags(movie)
            movies.append(movie)

    movies.sort(key=lambda movie: movie["title"].lower())
    return movies[:limit]


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    error = None
    movies = []

    try:
        movies = scrape_worst_movies(limit=1000, max_score=70)
        if search:
            movies = [m for m in movies if search.lower() in m["title"].lower()]
    except Exception as exc:
        movies = []
        error = str(exc)

    return render_template("index.html", movies=movies, search=search, error=error)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host=host, port=port)

import os
import re

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from urllib.parse import quote_plus

app = Flask(__name__)

WIKIPEDIA_RT_0_URL = "https://en.wikipedia.org/wiki/List_of_films_with_a_0%25_rating_on_Rotten_Tomatoes?printable=yes"
WIKIPEDIA_WORST_21_URL = "https://en.wikipedia.org/wiki/List_of_21st_century_films_considered_the_worst?printable=yes"
WIKIPEDIA_WORST_20_URL = "https://en.wikipedia.org/wiki/List_of_20th_century_films_considered_the_worst?printable=yes"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://en.wikipedia.org/",
    "Connection": "keep-alive",
}


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


def scrape_worst_movies(limit: int = 1000, max_score: int = 70):
    movies = parse_wikipedia_0_percent_page()
    movies.extend(
        parse_wikipedia_worst_films_page(WIKIPEDIA_WORST_21_URL, max_score=max_score)
    )
    movies.extend(
        parse_wikipedia_worst_films_page(WIKIPEDIA_WORST_20_URL, max_score=max_score)
    )

    unique_movies = {}
    for movie in movies:
        key = (movie["title"].lower(), movie["year"])
        existing = unique_movies.get(key)
        if existing is None:
            unique_movies[key] = movie
            continue

        current_rating = int(movie["rating"].rstrip("%"))
        existing_rating = int(existing["rating"].rstrip("%"))
        if current_rating < existing_rating:
            unique_movies[key] = movie

    movies = [
        movie
        for movie in unique_movies.values()
        if int(movie["rating"].rstrip("%")) <= max_score
    ]
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

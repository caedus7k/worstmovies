import os

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from urllib.parse import quote_plus

app = Flask(__name__)

WIKIPEDIA_RT_0_URL = "https://en.wikipedia.org/wiki/List_of_films_with_a_0%25_rating_on_Rotten_Tomatoes?printable=yes"
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


def scrape_worst_movies(limit: int = 50):
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
        if len(movies) >= limit:
            break

    if not movies:
        raise RuntimeError(
            "No movies were found in the Rotten Tomatoes 0% Wikipedia list."
        )

    return movies


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    error = None
    movies = []

    try:
        movies = scrape_worst_movies(limit=50)
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

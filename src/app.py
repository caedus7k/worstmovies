import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from urllib.parse import quote_plus

app = Flask(__name__)

IMDB_SEARCH_URL = "https://www.imdb.com/search/title/"
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


def scrape_worst_english_movies(limit: int = 50):
    params = {
        "title_type": "feature",
        "languages": "en",
        "sort": "user_rating,asc",
        "count": limit,
    }
    response = requests.get(IMDB_SEARCH_URL, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    movies = []

    for item in soup.select(".lister-item.mode-advanced"):
        header = item.select_one(".lister-item-header a")
        if not header:
            continue

        title = header.text.strip()
        imdb_url = "https://www.imdb.com" + header["href"].split("?")[0]
        year_tag = item.select_one(".lister-item-year")
        year = year_tag.text.strip() if year_tag else "N/A"
        rating_tag = item.select_one(".ratings-imdb-rating strong")
        rating = rating_tag.text.strip() if rating_tag else "N/A"
        runtime_tag = item.select_one(".runtime")
        runtime = runtime_tag.text.strip() if runtime_tag else "N/A"
        genre_tag = item.select_one(".genre")
        genre = genre_tag.text.strip() if genre_tag else "N/A"
        description_tag = item.select_one(".ratings-bar + .text-muted")
        description = description_tag.text.strip() if description_tag else ""
        poster_tag = item.select_one(".lister-item-image img")
        poster = None
        if poster_tag:
            poster = poster_tag.get("loadlate") or poster_tag.get("src")

        search_query = quote_plus(f"{title} trailer")
        movies.append(
            {
                "title": title,
                "year": year,
                "rating": rating,
                "runtime": runtime,
                "genre": genre,
                "description": description,
                "poster": poster,
                "imdb_url": imdb_url,
                "preview_url": f"https://www.youtube.com/results?search_query={search_query}",
                "alt_preview_url": f"https://www.dailymotion.com/search/{search_query}",
            }
        )

    return movies


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").strip()
    movies = scrape_worst_english_movies(limit=50)
    if search:
        movies = [m for m in movies if search.lower() in m["title"].lower()]
    return render_template("index.html", movies=movies, search=search)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# Worst Movies Web App

A simple Flask web app that scrapes films from Wikipedia's Rotten Tomatoes 0% list and provides preview links to Rotten Tomatoes, YouTube, and Dailymotion.

## Setup
1. Open the project folder in VS Code.
2. Create a Python virtual environment.
3. Install dependencies:
   ```
pip install -r requirements.txt
```

## Run
```bash
python src/app.py
```

Then open `http://127.0.0.1:5000`.

## Refresh stored data
Run the scraper and save the latest movie list into the code base:

```bash
python scripts/scrape_worst_movies.py
```

The data is stored in `data/worst_movies.json`.

### Change the host or port
To run on a different address or port, set `HOST` and `PORT` before starting the app:

```bash
HOST=0.0.0.0 PORT=8000 python src/app.py
```

On Windows PowerShell:

```powershell
$env:HOST = "0.0.0.0"
$env:PORT = "8000"
python src/app.py
```

## Notes
- The app scrapes Wikipedia's Rotten Tomatoes 0% film list.
- It provides Rotten Tomatoes search links plus YouTube and Dailymotion preview searches.

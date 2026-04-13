# Worst Movies Web App

A simple Flask web app that scrapes the lowest-rated English feature films from IMDb and provides preview links to YouTube and Dailymotion.

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

## Notes
- The app scrapes IMDb search results.
- It only includes English movies.
- Preview links are provided using YouTube and Dailymotion search results.

const MOVIES_JSON = 'data/worst_movies.json';
const searchInput = document.getElementById('search');
const ratingSelect = document.getElementById('max-rating');
const genreSelect = document.getElementById('genre-filter');
const cageCheckbox = document.getElementById('cage-filter');
const searchForm = document.getElementById('search-form');
const statusEl = document.getElementById('status');
const countEl = document.getElementById('movie-count');
const moviesEl = document.getElementById('movies');
let movies = [];

const escapeHtml = (text) =>
    String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

const isCageFilm = (movie) =>
    movie.featured || (movie.description && movie.description.includes('Nicolas Cage'));

const buildCard = (movie) => {
    const title = escapeHtml(movie.title);
    const year = escapeHtml(movie.year);
    const reviews = escapeHtml(movie.reviews);
    const rating = escapeHtml(movie.rating);
    const description = escapeHtml(movie.description);
    const genre = movie.genre && movie.genre !== 'N/A' ? escapeHtml(movie.genre) : null;
    const wikiUrl = movie.wiki_url ? escapeHtml(movie.wiki_url) : null;
    const rtUrl = escapeHtml(movie.rotten_tomatoes_url);
    const previewUrl = escapeHtml(movie.preview_url);
    const altUrl = escapeHtml(movie.alt_preview_url);

    return `
    <article class="movie-card">
      <div class="content">
        <div>
          <h2>${title}</h2>
          <div class="meta">${year} · ${reviews} reviews${genre ? ` · <span class="genre-tag">${genre}</span>` : ''}</div>
        </div>
        <div class="meta">Rotten Tomatoes score: ${rating}</div>
        <p class="description">${description}</p>
        <div class="links">
          ${wikiUrl ? `<a href="${wikiUrl}" target="_blank" rel="noreferrer">Wikipedia</a> ·` : ''}
          <a href="${rtUrl}" target="_blank" rel="noreferrer">Rotten Tomatoes</a> ·
          <a href="${previewUrl}" target="_blank" rel="noreferrer">YouTube</a> ·
          <a href="${altUrl}" target="_blank" rel="noreferrer">Dailymotion</a>
        </div>
      </div>
    </article>
  `;
};

const populateGenres = () => {
    const genreSet = new Set();
    movies.forEach((movie) => {
        if (movie.genre && movie.genre !== 'N/A') {
            movie.genre.split('/').forEach((g) => genreSet.add(g.trim()));
        }
    });
    const sorted = [...genreSet].sort();
    sorted.forEach((genre) => {
        const opt = document.createElement('option');
        opt.value = genre;
        opt.textContent = genre;
        genreSelect.appendChild(opt);
    });
};

const renderMovies = (items) => {
    if (!items.length) {
        moviesEl.innerHTML = '<p>No movies found.</p>';
        countEl.hidden = true;
        return;
    }
    moviesEl.innerHTML = items.map(buildCard).join('');
    countEl.hidden = false;
    countEl.textContent = `Showing ${items.length} movie${items.length === 1 ? '' : 's'}.`;
};

const showError = (message) => {
    statusEl.hidden = false;
    statusEl.textContent = message;
};

const loadMovies = async () => {
    try {
        const response = await fetch(MOVIES_JSON);
        if (!response.ok) {
            throw new Error(`Unable to load data: ${response.status} ${response.statusText}`);
        }
        movies = await response.json();
        populateGenres();
        applyFilters();
    } catch (error) {
        showError(error.message);
    }
};

const applyFilters = () => {
    const query = searchInput.value.trim().toLowerCase();
    const maxRating = Number(ratingSelect.value);
    const genreQuery = genreSelect.value.toLowerCase();
    const cageOnly = cageCheckbox.checked;

    const filtered = movies.filter((movie) => {
        const titleMatch = !query || movie.title.toLowerCase().includes(query);

        const ratingValue = Number(movie.rating.replace('%', ''));
        const ratingMatch = movie.featured
            ? true
            : Number.isFinite(ratingValue) && ratingValue <= maxRating;

        const genreMatch = !genreQuery || (
            movie.genre &&
            movie.genre !== 'N/A' &&
            movie.genre.toLowerCase().split('/').some((g) => g.trim() === genreQuery)
        );

        const cageMatch = !cageOnly || isCageFilm(movie);

        return titleMatch && ratingMatch && genreMatch && cageMatch;
    });

    renderMovies(filtered);
};

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    applyFilters();
});

ratingSelect.addEventListener('change', applyFilters);
genreSelect.addEventListener('change', applyFilters);
cageCheckbox.addEventListener('change', applyFilters);

loadMovies();

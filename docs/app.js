const MOVIES_JSON = 'data/worst_movies.json';
const searchInput = document.getElementById('search');
const ratingSelect = document.getElementById('max-rating');
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

const buildCard = (movie) => {
    const title = escapeHtml(movie.title);
    const year = escapeHtml(movie.year);
    const reviews = escapeHtml(movie.reviews);
    const rating = escapeHtml(movie.rating);
    const description = escapeHtml(movie.description);
    const wikiUrl = movie.wiki_url ? escapeHtml(movie.wiki_url) : null;
    const rtUrl = escapeHtml(movie.rotten_tomatoes_url);
    const previewUrl = escapeHtml(movie.preview_url);
    const altUrl = escapeHtml(movie.alt_preview_url);

    return `
    <article class="movie-card">
      <div class="content">
        <div>
          <h2>${title}</h2>
          <div class="meta">${year} · ${reviews} reviews</div>
        </div>
        <div class="meta">Rotten Tomatoes score: ${rating}</div>
        <p class="description">${description}</p>
        <div class="links">
          ${wikiUrl ? `<a href="${wikiUrl}" target="_blank" rel="noreferrer">Wikipedia page</a> ·` : ''}
          <a href="${rtUrl}" target="_blank" rel="noreferrer">Rotten Tomatoes</a> ·
          <a href="${previewUrl}" target="_blank" rel="noreferrer">YouTube preview</a> ·
          <a href="${altUrl}" target="_blank" rel="noreferrer">Dailymotion preview</a>
        </div>
      </div>
    </article>
  `;
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
        applyFilters();
    } catch (error) {
        showError(error.message);
    }
};

const applyFilters = () => {
    const query = searchInput.value.trim().toLowerCase();
    const maxRating = Number(ratingSelect.value);
    const filtered = movies.filter((movie) => {
        const titleMatch = !query || movie.title.toLowerCase().includes(query);
        const ratingValue = Number(movie.rating.replace('%', ''));
        const ratingMatch = Number.isFinite(ratingValue) && ratingValue <= maxRating;
        return titleMatch && ratingMatch;
    });
    renderMovies(filtered);
};

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    applyFilters();
});

ratingSelect.addEventListener('change', () => {
    applyFilters();
});

loadMovies();

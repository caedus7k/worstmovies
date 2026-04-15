const MOVIES_JSON = 'data/worst_movies.json';
const searchInput = document.getElementById('search');
const ratingSelect = document.getElementById('max-rating');
const genreSelect = document.getElementById('genre-filter');
const tagSelect = document.getElementById('tag-filter');
const cageCheckbox = document.getElementById('cage-filter');
const breenCheckbox = document.getElementById('breen-filter');
const searchForm = document.getElementById('search-form');
const statusEl = document.getElementById('status');
const countEl = document.getElementById('movie-count');
const moviesEl = document.getElementById('movies');
let movies = [];

const TAG_META = {
    'so-bad-its-good': { label: 'So bad it\'s good', emoji: '🍿' },
    'razzie-winner': { label: 'Razzie winner', emoji: '🏆' },
    'b-movie': { label: 'B movie', emoji: '🎬' },
    'neil-breen': { label: 'Neil Breen', emoji: '📼' },
    'tommy-wiseau': { label: 'Tommy Wiseau', emoji: '🎥' },
};

const escapeHtml = (text) =>
    String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

const isCageFilm = (movie) =>
    movie.featured || (movie.description && movie.description.includes('Nicolas Cage'));

const isBreenFilm = (movie) =>
    movie.tags && movie.tags.includes('neil-breen');

const buildTagBadges = (tags) => {
    if (!tags || !tags.length) return '';
    return tags.map((tag) => {
        const meta = TAG_META[tag];
        if (!meta) return '';
        return `<span class="tag-badge tag-${tag}">${meta.emoji} ${meta.label}</span>`;
    }).join('');
};

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
    const tagBadges = buildTagBadges(movie.tags);

    return `
    <article class="movie-card">
      <div class="content">
        <div>
          <h2>${title}</h2>
          <div class="meta">${year} · ${reviews} reviews${genre ? ` · <span class="genre-tag">${genre}</span>` : ''}</div>
        </div>
        ${tagBadges ? `<div class="tag-badges">${tagBadges}</div>` : ''}
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
    [...genreSet].sort().forEach((genre) => {
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
    const tagQuery = tagSelect.value;
    const cageOnly = cageCheckbox.checked;
    const breenOnly = breenCheckbox.checked;

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

        const tagMatch = !tagQuery || (movie.tags && movie.tags.includes(tagQuery));

        const cageMatch = !cageOnly || isCageFilm(movie);
        const breenMatch = !breenOnly || isBreenFilm(movie);

        return titleMatch && ratingMatch && genreMatch && tagMatch && cageMatch && breenMatch;
    });

    renderMovies(filtered);
};

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    applyFilters();
});

ratingSelect.addEventListener('change', applyFilters);
genreSelect.addEventListener('change', applyFilters);
tagSelect.addEventListener('change', applyFilters);
cageCheckbox.addEventListener('change', applyFilters);
breenCheckbox.addEventListener('change', applyFilters);

loadMovies();

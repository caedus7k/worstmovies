# JavaScript Pro

Source: Jeffallan/claude-skills (javascript-pro, v1.1.0) — MIT License

## When to Use
Invoke when writing, debugging, or refactoring the vanilla JavaScript in `docs/app.js` or any new JS files in this project.

---

## Core Rules

### Must Do
- Use ES2023+ syntax exclusively (`const`/`let`, arrow functions, optional chaining)
- `async`/`await` for all async operations; wrap in `try/catch`
- Explicit error handling — surface errors to the UI, never swallow silently
- Use `escapeHtml()` or equivalent before injecting any user-supplied or external data into the DOM
- JSDoc comments for non-obvious functions
- ESM imports/exports in any new module files

### Must Not Do
- Use `var` (use `const`/`let`)
- Use callback-based async patterns (use `async`/`await`)
- Leave unhandled Promise rejections
- Perform synchronous blocking operations on the main thread
- Inject unsanitized strings into `innerHTML`

---

## Modern Syntax Quick Reference

```javascript
// Optional chaining & nullish coalescing
const name = movie?.title ?? 'Unknown';
const rating = movie?.rating ?? 'N/A';

// Logical assignment
options.maxRating ??= 70;

// Array methods
const last = items.at(-1);
const sorted = [...items].toSorted((a, b) => a.title.localeCompare(b.title));

// Object destructuring
const { title, year, rating, wiki_url: wikiUrl = null } = movie;

// Template literals
const card = `<article class="movie-card"><h2>${escapeHtml(title)}</h2></article>`;
```

---

## Async / Fetch Patterns

```javascript
// Basic fetch with error handling
const loadMovies = async () => {
  try {
    const response = await fetch('data/worst_movies.json');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    showError(error.message);
    return [];
  }
};

// Fetch with timeout using AbortController
const fetchWithTimeout = async (url, ms = 10_000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(id);
  }
};

// Parallel requests
const [movies, config] = await Promise.all([
  fetch('data/worst_movies.json').then(r => r.json()),
  fetch('data/config.json').then(r => r.json()),
]);
```

---

## XSS Prevention (critical for this project)

```javascript
// The escapeHtml() function in docs/app.js — always use it before innerHTML
const escapeHtml = (text) =>
  String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

// GOOD — safe
card.innerHTML = `<h2>${escapeHtml(movie.title)}</h2>`;

// GOOD — also safe (textContent never executes HTML)
const h2 = document.createElement('h2');
h2.textContent = movie.title;

// BAD — XSS risk if movie.title comes from an untrusted source
card.innerHTML = `<h2>${movie.title}</h2>`;
```

---

## DOM Patterns

```javascript
// Safe card construction (pattern from docs/app.js)
const buildCard = (movie) => {
  const title = escapeHtml(movie.title);
  const year = escapeHtml(movie.year);
  const rating = escapeHtml(movie.rating);
  return `
    <article class="movie-card">
      <h2>${title} (${year})</h2>
      <p>Score: ${rating}</p>
    </article>
  `;
};

// Efficient batch render — set innerHTML once, not in a loop
moviesEl.innerHTML = items.map(buildCard).join('');

// Event delegation — one listener for many cards
moviesEl.addEventListener('click', (event) => {
  const card = event.target.closest('.movie-card');
  if (card) handleCardClick(card);
});

// Debounce for search inputs
const debounce = (fn, wait) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
};
searchInput.addEventListener('input', debounce(applyFilters, 300));
```

---

## Error Handling Patterns

```javascript
// Custom error class
class AppError extends Error {
  constructor(message, cause = null) {
    super(message);
    this.name = 'AppError';
    this.cause = cause;
  }
}

// Retry with exponential back-off
const retryFetch = async (url, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetchWithTimeout(url);
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise(r => setTimeout(r, 500 * 2 ** i));
    }
  }
};
```

---

## Quick Reference

| Pattern | When to Use |
|---------|-------------|
| `?.` optional chaining | Accessing potentially-null properties |
| `??` nullish coalescing | Default values for `null`/`undefined` |
| `Promise.all()` | Parallel fetches, fail-fast |
| `Promise.allSettled()` | Parallel fetches, handle each result |
| `AbortController` | Cancellable fetch / timeout |
| `escapeHtml()` | Before any `.innerHTML` injection |
| `textContent` | Set plain text — always safe |
| `closest()` | Event delegation |
| `toSorted()` / `toReversed()` | Non-mutating array transforms |

# Web Design & HTML Best Practices

Source: Jeffallan/claude-skills (fullstack-guardian v1.1.1, frontend-patterns) — MIT License  
Adapted for: HTML + CSS + vanilla JS static frontend (`docs/`) and Flask Jinja2 templates (`src/templates/`)

## When to Use
Invoke when working on `docs/index.html`, `src/templates/index.html`, CSS styling, layout, accessibility, or UI/UX improvements.

---

## HTML Structure

### Semantic HTML
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Browse the worst-rated movies of all time">
  <title>Worst Movies</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <h1>Worst Movies Ever Made</h1>
  </header>

  <main>
    <section aria-label="Search and filter">
      <form id="search-form" role="search">
        <label for="search">Search movies</label>
        <input
          id="search"
          type="search"
          name="search"
          placeholder="e.g. Plan 9"
          autocomplete="off"
        >
        <label for="max-rating">Max Rotten Tomatoes score</label>
        <select id="max-rating" name="max_score">
          <option value="10">10%</option>
          <option value="30">30%</option>
          <option value="50">50%</option>
          <option value="70" selected>70%</option>
        </select>
        <button type="submit">Search</button>
      </form>
    </section>

    <p id="status" role="alert" hidden></p>
    <p id="movie-count" aria-live="polite" hidden></p>

    <section id="movies" aria-label="Movie results">
      <!-- Cards rendered here by JS -->
    </section>
  </main>
</body>
</html>
```

### Semantic Element Usage

| Element | Use for |
|---------|---------|
| `<header>` | Page/section heading area |
| `<main>` | Primary page content (one per page) |
| `<nav>` | Navigation links |
| `<section>` | Thematically grouped content |
| `<article>` | Self-contained content (movie cards) |
| `<footer>` | Page/section footer |
| `<figure>` / `<figcaption>` | Images with captions |

---

## Accessibility (a11y)

```html
<!-- Form labels — always associate with inputs -->
<label for="search">Search movies</label>
<input id="search" type="search" ...>

<!-- ARIA live regions for dynamic content -->
<p id="movie-count" aria-live="polite" hidden></p>
<p id="status" role="alert" hidden></p>   <!-- role="alert" announces immediately -->

<!-- Icon buttons need accessible names -->
<button aria-label="Clear search">✕</button>

<!-- Cards: use article with a heading -->
<article class="movie-card">
  <h2>Plan 9 from Outer Space</h2>
  ...
</article>

<!-- External links: warn screen readers -->
<a href="https://rottentomatoes.com/..." target="_blank" rel="noreferrer">
  Rotten Tomatoes
  <span class="sr-only">(opens in new tab)</span>
</a>
```

### Screen-reader-only helper class
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## CSS Best Practices

```css
/* Custom properties for consistency */
:root {
  --color-bg: #1a1a2e;
  --color-surface: #16213e;
  --color-accent: #e94560;
  --color-text: #eaeaea;
  --color-muted: #a0a0b0;
  --radius: 8px;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
}

/* Fluid typography */
body {
  font-size: clamp(1rem, 1.5vw, 1.125rem);
  line-height: 1.6;
  color: var(--color-text);
  background: var(--color-bg);
}

/* Responsive layout with CSS Grid */
.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

/* Focus styles — never remove, only enhance */
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* Mobile-first */
.movie-card {
  padding: var(--spacing-md);
  border-radius: var(--radius);
  background: var(--color-surface);
}

@media (min-width: 768px) {
  .movie-card {
    padding: var(--spacing-lg);
  }
}
```

---

## Jinja2 Template Patterns (Flask)

```html
{# src/templates/index.html — safe output with |e (escape) filter #}
{% for movie in movies %}
<article class="movie-card">
  <h2>{{ movie.title | e }}</h2>
  <p class="meta">{{ movie.year | e }} · {{ movie.reviews | e }} reviews</p>
  <p class="score">Rotten Tomatoes: {{ movie.rating | e }}</p>
  <p>{{ movie.description | e }}</p>
  <nav class="links" aria-label="External links for {{ movie.title | e }}">
    {% if movie.wiki_url %}
    <a href="{{ movie.wiki_url | e }}" target="_blank" rel="noreferrer">Wikipedia</a>
    {% endif %}
    <a href="{{ movie.rotten_tomatoes_url | e }}" target="_blank" rel="noreferrer">RT</a>
    <a href="{{ movie.preview_url | e }}" target="_blank" rel="noreferrer">YouTube</a>
  </nav>
</article>
{% else %}
<p>No movies found{% if search %} for "{{ search | e }}"{% endif %}.</p>
{% endfor %}

{% if error %}
<p class="error" role="alert">Error: {{ error | e }}</p>
{% endif %}
```

---

## Performance

```html
<!-- Preload critical assets -->
<link rel="preload" href="app.js" as="script">

<!-- Defer non-critical JS -->
<script src="app.js" defer></script>
<!-- or for modules: -->
<script type="module" src="app.js"></script>  <!-- modules are deferred by default -->

<!-- Lazy-load images -->
<img src="poster.jpg" alt="Movie poster" loading="lazy" decoding="async">
```

---

## Core Constraints

### Must Do
- Use semantic HTML elements (`<article>`, `<section>`, `<nav>`, etc.)
- Associate every `<label>` with its `<input>` via `for`/`id`
- Escape all external data in templates (`| e` in Jinja2, `escapeHtml()` in JS)
- Provide `alt` text for meaningful images
- Add `rel="noreferrer"` on `target="_blank"` links
- Test with keyboard-only navigation
- Use `aria-live` for dynamically updated regions

### Must Not Do
- Use `<div>` or `<span>` when a semantic element fits
- Remove `:focus` styles
- Use inline styles for layout (use CSS classes)
- Hardcode colours without CSS custom properties
- Block rendering with synchronous `<script>` in `<head>`

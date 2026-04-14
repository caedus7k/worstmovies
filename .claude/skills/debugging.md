---
name: debugging-wizard
description: Parses error messages, traces execution flow through stack traces, correlates log entries to identify failure points, and applies systematic hypothesis-driven methodology to isolate and resolve bugs. Use when investigating errors, analyzing stack traces, finding root causes of unexpected behavior, troubleshooting crashes, or performing log analysis, error investigation, or root cause analysis.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  domain: quality
  triggers: debug, error, bug, exception, traceback, stack trace, troubleshoot, not working, crash, fix issue
  role: specialist
  scope: analysis
  output-format: analysis
  related-skills: test-master, fullstack-guardian, monitoring-expert
---

# Debugging Wizard

Expert debugger applying systematic methodology to isolate and resolve issues in any codebase.

## Core Workflow

1. **Reproduce** - Establish consistent reproduction steps
2. **Isolate** - Narrow down to smallest failing case
3. **Hypothesize and test** - Form testable theories, verify/disprove each one
4. **Fix** - Implement and verify solution
5. **Prevent** - Add tests/safeguards against regression

## Constraints

### MUST DO
- Reproduce the issue first
- Gather complete error messages and stack traces
- Test one hypothesis at a time
- Document findings for future reference
- Add regression tests after fixing
- Remove all debug code before committing

### MUST NOT DO
- Guess without testing
- Make multiple changes at once
- Skip reproduction steps
- Assume you know the cause
- Debug in production without safeguards
- Leave `print()`/`console.log()`/`debugger` statements in committed code

---

## Python Debugging

### pdb (built-in)
```bash
python -m pdb src/app.py        # launch debugger
# inside pdb:
# b 42          — set breakpoint at line 42
# b app.index   — set breakpoint on function
# n             — step over
# s             — step into
# c             — continue to next breakpoint
# p some_var    — print variable
# pp some_dict  — pretty-print
# bt            — print full traceback
# q             — quit
```

### Inline breakpoint (Python 3.7+)
```python
def scrape_worst_movies(limit, max_score):
    movies = parse_wikipedia_0_percent_page()
    breakpoint()   # drops into pdb here; remove before commit
    ...
```

### Inspecting requests/responses
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# urllib3 will log all HTTP request/response details

# Or manually:
response = requests.get(url, headers=HEADERS, timeout=30)
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body (first 500): {response.text[:500]}")
```

### Flask debug mode
```bash
FLASK_DEBUG=1 python src/app.py
# Enables interactive debugger in browser on unhandled exceptions
# NEVER enable in production
```

### Common Python errors in this project

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `AttributeError: 'NoneType' has no attribute ...` | `soup.find()` returned `None` | Guard with `if tag is not None:` |
| `requests.exceptions.Timeout` | Wikipedia slow or unreachable | Increase timeout or retry |
| `RuntimeError: Could not locate table` | Wikipedia changed page structure | Inspect live HTML, update selector |
| `KeyError: 'href'` | Anchor tag has no href | Use `tag.get("href", "")` not `tag["href"]` |

---

## JavaScript Debugging

### Browser DevTools
```javascript
// Pause execution at a specific line
debugger;   // remove before commit

// Inspect variables
console.log({ movies, filtered });   // object shorthand shows keys

// Group related logs
console.group("applyFilters");
console.log("query:", query);
console.log("maxRating:", maxRating);
console.groupEnd();
```

### Common JS errors in this project

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `TypeError: Cannot read properties of undefined` | `movie` is undefined in `buildCard` | Check `movies` is an array before mapping |
| `SyntaxError: Unexpected token '<'` | `fetch()` got HTML (404 page) instead of JSON | Check `response.ok` before `.json()` |
| `Failed to fetch` | CORS, network error, or wrong path | Check browser Network tab; verify JSON path |
| Cards showing `&lt;` etc. | Double-escaping | Escape only once, at render time |

### Network debugging
```javascript
// Log every fetch response
const origFetch = fetch;
window.fetch = async (...args) => {
  const res = await origFetch(...args);
  console.log(`[fetch] ${args[0]} → ${res.status}`);
  return res;
};
```

---

## Git Bisect (regression hunting)

```bash
git bisect start
git bisect bad                   # current commit is broken
git bisect good v1.0.0           # last known good tag/SHA
# Git checks out midpoint — test manually or run:
git bisect run pytest tests/     # auto-bisect with test command
# Git identifies the first bad commit
git bisect reset                 # return to HEAD
```

---

## Output Templates

When debugging, provide:
1. **Root Cause**: What specifically caused the issue
2. **Evidence**: Stack trace, logs, or test that proves it
3. **Fix**: Code change that resolves it
4. **Prevention**: Test or safeguard to prevent recurrence

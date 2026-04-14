# GitHub Actions & CI/CD

Source: Jeffallan/claude-skills (devops-engineer v1.1.1, github-actions reference) — MIT License  
Adapted for: Python Flask + vanilla JS project

## When to Use
Invoke when creating or modifying GitHub Actions workflows (`.github/workflows/*.yml`), setting up CI/CD, or configuring automated testing/deployment for this project.

---

## Python + JS CI Workflow (tailored for this repo)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, "claude/*"]
  pull_request:
    branches: [main]

jobs:
  test-python:
    name: Python tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov pytest-mock requests-mock

      - name: Run tests
        run: pytest --cov=src --cov-report=term-missing --cov-fail-under=80

      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check src/ scripts/

  test-js:
    name: JavaScript tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
        if: hashFiles('package.json') != ''

      - name: Install JS dependencies
        run: npm ci
        if: hashFiles('package.json') != ''

      - name: Run JS tests
        run: npm test
        if: hashFiles('package.json') != ''

  security-scan:
    name: Security scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Scan with pip-audit
        run: |
          pip install pip-audit
          pip-audit -r requirements.txt
```

---

## Dependency Caching

```yaml
# Python pip cache
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip          # caches ~/.cache/pip

# npm cache
- uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: npm          # caches ~/.npm

# Manual cache (for non-standard paths)
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

---

## Secrets & Environment Variables

```yaml
# In workflow file — reference GitHub Secrets
env:
  FLASK_SECRET_KEY: ${{ secrets.FLASK_SECRET_KEY }}

# Pass to a step
- name: Deploy
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
  run: ./deploy.sh
```

**Never** put secret values directly in workflow YAML. Add them at:  
Settings → Secrets and variables → Actions → New repository secret

---

## Common Workflow Patterns

### Matrix Builds
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
    os: [ubuntu-latest, macos-latest]
runs-on: ${{ matrix.os }}
```

### Conditional Steps
```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

### Reusable Workflows
```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
```

### Upload Test Reports
```yaml
- name: Run tests
  run: pytest --junitxml=test-results.xml

- name: Upload results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results
    path: test-results.xml
```

---

## Quick Reference

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | v4 | Clone repository |
| `actions/setup-python` | v5 | Install Python + pip cache |
| `actions/setup-node` | v4 | Install Node.js + npm cache |
| `actions/cache` | v4 | Manual dependency caching |
| `actions/upload-artifact` | v4 | Save build/test artifacts |

## Core Constraints
- Always pin action versions (`@v4` not `@latest`)
- Never store secrets in workflow YAML — use GitHub Secrets
- Run tests before any deployment step
- Use `if: always()` on artifact upload so reports are saved even on failure
- Separate jobs for Python and JS to allow parallel execution

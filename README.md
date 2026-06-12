# OpenReview

> An open-source AI framework for structured idea and project proposal reviews using configurable expert agents.

[![CI](https://github.com/corykim2/OpenReview/actions/workflows/python.yml/badge.svg)](https://github.com/corykim2/OpenReview/actions/workflows/python.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## What is OpenReview?

OpenReview evaluates your idea or project proposal through five independent AI-powered expert agents — each reviewing from a distinct perspective:

| Agent | Focus |
|---|---|
| **TechnologyReviewer** | Architecture, feasibility, security, stack choices |
| **BusinessReviewer** | Revenue model, unit economics, go-to-market |
| **MarketReviewer** | Market size, competition, positioning |
| **UXReviewer** | User journey, accessibility, onboarding |
| **RiskReviewer** | Compliance, failure modes, legal exposure |

Each agent reads a prompt template, calls an AI provider, and returns a structured score with strengths, weaknesses, and actionable recommendations. A final Markdown report aggregates all results.

**No OpenAI API key required** — a built-in `MockProvider` makes the framework fully runnable offline.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/corykim2/OpenReview.git
cd OpenReview

# Install in editable mode (includes dev tools)
pip install -e ".[dev]"

# OR minimal install (runtime only)
pip install -e .

# Optional: add OpenAI support
pip install -e ".[openai]"
```

---

## Quick Start

### 1. Run with the included sample (no API key needed)

```bash
python main.py --input examples/sample.yaml
```

### 2. Run with your own project file

```yaml
# my_project.yaml
title: My Awesome Startup

description: |
  A platform that does something genuinely useful.

target_users:
  - small business owners
  - freelancers

business_model: subscription
```

```bash
python main.py --input my_project.yaml
```

The report is saved to `reports/output.md`.

### 3. Use the OpenAI provider

```bash
export OPENAI_API_KEY=sk-...
python main.py --input examples/sample.yaml --provider openai
```

Or set `provider: openai` in `config.yaml`.

### 4. All CLI options

```
usage: openreview [-h] --input FILE [--config FILE] [--provider {openai,mock}]
                  [--output-dir DIR] [--verbose]

options:
  --input FILE, -i FILE       Path to the YAML or JSON project input file
  --config FILE, -c FILE      Path to config.yaml (default: config.yaml)
  --provider {openai,mock}    Override AI provider
  --output-dir DIR            Override output directory
  --verbose, -v               Enable debug logging
```

---

## Input Format

Both **YAML** and **JSON** are supported.

### YAML example

```yaml
title: AI Resume Builder

description: |
  An AI-powered platform that generates personalised,
  ATS-optimised resumes from a structured profile.

target_users:
  - university students
  - job seekers

business_model: freemium subscription
```

### JSON example

```json
{
  "title": "AI Resume Builder",
  "description": "An AI-powered resume generation platform.",
  "target_users": ["students", "job seekers"],
  "business_model": "freemium subscription"
}
```

Required fields: `title`, `description`. All other fields are optional but improve review quality.

---

## Sample Output

```markdown
# OpenReview Report

**Project:** AI Resume Builder
**Generated:** 2026-06-12 09:00 UTC
**Reviewers:** 5

## Overall Score 🟢

[████████████████░░░░] 6.8/10

> **6.8 / 10** — averaged across 5 reviewers.

## Score Summary

| Reviewer   | Score | Rating |
|------------|-------|--------|
| Technology | 7.5   | 🟢     |
| Business   | 6.8   | 🟢     |
| Market     | 7.2   | 🟢     |
| UX         | 6.5   | 🟡     |
| Risk       | 5.9   | 🟡     |
| **Overall**| **6.8**| 🟢    |
```

---

## Project Structure

```
OpenReview/
├── src/
│   ├── core/
│   │   ├── models.py          # Project, ReviewResult, ReportData dataclasses
│   │   ├── config.py          # AppConfig + load_config()
│   │   └── base_reviewer.py   # Abstract BaseReviewer
│   ├── providers/
│   │   ├── base_provider.py   # AIProvider interface
│   │   ├── openai_provider.py # OpenAI Chat Completions
│   │   └── mock_provider.py   # Offline deterministic provider
│   ├── reviewers/
│   │   ├── technology.py
│   │   ├── business.py
│   │   ├── market.py
│   │   ├── ux.py
│   │   └── risk.py
│   └── report/
│       └── generator.py       # Markdown report renderer
├── prompts/                   # Prompt templates (one per reviewer)
├── examples/                  # Sample project input files
├── tests/
│   ├── conftest.py
│   ├── test_reviewers.py
│   ├── test_report.py
│   └── test_provider.py
├── reports/                   # Generated reports
├── docs/
│   └── architecture.md
├── .github/workflows/
│   └── python.yml             # CI: lint + test + type-check
├── main.py                    # CLI entry point
├── config.yaml
├── pyproject.toml
└── requirements.txt
```

---

## Configuration

Edit `config.yaml` to change defaults:

```yaml
provider: mock          # "mock" or "openai"
model: gpt-4.1          # OpenAI model (used when provider=openai)
output: reports/        # Report output directory
prompts_dir: prompts/   # Prompt template directory
temperature: 0.7        # LLM sampling temperature
max_tokens: 1024        # Max completion tokens
```

---

## Extending OpenReview

### Add a new reviewer in 5 steps

1. Create `prompts/finance.md` with `{{PROJECT_CONTEXT}}` placeholder.
2. Create `src/reviewers/finance.py` extending `BaseReviewer`.
3. Export it from `src/reviewers/__init__.py`.
4. Add it to the reviewers list in `main.py`.
5. Add a mock response entry in `src/providers/mock_provider.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for a full step-by-step walkthrough.

---

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run a specific test file
pytest tests/test_reviewers.py -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

---

## Roadmap

- [ ] **v0.2** — HTML report output option
- [ ] **v0.2** — Parallel reviewer execution (asyncio)
- [ ] **v0.3** — Anthropic Claude provider
- [ ] **v0.3** — Interactive reviewer weight configuration
- [ ] **v0.4** — Web UI (FastAPI + React)
- [ ] **v0.5** — Review history and comparison across iterations
- [ ] **v1.0** — Plugin system for community-contributed reviewers

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Commit convention
- Pull request guidelines
- How to add a new reviewer

---

## License

MIT — see [LICENSE](LICENSE).

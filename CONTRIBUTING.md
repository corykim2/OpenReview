# Contributing to OpenReview

Thank you for considering a contribution to OpenReview!  This document explains how to get started, what our code standards are, and how to submit changes.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Convention](#commit-convention)
- [Code Style](#code-style)
- [Testing](#testing)
- [Adding a New Reviewer](#adding-a-new-reviewer)

---

## Code of Conduct

All contributors are expected to uphold our Code of Conduct: be respectful, constructive, and inclusive.  Harassment of any kind will not be tolerated.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/OpenReview.git
   cd OpenReview
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/corykim2/OpenReview.git
   ```

---

## Development Setup

### Prerequisites

- Python 3.12 or higher
- `pip`

### Install in editable mode with dev extras

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Verify the setup

```bash
pytest
python main.py --input examples/sample.yaml
```

---

## Issue Guidelines

Before opening an issue:

1. Search existing issues to avoid duplicates.
2. Use the correct template:
   - **Bug Report** — describe the problem, expected behaviour, and steps to reproduce.
   - **Feature Request** — describe the use case and why the feature is valuable.
3. Include the Python version and OS in bug reports.
4. Provide a minimal reproducible example where possible.

---

## Pull Request Guidelines

1. **One PR per concern** — keep scope small and focused.
2. **Branch naming**:
   - `feat/short-description` for new features
   - `fix/short-description` for bug fixes
   - `docs/short-description` for documentation changes
   - `refactor/short-description` for refactoring
3. **Base your PR on `main`** (never `develop` or a feature branch unless coordinated).
4. Fill in the PR template completely — describe *what* and *why*, not just *how*.
5. All CI checks must pass before a PR will be reviewed.
6. Squash-merge is preferred; keep the commit history clean.
7. Every user-facing change requires a test.  PRs without tests for new behaviour will not be merged.

---

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

### Types

| Type       | When to use                                         |
|------------|-----------------------------------------------------|
| `feat`     | A new feature                                       |
| `fix`      | A bug fix                                           |
| `docs`     | Documentation only                                  |
| `style`    | Formatting, whitespace (no logic change)            |
| `refactor` | Code restructuring (no feature/fix)                 |
| `test`     | Adding or updating tests                            |
| `chore`    | Build process, CI, dependencies                     |
| `perf`     | Performance improvement                             |

### Examples

```
feat(reviewers): add FinanceReviewer agent
fix(provider): handle empty OpenAI response gracefully
docs(readme): add installation badge
test(report): cover empty results edge case
chore(ci): upgrade actions/setup-python to v5
```

---

## Code Style

- **Formatter**: [black](https://black.readthedocs.io/) with `line-length = 100`
  ```bash
  black src/ tests/ main.py
  ```
- **Linter**: [pylint](https://pylint.readthedocs.io/) with minimum score 8.0
  ```bash
  pylint src/ main.py
  ```
- **Type checking**: [mypy](https://mypy.readthedocs.io/) in strict mode
  ```bash
  mypy src/ main.py
  ```
- **Type hints**: required on all public functions and methods.
- **Docstrings**: use Google-style for all public classes and functions.
- **Comments**: only when the *why* is non-obvious.

---

## Testing

- Tests live in `tests/` and follow the `test_<module>.py` naming convention.
- We target **≥ 80% line coverage**.
- Run the full test suite:
  ```bash
  pytest
  ```
- Run with coverage report:
  ```bash
  pytest --cov=src --cov-report=html
  open htmlcov/index.html
  ```

---

## Adding a New Reviewer

OpenReview is designed for extension.  Adding a new reviewer requires **zero changes to existing code**:

1. **Create a prompt template** in `prompts/`:
   ```
   prompts/finance.md
   ```
   Include `{{PROJECT_CONTEXT}}` as a placeholder and instruct the AI to return the standard JSON schema.

2. **Create the reviewer class** in `src/reviewers/`:
   ```python
   # src/reviewers/finance.py
   from src.core.base_reviewer import BaseReviewer

   class FinanceReviewer(BaseReviewer):
       reviewer_name = "Finance"
       prompt_file = "finance.md"

       def get_focus_areas(self) -> list[str]:
           return ["Revenue projections", "Burn rate", "Fundraising strategy"]
   ```

3. **Export from `__init__.py`**:
   ```python
   # src/reviewers/__init__.py
   from src.reviewers.finance import FinanceReviewer
   ```

4. **Add to `main.py`** inside `run_review()`:
   ```python
   FinanceReviewer(provider=provider, prompts_dir=config.prompts_dir),
   ```

5. **Add a mock response** to `src/providers/mock_provider.py` under `_MOCK_RESPONSES["finance"]`.

6. **Write tests** in `tests/test_reviewers.py`.

That's it — no existing files need modification.

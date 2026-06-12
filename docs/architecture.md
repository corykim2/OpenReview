# OpenReview Architecture

## Overview

OpenReview is a CLI-driven, multi-agent AI review framework.  A single project proposal passes through five independent Reviewer Agents that each evaluate it from a distinct expert perspective.  Their results are aggregated into a single Markdown report.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (main.py)                        │
│  --input sample.yaml  --provider mock  --output-dir reports/ │
└──────────────────────────┬──────────────────────────────────┘
                           │ load + validate
                           ▼
                    ┌──────────────┐
                    │   Project    │  (dataclass — parsed input)
                    └──────┬───────┘
                           │ passed to each reviewer
          ┌────────────────┼──────────────────────┐
          │                │                      │
          ▼                ▼                      ▼
  ┌───────────────┐ ┌────────────┐  … ┌───────────────┐
  │TechnologyReview│ │BusinessReview│   │  RiskReviewer │
  │  (BaseReviewer)│ │(BaseReviewer)│   │(BaseReviewer) │
  └───────┬───────┘ └─────┬──────┘     └──────┬────────┘
          │               │                    │
          │ loads prompts/<name>.md             │
          │ injects {{PROJECT_CONTEXT}}         │
          │               │                    │
          └───────────────┴────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  AIProvider  │  (interface)
                    └──────┬──────┘
               ┌───────────┴────────────┐
               ▼                        ▼
        ┌─────────────┐         ┌───────────────┐
        │ OpenAIProvider│       │  MockProvider  │
        │ (gpt-4.1)    │       │ (offline/test) │
        └─────────────┘         └───────────────┘
                           │
                    ┌──────▼──────┐
                    │ ReviewResult │  (dataclass per reviewer)
                    └──────┬──────┘
                           │ all results collected
                    ┌──────▼──────┐
                    │  ReportData  │  (project + all results)
                    └──────┬──────┘
                           │
                  ┌────────▼─────────┐
                  │  ReportGenerator  │
                  └────────┬─────────┘
                           │ writes
                    reports/output.md
```

## Key Design Decisions

### Open/Closed Principle
New reviewers can be added without modifying `BaseReviewer`, `ReportGenerator`, or `main.py`.  Only two things are needed: a new `*Reviewer` subclass and a prompt template file.

### Dependency Injection
`AIProvider` is injected into every `BaseReviewer`.  This makes provider-switching (e.g. OpenAI → Anthropic) a single-line config change, and makes unit testing trivial via `MockProvider`.

### Prompt Templates as Plain Text Files
Prompts are stored in `prompts/*.md` rather than hardcoded strings.  This enables non-engineers to iterate on prompt quality without touching Python code.

### Graceful Degradation
If the AI returns malformed JSON, `BaseReviewer._parse_response` falls back to a neutral score (5.0) and uses the raw text as the summary — no crash, no data loss.

### No API Key Required
`MockProvider` ships deterministic responses keyed on reviewer name keywords.  The project is fully runnable offline for demos, onboarding, and CI environments without any secrets.

# Project Collaboration Guide

## Startup Routine

Before starting any task in this repository:

1. Read this file completely.
2. Read `PROJECT-CONTEXT.md` completely.
3. Run `git status -sb` before editing.
4. Inspect the relevant source, tests, documentation, and generated artifacts.
5. Preserve unrelated user changes and all source data.

## Project Scope

This repository is a reproducible Python analytics project for diagnosing Olist
Brazilian marketplace operations and identifying growth opportunities. The
core analysis covers customers, RFM, orders, products, categories, sellers,
payments, delivery performance, reviews, and geography.

Do not claim advertising ROI, campaign causality, accounting profit, or funnel
conversion from this dataset. It does not contain advertising exposure, spend,
product cost, commission, or browsing-event data.

## Environment and Commands

The primary development environment is Windows, PowerShell, VS Code, and a
project-local Python virtual environment.

Create and activate the environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Run the workflow from the repository root:

```powershell
python scripts/run_pipeline.py
python scripts/run_analysis.py
python scripts/run_dashboard.py
```

Run tests:

```powershell
python -m pytest -q
```

Optional quality checks:

```powershell
python -m black --check src scripts tests
isort --check-only src scripts tests
python -m flake8 src scripts tests
python -m mypy src
```

Open the generated dashboard:

```powershell
Start-Process .\outputs\dashboard.html
```

## Architecture Rules

- Keep the nine source CSV files unchanged in `data/raw/`.
- Use paths relative to the project root; never add machine-specific absolute
  paths to code or documentation.
- Put reusable processing and analysis logic in `src/olist_analysis/`.
- Keep `scripts/` as thin orchestration entry points.
- Treat `data/processed/` and generated metric CSVs as reproducible artifacts.
- Keep metric definitions and cleaning rules explicit in `docs/`.
- Preserve delivered orders as the completed-order baseline unless a documented
  analysis explicitly requires another population.
- Keep filenames, module names, variables, functions, and Git commit messages
  in English.
- Keep code comments and docstrings in Simplified Chinese while preserving
  English technical terms, identifiers, field names, and API names.
- Keep public-facing README, methodology documents, reports, chart titles, and
  dashboard labels in Simplified Chinese while preserving English filenames,
  code identifiers, and source-data values.
- Use unnumbered level-1 Markdown titles, sequential decimal numbering for
  level-2 sections, and hierarchical numbering for level-3 sections in all
  public-facing Markdown documents.
- Do not silently change business definitions. Update the relevant docs, tests,
  report, dashboard, and `PROJECT-CONTEXT.md` together.

## Code Standards

- Support Python 3.10 or newer.
- Follow PEP 8 and the tooling configured in `pyproject.toml`.
- Use Black with an 88-character line length and isort's Black profile.
- Add type hints to new reusable functions where practical.
- Prefer small functions with explicit inputs and returned values.
- Use `pathlib.Path` for filesystem paths.
- Coerce or validate malformed source values explicitly; do not hide data
  quality problems with broad exception handling.
- Avoid row-by-row pandas operations when a clear vectorized solution exists.
- Add or update tests for changes to transformations, joins, metric logic, and
  output schemas.
- Use concise docstrings and comments to explain business rules and non-obvious
  decisions, not syntax.

## Data and Git Safety

- Never commit `.venv/`, raw CSVs, processed CSVs, SQLite databases, caches, or
  other large reproducible artifacts excluded by `.gitignore`.
- Before committing, run `git status --short` and verify no source data or
  secrets are staged.
- Do not delete or overwrite raw data.
- Do not use destructive Git commands such as `git reset --hard` unless the user
  explicitly requests and confirms the exact action.
- Keep version-controlled presentation artifacts such as the README, analysis
  report, dashboard HTML, SVG charts, and dashboard preview image current when
  their source metrics change.

## Context Maintenance

- `PROJECT-CONTEXT.md` is the authoritative handoff snapshot for future Codex
  sessions.
- Update it after a material phase, feature, important modification, technical
  decision, or discovery of an important issue.
- After code changes, decide whether project status, current work, decisions,
  issues, files, or next steps changed. If so, update the context in the same
  task.
- Record durable facts and actionable state only. Do not record chat history,
  transient command output, or one-off progress narration.
- Do not delete `AGENTS.md` or `PROJECT-CONTEXT.md` until the user explicitly
  confirms the project is complete and asks for cleanup.

# Project Context

Last updated: 2026-08-31

## Project Goal

Build a portfolio-quality, reproducible analytics project that converts the
nine public Olist Brazilian e-commerce CSV datasets into reliable analytical
marts, an operations dashboard, a business diagnosis, and prioritized customer,
seller, category, logistics, and growth actions.

## Current Status

The first complete end-to-end version is operational. The environment,
processing pipeline, analytical outputs, automated tests, report, dashboard,
documentation, Git repository, and GitHub remote are configured. The GitHub
presentation has been upgraded locally with a detailed README and dashboard
preview.

After the context files are committed, the local Git tracking state will show
`main` two commits ahead of `origin/main`: the GitHub presentation upgrade and
the persistent project-context update. Previous push attempts ended with GitHub
HTTPS connection timeouts/resets. The local commits are safe.

## Completed

- Created the standard project structure for source data, processed data,
  documentation, reusable source code, scripts, tests, and outputs.
- Renamed project documents and artifacts to English filenames.
- Implemented ingestion and cleaning for all nine source CSV files.
- Built 13 SQLite tables, including cleaned sources and order, item, user, and
  seller analytical marts.
- Added 12 pipeline data-quality checks.
- Implemented monthly GMV/orders, category, customer RFM, state, seller,
  delivery, and review analyses.
- Generated seven analysis tables and four version-controlled SVG charts.
- Generated `outputs/analysis_report.md` and the standalone
  `outputs/dashboard.html` dashboard.
- Established the delivered-order baseline and complete trend window through
  August 2018.
- Verified the pipeline tests: 2 tests pass.
- Initialized Git on `main`, configured the GitHub remote, and pushed the first
  project commit.
- Expanded the GitHub README with KPIs, findings, recommendations, workflow,
  project structure, reproducibility instructions, limitations, and a dashboard
  preview image.
- Added persistent collaboration guidance and project handoff context.

## Current Task

Maintain a durable project handoff for future Codex sessions, then synchronize
the outstanding local commits to GitHub when the HTTPS connection is stable.

## Important Files

- `AGENTS.md`: long-term development, testing, safety, and context-maintenance
  rules.
- `PROJECT-CONTEXT.md`: authoritative current project handoff.
- `README.md`: GitHub portfolio landing page and reproducibility guide.
- `src/olist_analysis/config.py`: project paths and shared constants.
- `src/olist_analysis/pipeline.py`: ingestion, cleaning, validation, marts, and
  SQLite generation.
- `src/olist_analysis/analytics.py`: business metrics, analytical tables, SVG
  charts, and report generation.
- `src/olist_analysis/dashboard.py`: standalone HTML dashboard generation.
- `scripts/run_pipeline.py`: processing pipeline entry point.
- `scripts/run_analysis.py`: analytical output entry point.
- `scripts/run_dashboard.py`: dashboard entry point.
- `tests/test_pipeline.py`: current automated tests.
- `docs/data_dictionary.md`: dataset fields, keys, and relationships.
- `docs/data_cleaning_rules.md`: cleaning and metric rules.
- `outputs/analysis_report.md`: current business diagnosis.
- `outputs/dashboard.html`: generated operations dashboard.
- `docs/assets/dashboard_preview.png`: README dashboard preview.
- `.gitignore`: prevents raw data, processed data, environments, databases, and
  caches from entering Git.

## Important Decisions

- Delivered orders define completed transactions for order-level KPIs.
- Trend reporting stops at August 2018 to avoid incomplete trailing periods.
- Merchandise GMV represents product value and is kept distinct from freight
  and payment totals.
- Customer identity for repeat behavior uses the stable customer identifier,
  not an individual order-level customer record.
- The analysis reports associations rather than unsupported causal claims.
- Raw CSVs remain immutable and untracked; processed datasets and SQLite are
  reproducible and untracked.
- Reusable logic belongs in `src/olist_analysis/`; scripts only orchestrate.
- The dashboard is a self-contained local HTML artifact using tracked SVG
  charts; the README uses a tracked PNG preview for GitHub rendering.
- Brazilian state codes must remain original two-letter abbreviations. Browser
  auto-translation can corrupt them and should not be treated as source data.
- Project and code filenames remain in English.

## Known Issues

- GitHub HTTPS pushes have intermittently failed on port 443 with timeout or
  connection-reset errors. A push can finish writing objects but lose the final
  server acknowledgement. Confirm remote state on GitHub before retrying.
- The repository is currently private; it must be made public later if it is to
  serve as an externally visible portfolio project.
- Pytest can emit a Windows cache-provider warning when `.pytest_cache` already
  exists in an incompatible state. Tests still pass; use
  `python -m pytest -q -p no:cacheprovider` if a clean, cache-free run is needed.
- The dataset cannot support causal advertising ROI, accounting profit, or
  browsing-funnel conclusions because the necessary variables are absent.

## Next Steps

1. Confirm whether commit `4fbdbc4` reached GitHub; push outstanding commits
   when the GitHub HTTPS connection is stable.
2. Refresh the GitHub repository and verify the README image, Mermaid workflow,
   internal links, and badges render correctly.
3. Add cohort-retention analysis to complement the current RFM segmentation.
4. Add minimum-volume thresholds to seller and state risk rankings so small
   samples do not dominate operational priorities.
5. Create a prioritized seller-state late-delivery action table.
6. Decide when to make the repository public and whether to publish the static
   dashboard through GitHub Pages or another static host.

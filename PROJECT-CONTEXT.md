# Project Context

Last updated: 2026-08-31

## Project Goal

Build a portfolio-quality, reproducible analytics project that converts the
nine public Olist Brazilian e-commerce CSV datasets into reliable analytical
marts, an operations dashboard, a business diagnosis, and prioritized customer,
seller, category, logistics, and growth actions.

## Current Status

The end-to-end project is operational. The environment, processing pipeline,
analytical outputs, automated tests, report, dashboard, documentation, Git
repository, and GitHub remote are configured. Customer cohort retention,
tie-stable RFM segmentation, cohort-RFM targeting, and volume-qualified
delivery-risk prioritization are integrated into the analysis layer, report,
dashboard, methodology docs, tests, and GitHub presentation. The analysis
generates ten metric tables and six SVG charts, and all configured quality
checks pass.

The cohort-RFM phase is committed locally and `main` is one commit ahead of
`origin/main`. The latest push could not connect to `github.com:443`; all local
work and generated presentation artifacts are safe.

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
- Generated ten analysis tables and six version-controlled SVG charts.
- Generated `outputs/analysis_report.md` and the standalone
  `outputs/dashboard.html` dashboard.
- Established the delivered-order baseline and complete trend window through
  August 2018.
- Added tidy monthly cohort retention based on first completed purchase month,
  plus an 18-cohort, 12-month SVG heatmap and dashboard summary table.
- Measured weighted exact-month retention at 0.48% for month 1, 0.26% for month
  3, and 0.23% for month 6.
- Added a focused cohort methodology document covering population, definitions,
  censoring, and interpretation.
- Corrected RFM scoring so tied recency and monetary values receive the same
  score and frequency uses actual completed order count capped at 5. This
  prevents identical one-time buyers from being arbitrarily labeled loyal.
- Made RFM segments mutually exclusive and restored meaningful `champions`,
  `at_risk`, `loyal`, `high_value`, `new_active`, and `standard` groups.
- Added 88 cohort-RFM target groups. Forty-one meet the minimum of 100 buyers
  and three observable follow-up months; the top group is the November 2017
  `at_risk` cohort with 2,702 target customers and R$719,732.08 merchandise GMV.
- Added strategic priority tiers, suggested customer journeys, a dedicated
  targeting methodology, an SVG ranking chart, report conclusions, and
  dashboard action table.
- Added minimum completed-order guards of 100 for state risk, 20 for seller
  risk, and 10 for seller-state action lanes.
- Added impact-first delivery-risk ranking by late-order volume, then late rate
  and merchandise GMV.
- Generated 1,886 qualified seller-state action lanes; 24 states and 804
  sellers meet their ranking thresholds. The leading lane is seller
  `4a3ca9315b744ce9f8e9374361493884`, SP to SP, with 58 late orders across 800
  completed orders.
- Added dispatch-SLA versus carrier-lane triage and a dedicated delivery-risk
  methodology document.
- Verified the automated test suite: 7 tests pass.
- Added working Flake8 and mypy configuration and verified isort, Black,
  Flake8, mypy, tests, analysis generation, and dashboard generation.
- Initialized Git on `main`, configured the GitHub remote, and pushed the first
  project commit.
- Expanded the GitHub README with KPIs, findings, recommendations, workflow,
  project structure, reproducibility instructions, limitations, and a dashboard
  preview image.
- Added persistent collaboration guidance and project handoff context.

## Current Task

Build a concise executive synthesis view connecting retention opportunity,
delivery risk, and commercial value without implying causal effects.

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
- `docs/cohort_retention_methodology.md`: cohort population, month index,
  retention formula, censoring, and interpretation.
- `docs/cohort_rfm_targeting_methodology.md`: tie-stable RFM definitions,
  cohort eligibility, target pools, priority tiers, and journey rules.
- `docs/delivery_risk_methodology.md`: volume guards, ranking order, triage
  rules, and interpretation limits for delivery-risk actions.
- `outputs/analysis_report.md`: current business diagnosis.
- `outputs/dashboard.html`: generated operations dashboard.
- `outputs/analysis/cohort_retention.svg`: tracked cohort-retention heatmap.
- `outputs/analysis/cohort_retention.csv`: generated tidy cohort metrics; the
  CSV is reproducible and intentionally untracked.
- `outputs/analysis/cohort_rfm_targets.csv`: generated cohort-segment retention
  planning queue; reproducible and intentionally untracked.
- `outputs/analysis/cohort_rfm_targets.svg`: tracked top retention target chart.
- `outputs/analysis/seller_state_delivery_actions.csv`: generated qualified
  seller-to-customer-state delivery action queue; reproducible and untracked.
- `docs/assets/dashboard_preview.png`: README dashboard preview.
- `.flake8`: executable Flake8 configuration.
- `.gitignore`: prevents raw data, processed data, environments, databases, and
  caches from entering Git.

## Important Decisions

- Delivered orders define completed transactions for order-level KPIs.
- Trend reporting stops at August 2018 to avoid incomplete trailing periods.
- Merchandise GMV represents product value and is kept distinct from freight
  and payment totals.
- Customer identity for repeat behavior uses the stable customer identifier,
  not an individual order-level customer record.
- A customer's cohort is the month of the first delivered order through
  2018-08. Each customer is counted once per activity month, and exact-month
  retention is active buyers divided by the initial cohort size.
- Missing future cells for recent cohorts are censored observations, not zero
  retention. Month 1, 3, and 6 are exact-month rates, not cumulative survival.
- RFM recency and monetary scores use tie-stable percentile bands. Frequency
  uses actual completed order count capped at 5 because the distribution is too
  concentrated for defensible quantile splitting.
- RFM assignment is mutually exclusive: champions, at-risk, loyal, high-value,
  new-active, then standard. One-time buyers cannot be loyal or champions.
- Cohort-RFM ranking requires at least 100 buyers and three observable follow-up
  months. Priority tiers and journeys are planning hypotheses, not predicted
  uplift; evaluation should use a holdout group.
- State and seller delivery-risk rankings exclude small samples using explicit
  order-volume guards. Qualified rows rank by late orders, late rate, then GMV.
- Seller-state actions count each seller-order once after aggregating multiple
  items. Dispatch share of at least 35% suggests a seller SLA review; otherwise
  the first review is carrier lane capacity and routing.
- Delivery action labels are investigation starting points, not causal blame or
  statistical-significance claims.
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
  connection-reset errors. The current cohort-RFM commit is pending remote
  synchronization. Confirm remote state after future interrupted pushes.
- The repository is currently private; it must be made public later if it is to
  serve as an externally visible portfolio project.
- Pytest can emit a Windows cache-provider warning when `.pytest_cache` already
  exists in an incompatible state. Tests still pass; use
  `python -m pytest -q -p no:cacheprovider` if a clean, cache-free run is needed.
- The dataset cannot support causal advertising ROI, accounting profit, or
  browsing-funnel conclusions because the necessary variables are absent.

## Next Steps

1. Add a small executive summary view that connects retention opportunity,
   delivery risk, and commercial value without implying causality.
2. Add compact validation summaries for the corrected RFM population and
   cohort-target eligibility to the data-quality report.
3. Decide when to make the repository public and whether to publish the static
   dashboard through GitHub Pages or another static host.

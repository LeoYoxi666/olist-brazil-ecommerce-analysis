# Project Context

Last updated: 2026-09-02

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
generates eleven metric tables and six SVG charts. A three-priority executive
decision summary and compact analysis validations are now integrated into the
analysis layer, report, dashboard, README, and quality report. All configured
quality checks pass, including nine automated tests. The repository is public
and synchronized with `origin/main`. GitHub Pages is enabled with GitHub Actions
as its publishing source. The public dashboard is live and verified, including
all six SVG chart dependencies. The repository homepage points to the live
dashboard and portfolio topics are configured. GitHub Actions also runs the
project's test and core code-quality suite in a clean Python 3.10 environment;
the first CI run completed successfully. The final portfolio-summary update is
committed and synchronized with `origin/main`. All public-facing Markdown
documents, generated report content, dashboard labels and section headings,
and SVG chart titles now use Simplified Chinese. Public Markdown uses one
consistent heading scheme: the H1 title is unnumbered, H2 headings use
sequential decimal numbers, and H3 headings use hierarchical decimal numbers.
Automated presentation checks increased the test suite to 12 passing tests.

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
- Generated eleven analysis tables and six version-controlled SVG charts.
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
- Added an executive decision summary covering retention growth, delivery
  service, and category experience. The qualified historical scopes are 74,153
  target customers with R$10.37M GMV, 7,826 late orders with R$1.16M GMV, and
  six high-GMV below-average-review categories with R$4.98M GMV.
- Added analysis-level validation summaries for the RFM population and
  cohort-target eligibility to `outputs/data_quality_report.json`.
- Confirmed that no one-time buyer is assigned to `loyal` or `champions`, and
  that eligible cohort-RFM target ranks contain no duplicates.
- Added executive-summary methodology, dashboard decision cards, report and
  README conclusions, and an updated dashboard preview.
- Replaced the machine-specific database path in the generated quality report
  with the portable project-relative path.
- Verified the automated test suite: 12 tests pass.
- Added working Flake8 and mypy configuration and verified isort, Black,
  Flake8, mypy, tests, analysis generation, and dashboard generation.
- Initialized Git on `main`, configured the GitHub remote, and pushed the first
  project commit.
- Expanded the GitHub README with KPIs, findings, recommendations, workflow,
  project structure, reproducibility instructions, limitations, and a dashboard
  preview image.
- Added persistent collaboration guidance and project handoff context.
- Changed the GitHub repository visibility to public and enabled GitHub Pages
  with GitHub Actions as the publishing source.
- Added a Pages deployment workflow that publishes only the standalone
  dashboard HTML and its six tracked SVG chart dependencies.
- Successfully deployed and verified the public dashboard at
  `https://leoyoxi666.github.io/olist-brazil-ecommerce-analysis/`; the page and
  all six SVG assets return HTTP 200.
- Set the repository homepage to the live dashboard and added relevant GitHub
  topics for Python, pandas, analytics, visualization, RFM, cohorts, e-commerce,
  and GitHub Pages.
- Confirmed that Git history contains no raw CSVs, processed CSVs, SQLite
  databases, virtual-environment files, Python caches, or compiled bytecode.
- Added automated Python CI for relevant pushes and pull requests. The workflow
  installs dependencies and runs isort, Black, Flake8, mypy, and all 12 tests;
  its first GitHub-hosted run passed.
- Added concise Chinese resume bullets, an interview pitch, an evidence
  walkthrough, and interpretation boundaries for portfolio use.
- Standardized all public-facing reports and methodology documents to
  Simplified Chinese with consistently numbered H2 and H3 headings.
- Localized generated report text, dashboard KPIs, tables, decision cards,
  recommendations, section headings, and all six SVG chart titles while
  preserving English filenames, code identifiers, and source-data values.
- Added automated checks for public-document heading numbering, Chinese
  dashboard/report titles, translated table labels, and preserved state codes.
- Regenerated the dashboard preview after the Chinese presentation update.

## Current Task

Keep the published project healthy and add future analytical enhancements only
when they improve a clear business decision or methodological reliability. The
unified Chinese presentation is committed and synchronized with `origin/main`.

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
- `docs/executive_summary_methodology.md`: executive-priority definitions,
  commercial-scope calculations, action rules, and interpretation limits.
- `docs/portfolio_summary.md`: concise Chinese resume bullets, interview pitch,
  evidence sequence, and interpretation boundaries.
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
- `outputs/analysis/executive_summary.csv`: generated three-row executive
  decision table; reproducible and intentionally untracked.
- `docs/assets/dashboard_preview.png`: README dashboard preview.
- `.flake8`: executable Flake8 configuration.
- `.gitignore`: prevents raw data, processed data, environments, databases, and
  caches from entering Git.
- `.github/workflows/pages.yml`: packages the dashboard and tracked SVG charts
  and deploys them through GitHub Pages.
- `.github/workflows/ci.yml`: runs isort, Black, Flake8, mypy, and pytest with
  Python 3.10 for relevant pushes and pull requests.

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
- Executive prioritization uses three decision areas: retention growth,
  delivery service, and category experience. Commercial values are historical
  merchandise-GMV exposure, not predicted uplift, recoverable revenue, profit,
  or a forecast.
- Category-experience scope is limited to categories within the top ten by GMV
  whose completed-order-weighted review score is below the platform average.
- Analysis validations are appended to the pipeline quality report after
  analytical outputs are generated.
- The analysis reports associations rather than unsupported causal claims.
- Raw CSVs remain immutable and untracked; processed datasets and SQLite are
  reproducible and untracked.
- Reusable logic belongs in `src/olist_analysis/`; scripts only orchestrate.
- The dashboard is a self-contained local HTML artifact using tracked SVG
  charts; the README uses a tracked PNG preview for GitHub rendering.
- GitHub Pages publishes a minimal static artifact containing only
  `outputs/dashboard.html` as `index.html` and the six tracked SVG charts. Raw
  data, processed data, generated CSVs, and the SQLite database are excluded.
- Brazilian state codes must remain original two-letter abbreviations. Browser
  auto-translation can corrupt them and should not be treated as source data.
- Project and code filenames remain in English.
- Public-facing README, methodology documents, generated reports, dashboards,
  table labels, and chart titles use Simplified Chinese. Public Markdown keeps
  H1 unnumbered, H2 sequentially numbered, and H3 hierarchically numbered.

## Known Issues

- GitHub HTTPS pushes have intermittently failed on port 443 with timeout or
  connection-reset errors. Confirm remote state after any interrupted push.
- Pytest can emit a Windows cache-provider warning when `.pytest_cache` already
  exists in an incompatible state. Tests still pass; use
  `python -m pytest -q -p no:cacheprovider` if a clean, cache-free run is needed.
- The dataset cannot support causal advertising ROI, accounting profit, or
  browsing-funnel conclusions because the necessary variables are absent.

## Next Steps

1. Verify the updated GitHub README, methodology documents, dashboard, charts,
   and Pages site after the deployment workflow completes.
2. Continue future analytical enhancements only when they add a clear business
   decision or improve methodological reliability.
3. Keep README, dashboard, report, tests, CI, and project context synchronized
   with any future metric or business-definition changes.

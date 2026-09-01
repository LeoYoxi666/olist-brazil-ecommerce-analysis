# Olist Brazil E-commerce Operations Analysis

An end-to-end analytics project that turns nine raw Olist marketplace datasets
into a reproducible operations diagnosis, customer analysis, and growth action
plan. The workflow covers data quality, analytical marts, customer RFM,
category performance, seller performance, delivery risk, reviews, and an HTML
operations dashboard.

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0%2B-150458?logo=pandas&logoColor=white)
![Tests](https://img.shields.io/badge/tests-9%20passed-2E8B57)
[![Python CI](https://github.com/LeoYoxi666/olist-brazil-ecommerce-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/LeoYoxi666/olist-brazil-ecommerce-analysis/actions/workflows/ci.yml)
![Status](https://img.shields.io/badge/status-active%20development-2F6FED)

## Dashboard preview

![Olist operations dashboard](docs/assets/dashboard_preview.png)

**Live dashboard:**
[Open the published Olist operations dashboard](https://leoyoxi666.github.io/olist-brazil-ecommerce-analysis/)

The generated local dashboard is also available at
[`outputs/dashboard.html`](outputs/dashboard.html). Download or clone the
repository and open the file in a browser to view the full dashboard.

## Executive summary

The baseline uses delivered orders and includes complete trend months through
August 2018.

| KPI | Result | Operational meaning |
|---|---:|---|
| Completed orders | 96,478 | Delivered-order analysis base |
| Merchandise GMV | R$13.22M | Product value excluding freight |
| Active buyers | 93,358 | Unique customers with completed orders |
| Average order value | R$137.04 | Merchandise GMV per completed order |
| Repeat buyer rate | 3.00% | Retention is the clearest growth gap |
| Late delivery rate | 8.11% | Material service-risk population |
| Average delivery time | 12.13 days | Purchase-to-delivery cycle time |
| Average review score | 4.16 / 5 | Overall delivered-order satisfaction |

### Executive decision priorities

| Priority | Current signal | Historical scope | Merchandise GMV | Recommended action |
|---|---:|---:|---:|---|
| Retention growth | 3.00% repeat-buyer rate | 74,153 qualified target customers | R$10.37M | Segment-specific tests with holdouts |
| Delivery service | 8.11% late-delivery rate | 7,826 late orders | R$1.16M | Seller dispatch and carrier-lane reviews |
| Category experience | 4.01 / 5 focus-category score | 6 top-GMV categories below platform average | R$4.98M | Resolve quality and freight issues before growth |

Commercial values show historical diagnostic exposure, not predicted uplift,
recoverable revenue, or accounting profit.

## Key findings and recommendations

1. **Retention is the largest growth opportunity.** Only 3.00% of buyers made
   repeat purchases in the observed period. Weighted exact-month cohort
   retention is 0.48% in month 1, 0.26% in month 3, and 0.23% in month 6. The
   combined cohort-RFM queue contains 41 volume- and follow-up-qualified groups;
   the first priority is the November 2017 `at_risk` group with 2,702 target
   customers.
2. **Late delivery is strongly associated with poor reviews.** On-time orders
   average 4.29 stars, compared with 2.57 for late orders. After minimum-volume
   guards, 24 states and 804 sellers qualify for risk ranking. The generated
   seller-state action list contains 1,886 qualified lanes, ordered by affected
   late-order volume.
3. **Marketplace demand scaled rapidly during 2017.** Orders and merchandise
   GMV rose materially, with November 2017 producing the largest complete-month
   volume. Treat this as a seasonal planning signal rather than proof of a
   campaign effect.
4. **Category decisions should balance sales and experience.** High-GMV
   categories with weak ratings or high freight burden require quality and
   logistics actions before additional promotion.
5. **Regional service levels are uneven.** Use state-level GMV, delivery time,
   delay rate, and review score together to allocate operational attention by
   both commercial impact and customer risk.

See the full diagnosis in
[`outputs/analysis_report.md`](outputs/analysis_report.md).

## Reproducible workflow

```mermaid
flowchart LR
    A[9 raw CSV files] --> B[Data quality and cleaning pipeline]
    B --> C[Clean tables and analytical marts]
    C --> D[(SQLite database)]
    C --> E[Customer, category, seller and logistics analysis]
    E --> F[CSV metrics and SVG charts]
    F --> G[Business report]
    F --> H[HTML dashboard]
```

### 1. Clone and create an environment

```powershell
git clone https://github.com/LeoYoxi666/olist-brazil-ecommerce-analysis.git
cd olist-brazil-ecommerce-analysis
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, allow scripts only for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 2. Add the source data

Place these nine unchanged CSV files in `data/raw/`:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

Raw and processed data are excluded from Git because they are large and can be
recreated from the public Olist dataset.

### 3. Run the complete analysis

Run each stage from the project root:

```powershell
python scripts/run_pipeline.py
python scripts/run_analysis.py
python scripts/run_dashboard.py
python -m pytest -q
```

Expected verification result:

```text
Built 13 tables
Quality checks: 12
Generated 11 analysis tables
9 passed
```

Open the dashboard on Windows:

```powershell
Start-Process .\outputs\dashboard.html
```

## Project structure

```text
olist-brazil-ecommerce-analysis/
|-- configs/                    # Reserved project configuration
|-- data/
|   |-- raw/                    # Nine source CSV files (not tracked)
|   `-- processed/              # Clean tables, marts and SQLite (not tracked)
|-- docs/
|   |-- assets/                 # README presentation assets
|   |-- cohort_retention_methodology.md
|   |-- cohort_rfm_targeting_methodology.md
|   |-- delivery_risk_methodology.md
|   |-- executive_summary_methodology.md
|   |-- data_dictionary.md      # Dataset keys and relationships
|   `-- data_cleaning_rules.md  # Cleaning and metric rules
|-- outputs/
|   |-- analysis/               # Metric tables and SVG charts
|   |-- analysis_report.md      # Business diagnosis
|   `-- dashboard.html          # Standalone operations dashboard
|-- scripts/                    # Pipeline entry points
|-- src/olist_analysis/         # Reusable processing and analysis package
|-- tests/                      # Automated pipeline tests
|-- pyproject.toml              # Python tooling configuration
`-- requirements.txt            # Reproducible dependencies
```

## Main analytical outputs

| Artifact | Purpose |
|---|---|
| `order_mart.csv` | One row per order with customer, delivery, payment, and review metrics |
| `item_mart.csv` | Item-, product-, category-, seller-, price-, and freight-level analysis |
| `user_mart.csv` | Customer recency, frequency, monetary value, and RFM segment |
| `seller_mart.csv` | Seller volume, GMV, freight, delivery, and satisfaction performance |
| `olist_analysis.sqlite` | Thirteen cleaned and analytical tables for SQL exploration |
| `data_quality_report.json` | Row counts, keys, missingness, and validation results |
| `analysis/*.csv` | Monthly, cohort, category, state, seller, RFM, and logistics metrics |
| `analysis/*.svg` | Version-controlled charts used by the dashboard |
| `cohort_retention.csv` | Tidy monthly cohort size, active buyers, and retention rates |
| `cohort_rfm_targets.csv` | Qualified cohort-segment retention planning queue |
| `executive_summary.csv` | Three-row management decision summary with historical scope |
| `seller_state_delivery_actions.csv` | Volume-qualified seller-to-customer-state delivery review queue |

## Metric and quality controls

- Source CSVs remain unchanged in `data/raw/`.
- Order-level KPIs use delivered orders as completed transactions.
- Trend analysis stops at August 2018 to avoid incomplete trailing months.
- Invalid timestamps are coerced to missing values and monitored.
- Duplicate primary keys, join coverage, missingness, and output row counts are
  checked by the pipeline.
- The analysis stage appends RFM population integrity and cohort-target ranking
  checks to `data_quality_report.json`.
- Monetary metrics distinguish merchandise value, freight, and payments.
- RFM scoring preserves ties; frequency uses actual completed order count capped
  at 5 so one-time buyers cannot be arbitrarily scored as loyal.
- Cohort-RFM priority groups require at least 100 buyers and three observable
  follow-up months.
- Delivery risk rankings require at least 100 completed orders per state, 20
  per seller, and 10 per seller-state lane; eligible rows are ranked by late
  orders, late rate, then merchandise GMV.
- Reusable transformations live in `src/`; scripts only orchestrate stages.

Detailed definitions are documented in
[`docs/data_dictionary.md`](docs/data_dictionary.md) and
[`docs/data_cleaning_rules.md`](docs/data_cleaning_rules.md). Cohort definitions
are documented in
[`docs/cohort_retention_methodology.md`](docs/cohort_retention_methodology.md).
Cohort-RFM segmentation, eligibility, and journey rules are documented in
[`docs/cohort_rfm_targeting_methodology.md`](docs/cohort_rfm_targeting_methodology.md).
Executive scope and interpretation rules are documented in
[`docs/executive_summary_methodology.md`](docs/executive_summary_methodology.md).
Delivery ranking thresholds and triage logic are documented in
[`docs/delivery_risk_methodology.md`](docs/delivery_risk_methodology.md).

## Technology

- Python 3.10+
- pandas and NumPy
- SQLite
- HTML, CSS, and SVG
- pytest, Black, isort, Flake8, and mypy
- Git and GitHub

## Analytical limitations

The source data does not include campaign exposure, advertising spend, product
cost, marketplace commission, or browsing behavior. The project therefore does
not claim causal marketing lift, advertising ROI, accounting profit, or funnel
conversion. Relationships such as delivery delay and review score are
diagnostic associations, not controlled causal estimates.

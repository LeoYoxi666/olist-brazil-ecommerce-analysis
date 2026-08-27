# Olist Brazil E-commerce Operations Diagnosis

This project analyzes Olist marketplace data with a user-analysis-first
workflow, extended with product, logistics, review, and seller diagnostics.

## Project workflow

1. Keep the nine source CSV files unchanged in `data/raw/`.
2. Run the reproducible pipeline to create cleaned data and analysis marts.
3. Generate user, product, logistics, and seller metrics.
4. Review the generated charts and `outputs/analysis_report.md`.
5. Validate the findings against the metric definitions in `docs/`.

## Run the project

```powershell
python scripts/run_pipeline.py
python scripts/run_analysis.py
```

The scripts use paths relative to the project root. They do not require
hardcoded machine-specific paths.

## Main outputs

- `data/processed/olist_analysis.sqlite`: cleaned source tables and marts.
- `data/processed/*_mart.csv`: order, item, user, and seller analysis tables.
- `outputs/analysis/`: metric tables and SVG charts.
- `outputs/analysis_report.md`: first-pass business diagnosis.
- `outputs/data_quality_report.json`: reproducibility and quality checks.

## Scope note

The data contains transactions, payments, reviews, delivery events, and
seller/product dimensions. It does not contain ad impressions, campaign
exposure, product cost, or commission data, so the project does not claim
causal campaign lift, advertising ROI, or accounting profit.

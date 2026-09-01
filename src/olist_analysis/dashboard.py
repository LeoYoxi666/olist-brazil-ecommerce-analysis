"""Build a lightweight, dependency-free HTML operations dashboard."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from olist_analysis.config import COMPLETED_STATUS, ProjectPaths


def _read(paths: ProjectPaths, name: str) -> pd.DataFrame:
    """Read one generated analysis table."""
    return pd.read_csv(paths.analysis / f"{name}.csv")


def _table_html(frame: pd.DataFrame, columns: list[str], limit: int) -> str:
    """Render a selected DataFrame slice as an escaped HTML table."""
    view = frame.loc[:, columns].head(limit).copy()
    view.columns = [column.replace("_", " ").title() for column in view.columns]
    return str(
        view.to_html(index=False, classes="data-table", border=0, justify="left")
    )


def _cohort_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Create a compact month 1, 3, and 6 cohort-retention table."""
    sizes = frame.loc[:, ["cohort_month", "cohort_size"]].drop_duplicates()
    rates = frame.pivot(
        index="cohort_month", columns="month_number", values="retention_rate"
    )
    summary = sizes.set_index("cohort_month")
    for month_number in (1, 3, 6):
        column = f"month_{month_number}_retention"
        summary[column] = rates.get(month_number)
        summary[column] = summary[column].map(
            lambda value: "—" if pd.isna(value) else f"{value:.2%}"
        )
        summary[column] = summary[column].replace("\ufffd\ufffd", "—")
    return summary.reset_index().sort_values("cohort_month", ascending=False)


def _executive_cards_html(frame: pd.DataFrame) -> str:
    """Render decision-focused cards from the executive summary table."""
    cards = []
    for row in frame.sort_values("priority_rank").to_dict("records"):
        signal = (
            f"{row['signal_value']:.2%}"
            if row["signal_unit"] == "rate"
            else f"{row['signal_value']:.2f} / 5"
        )
        area = str(row["priority_area"]).replace("_", " ").title()
        scope = str(row["scope_unit"]).replace("_", " ")
        action = str(row["recommended_action"]).replace("_", " ")
        cards.append(
            '<article class="decision-card">'
            f'<div class="decision-rank">Priority {int(row["priority_rank"])}</div>'
            f"<h3>{html.escape(area)}</h3>"
            f'<div class="decision-signal">{html.escape(signal)}</div>'
            f'<div class="decision-detail">{int(row["scope_count"]):,} '
            f"{html.escape(scope)}</div>"
            f'<div class="decision-detail">R${row["commercial_value"]:,.2f} '
            "historical merchandise GMV</div>"
            f'<div class="decision-action">{html.escape(action)}</div>'
            "</article>"
        )
    return "".join(cards)


def build_dashboard(paths: ProjectPaths) -> Path:
    """Write the standalone HTML dashboard and return its path."""
    order_mart = pd.read_csv(paths.processed / "order_mart.csv")
    user_mart = pd.read_csv(paths.processed / "user_mart.csv")
    category = _read(paths, "category_metrics")
    state = _read(paths, "state_metrics")
    monthly = _read(paths, "monthly_metrics")
    cohort = _read(paths, "cohort_retention")
    cohort_rfm = _read(paths, "cohort_rfm_targets")
    executive = _read(paths, "executive_summary")
    seller_state_actions = _read(paths, "seller_state_delivery_actions")
    completed = order_mart[order_mart["order_status"] == COMPLETED_STATUS]
    gmv = completed["merchandise_gmv"].sum()
    aov = completed["merchandise_gmv"].mean()
    repeat_rate = user_mart["is_repeat_buyer"].mean()
    late_rate = completed["is_late_delivery"].mean()
    delivery_days = completed["delivery_days"].mean()
    score = completed["average_review_score"].mean()
    cards = [
        ("Completed orders", f"{len(completed):,}"),
        ("Merchandise GMV", f"{gmv:,.2f}"),
        ("Active buyers", f"{user_mart['customer_unique_id'].nunique():,}"),
        ("Average order value", f"{aov:,.2f}"),
        ("Repeat buyer rate", f"{repeat_rate:.2%}"),
        ("Late delivery rate", f"{late_rate:.2%}"),
        ("Average delivery days", f"{delivery_days:.2f}"),
        ("Average review score", f"{score:.2f} / 5"),
    ]
    card_html = "".join(
        f'<div class="card"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div></div>'
        for label, value in cards
    )
    executive_html = _executive_cards_html(executive)
    category_view = category.sort_values("merchandise_gmv", ascending=False)
    state_view = state[state["risk_ranking_eligible"]].sort_values("risk_priority_rank")
    state_view["late_delivery_rate"] = state_view["late_delivery_rate"].map(
        lambda value: f"{value:.2%}"
    )
    action_view = seller_state_actions.head(15).copy()
    action_view["late_delivery_rate"] = action_view["late_delivery_rate"].map(
        lambda value: f"{value:.2%}"
    )
    action_view["average_dispatch_days"] = action_view["average_dispatch_days"].round(2)
    recent_months = monthly.tail(12).sort_values("order_month", ascending=False)
    cohort_view = _cohort_summary(cohort)
    retention_target_view = (
        cohort_rfm[cohort_rfm["priority_rank"].notna()]
        .sort_values("priority_rank")
        .head(15)
        .copy()
    )
    retention_target_view["repeat_buyer_rate"] = retention_target_view[
        "repeat_buyer_rate"
    ].map(lambda value: f"{value:.2%}")
    retention_target_view["target_customer_gmv"] = retention_target_view[
        "target_customer_gmv"
    ].round(2)
    category_table = _table_html(
        category_view,
        [
            "category_name",
            "completed_orders",
            "merchandise_gmv",
            "average_review_score",
        ],
        10,
    )
    state_table = _table_html(
        state_view,
        [
            "risk_priority_rank",
            "customer_state",
            "completed_orders",
            "late_orders",
            "late_delivery_rate",
            "average_delivery_days",
            "average_review_score",
        ],
        10,
    )
    action_table = _table_html(
        action_view,
        [
            "priority_rank",
            "seller_id",
            "seller_state",
            "customer_state",
            "completed_orders",
            "late_orders",
            "late_delivery_rate",
            "average_dispatch_days",
            "recommended_action",
        ],
        15,
    )
    monthly_table = _table_html(
        recent_months,
        [
            "order_month",
            "completed_orders",
            "merchandise_gmv",
            "active_buyers",
            "average_order_value",
        ],
        12,
    )
    cohort_table = _table_html(
        cohort_view,
        [
            "cohort_month",
            "cohort_size",
            "month_1_retention",
            "month_3_retention",
            "month_6_retention",
        ],
        12,
    )
    retention_target_table = _table_html(
        retention_target_view,
        [
            "priority_rank",
            "cohort_month",
            "rfm_segment",
            "target_customers",
            "target_customer_gmv",
            "repeat_buyer_rate",
            "observable_followup_months",
            "recommended_journey",
        ],
        15,
    )
    dashboard = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Olist Operations Dashboard</title>
<style>
body {{ margin: 0; background: #f4f6fa; color: #172033; font-family: Arial, sans-serif; }}
.wrap {{ max-width: 1220px; margin: 0 auto; padding: 32px; }}
h1 {{ margin: 0 0 6px; font-size: 30px; }}
.subtitle {{ color: #596579; margin-bottom: 24px; }}
.cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
.card, .panel {{ background: #fff; border-radius: 10px; padding: 18px;
box-shadow: 0 2px 10px rgba(23,32,51,.06); }}
.label {{ color: #596579; font-size: 13px; }}
.value {{ font-size: 24px; font-weight: 700; margin-top: 8px; }}
.executive {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
margin-top: 18px; }}
.decision-card {{ background: #172033; color: #fff; border-radius: 10px; padding: 18px; }}
.decision-card h3 {{ margin: 5px 0 12px; font-size: 18px; }}
.decision-rank {{ color: #9fb9ff; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
.decision-signal {{ color: #fff; font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
.decision-detail {{ color: #dbe3f2; font-size: 13px; margin-top: 4px; }}
.decision-action {{ color: #b9f4d0; font-size: 13px; font-weight: 700; margin-top: 14px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 18px; }}
.wide {{ grid-column: 1 / -1; }}
.panel h2 {{ font-size: 18px; margin: 0 0 14px; }}
.chart {{ width: 100%; height: 360px; border: 0; }}
.chart-wide {{ width: 100%; height: auto; border: 0; }}
.data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
.data-table th, .data-table td {{ padding: 8px 6px; border-bottom: 1px solid #e7eaf0;
text-align: left; }}
.data-table th {{ color: #596579; font-weight: 600; }}
.table-scroll {{ overflow-x: auto; }}
.action-table {{ min-width: 1120px; }}
@media (max-width: 800px) {{ .cards, .grid, .executive {{ grid-template-columns: 1fr 1fr; }} }}
@media (max-width: 520px) {{ .cards, .grid, .executive {{ grid-template-columns: 1fr; }} .wrap {{ padding: 18px; }} }}
</style></head>
<body><main class="wrap">
<h1>Olist Brazil E-commerce Operations Dashboard</h1>
<div class="subtitle">Delivered-order baseline; trend window through 2018-08</div>
<section class="cards">{card_html}</section>
<section class="executive">{executive_html}</section>
<section class="grid">
<div class="panel"><h2>Monthly merchandise GMV</h2>
<img class="chart" src="analysis/monthly_gmv.svg" alt="Monthly merchandise GMV"></div>
<div class="panel"><h2>Monthly completed orders</h2>
<img class="chart" src="analysis/monthly_orders.svg" alt="Monthly completed orders"></div>
<div class="panel wide"><h2>Monthly customer cohort retention</h2>
<img class="chart-wide" src="analysis/cohort_retention.svg"
 alt="Monthly customer cohort retention heatmap"></div>
<div class="panel wide"><h2>Top cohort-RFM retention targets</h2>
<img class="chart" src="analysis/cohort_rfm_targets.svg"
 alt="Top cohort and RFM retention target groups"></div>
<div class="panel"><h2>Top categories by GMV</h2>
<img class="chart" src="analysis/top_categories_gmv.svg" alt="Top categories by GMV"></div>
<div class="panel"><h2>Late delivery rate by state</h2>
<img class="chart" src="analysis/state_late_delivery.svg" alt="Late delivery rate by state"></div>
<div class="panel"><h2>Top categories</h2>
{category_table}</div>
<div class="panel"><h2>State service risk</h2>
{state_table}</div>
<div class="panel"><h2>Recent monthly performance</h2>
{monthly_table}</div>
<div class="panel wide"><h2>Cohort retention summary</h2>
{cohort_table}</div>
<div class="panel wide"><h2>Cohort-RFM retention action list</h2>
<div class="table-scroll action-table">{retention_target_table}</div></div>
<div class="panel wide"><h2>Seller-state late-delivery action list</h2>
<div class="table-scroll action-table">{action_table}</div></div>
</section></main></body></html>"""
    output = paths.outputs / "dashboard.html"
    output.write_text(dashboard, encoding="utf-8")
    return output

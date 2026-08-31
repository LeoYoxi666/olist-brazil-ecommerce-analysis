"""Generate reproducible metrics, SVG charts, and a first business report."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from olist_analysis.config import (
    COMPLETED_STATUS,
    LAST_COMPLETE_TREND_MONTH,
    MIN_SELLER_RISK_ORDERS,
    MIN_SELLER_STATE_ACTION_ORDERS,
    MIN_STATE_RISK_ORDERS,
    SELLER_DISPATCH_SHARE_THRESHOLD,
    ProjectPaths,
)


def _read_processed(paths: ProjectPaths, name: str) -> pd.DataFrame:
    """Read one processed CSV table."""
    return pd.read_csv(paths.processed / f"{name}.csv")


def _parse_datetime(frame: pd.DataFrame, columns: list[str]) -> None:
    """Parse date columns in place, coercing invalid values to missing."""
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")


def _write_svg(path: Path, body: str, title: str) -> None:
    """Write a self-contained SVG document."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680"
 viewBox="0 0 1200 680">
<rect width="1200" height="680" fill="#ffffff"/>
<text x="70" y="58" font-family="Arial" font-size="26" font-weight="700"
 fill="#172033">{html.escape(title)}</text>
{body}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def _line_chart(path: Path, labels: list[str], values: list[float], title: str) -> None:
    """Render a simple line chart as an SVG file."""
    width, height = 1080, 520
    left, top, right, bottom = 90, 90, 40, 90
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(values) if values else 1.0
    maximum = maximum * 1.1 if maximum else 1.0
    points = []
    for index, value in enumerate(values):
        x = left + plot_width * index / max(len(values) - 1, 1)
        y = top + plot_height * (1 - value / maximum)
        points.append((x, y))
    path_data = " ".join(
        f"{'M' if index == 0 else 'L'} {x:.1f} {y:.1f}"
        for index, (x, y) in enumerate(points)
    )
    body = [
        f'<line x1="{left}" y1="{top + plot_height}" x2="{width - right}" '
        f'y2="{top + plot_height}" stroke="#9aa5b1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{top + plot_height}" stroke="#9aa5b1"/>',
        f'<path d="{path_data}" fill="none" stroke="#2f6fed" stroke-width="4"/>',
    ]
    for index, (x, y) in enumerate(points):
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#2f6fed"/>')
        if index % max(len(labels) // 10, 1) == 0:
            body.append(
                f'<text x="{x:.1f}" y="{top + plot_height + 30}" '
                f'text-anchor="middle" font-family="Arial" font-size="12">'
                f"{html.escape(labels[index])}</text>"
            )
    _write_svg(path, "\n".join(body), title)


def _bar_chart(
    path: Path,
    labels: list[str],
    values: list[float],
    title: str,
    color: str = "#2f6fed",
) -> None:
    """Render a horizontal bar chart as an SVG file."""
    width, height = 1080, 520
    left, top, right, bottom = 250, 90, 50, 70
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(values) if values else 1.0
    bar_height = plot_height / max(len(values), 1) * 0.65
    body = [
        f'<line x1="{left}" y1="{top + plot_height}" x2="{width - right}" '
        f'y2="{top + plot_height}" stroke="#9aa5b1"/>',
    ]
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + plot_height * index / max(len(values), 1)
        bar_width = plot_width * value / maximum if maximum else 0
        body.append(
            f'<rect x="{left}" y="{y:.1f}" width="{bar_width:.1f}" '
            f'height="{bar_height:.1f}" rx="3" fill="{color}"/>'
        )
        body.append(
            f'<text x="{left - 10}" y="{y + bar_height * 0.75:.1f}" '
            f'text-anchor="end" font-family="Arial" font-size="13">'
            f"{html.escape(str(label))}</text>"
        )
        body.append(
            f'<text x="{left + bar_width + 8:.1f}" '
            f'y="{y + bar_height * 0.75:.1f}" font-family="Arial" '
            f'font-size="12">{value:,.0f}</text>'
        )
    _write_svg(path, "\n".join(body), title)


def _build_cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:
    """Build tidy monthly customer-cohort retention metrics."""
    required = {
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "customer_unique_id",
    }
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f"Missing cohort columns: {sorted(missing)}")

    activity = orders.loc[:, sorted(required)].copy()
    _parse_datetime(activity, ["order_purchase_timestamp"])
    activity = activity[
        (activity["order_status"] == COMPLETED_STATUS)
        & activity["order_purchase_timestamp"].notna()
        & activity["customer_unique_id"].notna()
    ].copy()
    activity["activity_month"] = activity["order_purchase_timestamp"].dt.to_period("M")
    cutoff = pd.Period(LAST_COMPLETE_TREND_MONTH, freq="M")
    activity = activity[activity["activity_month"] <= cutoff]

    columns = [
        "cohort_month",
        "cohort_size",
        "month_number",
        "active_buyers",
        "retention_rate",
    ]
    if activity.empty:
        return pd.DataFrame(columns=columns)

    activity = activity.drop_duplicates(subset=["customer_unique_id", "activity_month"])
    activity["cohort_month"] = activity.groupby("customer_unique_id")[
        "activity_month"
    ].transform("min")
    activity["month_number"] = activity["activity_month"].astype("int64") - activity[
        "cohort_month"
    ].astype("int64")
    cohort_sizes = (
        activity[activity["month_number"] == 0]
        .groupby("cohort_month")["customer_unique_id"]
        .nunique()
        .rename("cohort_size")
    )
    retention = (
        activity.groupby(["cohort_month", "month_number"], as_index=False)
        .agg(active_buyers=("customer_unique_id", "nunique"))
        .merge(cohort_sizes, on="cohort_month", how="left", validate="many_to_one")
    )
    retention["retention_rate"] = retention["active_buyers"] / retention["cohort_size"]
    retention["cohort_month"] = retention["cohort_month"].astype(str)
    return retention.loc[:, columns].sort_values(
        ["cohort_month", "month_number"], ignore_index=True
    )


def _retention_heatmap(
    path: Path,
    retention: pd.DataFrame,
    title: str,
    max_cohorts: int = 18,
    max_months: int = 12,
) -> None:
    """Render recent monthly cohort retention as an SVG heatmap."""
    if retention.empty:
        _write_svg(
            path,
            '<text x="70" y="130" font-family="Arial" font-size="18">'
            "No cohort data available</text>",
            title,
        )
        return

    matrix = retention.pivot(
        index="cohort_month", columns="month_number", values="retention_rate"
    ).sort_index()
    matrix = matrix.tail(max_cohorts)
    last_month = min(int(retention["month_number"].max()), max_months)
    month_numbers = list(range(last_month + 1))
    matrix = matrix.reindex(columns=month_numbers)

    left, top, right = 150, 115, 45
    plot_width = 1200 - left - right
    cell_width = plot_width / max(len(month_numbers), 1)
    cell_height = min(28.0, 490 / max(len(matrix), 1))
    repeat_values = retention.loc[retention["month_number"] > 0, "retention_rate"]
    scale_max = max(float(repeat_values.max()) if not repeat_values.empty else 0, 0.01)
    start_color = (238, 243, 255)
    end_color = (47, 111, 237)
    body: list[str] = []

    for column_index, month_number in enumerate(month_numbers):
        x = left + column_index * cell_width + cell_width / 2
        body.append(
            f'<text x="{x:.1f}" y="98" text-anchor="middle" '
            f'font-family="Arial" font-size="13" fill="#596579">'
            f"M{month_number}</text>"
        )

    for row_index, (cohort_month, row) in enumerate(matrix.iterrows()):
        y = top + row_index * cell_height
        body.append(
            f'<text x="{left - 12}" y="{y + cell_height * 0.7:.1f}" '
            f'text-anchor="end" font-family="Arial" font-size="13" '
            f'fill="#172033">{html.escape(str(cohort_month))}</text>'
        )
        for column_index, month_number in enumerate(month_numbers):
            x = left + column_index * cell_width
            value = row.get(month_number)
            if pd.isna(value):
                fill = "#f4f6fa"
                label = ""
                text_color = "#596579"
            else:
                ratio = min(float(value) / scale_max, 1.0)
                fill_rgb = tuple(
                    round(start + (end - start) * ratio)
                    for start, end in zip(start_color, end_color)
                )
                fill = "#{:02x}{:02x}{:02x}".format(*fill_rgb)
                label = f"{float(value):.1%}"
                text_color = "#ffffff" if ratio >= 0.55 else "#172033"
            body.append(
                f'<rect x="{x + 1:.1f}" y="{y + 1:.1f}" '
                f'width="{cell_width - 2:.1f}" height="{cell_height - 2:.1f}" '
                f'rx="3" fill="{fill}"/>'
            )
            if label:
                body.append(
                    f'<text x="{x + cell_width / 2:.1f}" '
                    f'y="{y + cell_height * 0.68:.1f}" text-anchor="middle" '
                    f'font-family="Arial" font-size="11" fill="{text_color}">'
                    f"{label}</text>"
                )
    _write_svg(path, "\n".join(body), title)


def _weighted_cohort_rate(retention: pd.DataFrame, month_number: int) -> float:
    """Return the cohort-size-weighted retention rate for one month number."""
    selected = retention[retention["month_number"] == month_number]
    if selected.empty or selected["cohort_size"].sum() == 0:
        return float("nan")
    return float(selected["active_buyers"].sum() / selected["cohort_size"].sum())


def _apply_risk_ranking(
    frame: pd.DataFrame,
    completed_orders_column: str,
    minimum_orders: int,
) -> pd.DataFrame:
    """Add sample eligibility and impact-first delivery-risk ranking."""
    result = frame.copy()
    if "late_orders" not in result:
        result["late_orders"] = (
            result[completed_orders_column] * result["late_delivery_rate"]
        ).round()
    result["late_orders"] = result["late_orders"].astype("Int64")
    result["risk_ranking_eligible"] = result[completed_orders_column] >= minimum_orders
    result["risk_priority_rank"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    eligible_index = (
        result[result["risk_ranking_eligible"]]
        .sort_values(
            ["late_orders", "late_delivery_rate", "merchandise_gmv"],
            ascending=[False, False, False],
        )
        .index
    )
    result.loc[eligible_index, "risk_priority_rank"] = range(1, len(eligible_index) + 1)
    return result.sort_values(
        ["risk_ranking_eligible", "risk_priority_rank", "merchandise_gmv"],
        ascending=[False, True, False],
        na_position="last",
        ignore_index=True,
    )


def _build_seller_state_actions(
    orders: pd.DataFrame,
    items: pd.DataFrame,
    minimum_orders: int = MIN_SELLER_STATE_ACTION_ORDERS,
) -> pd.DataFrame:
    """Build a volume-qualified seller-to-customer-state delay action list."""
    order_columns = [
        "order_id",
        "customer_state",
        "dispatch_days",
        "delivery_days",
        "is_late_delivery",
        "average_review_score",
        "has_negative_review",
    ]
    required_orders = {"order_status", *order_columns}
    required_items = {
        "order_id",
        "seller_id",
        "seller_state",
        "price",
        "order_status",
    }
    missing_orders = required_orders.difference(orders.columns)
    missing_items = required_items.difference(items.columns)
    if missing_orders or missing_items:
        raise ValueError(
            "Missing seller-state action columns: "
            f"orders={sorted(missing_orders)}, items={sorted(missing_items)}"
        )

    completed_orders = orders[orders["order_status"] == COMPLETED_STATUS].loc[
        :, order_columns
    ]
    seller_orders = (
        items[items["order_status"] == COMPLETED_STATUS]
        .assign(seller_state=lambda frame: frame["seller_state"].fillna("unknown"))
        .groupby(["seller_id", "seller_state", "order_id"], as_index=False)
        .agg(merchandise_gmv=("price", "sum"))
        .merge(completed_orders, on="order_id", how="inner", validate="many_to_one")
    )
    seller_orders["customer_state"] = seller_orders["customer_state"].fillna("unknown")
    seller_orders["delayed_merchandise_gmv"] = seller_orders["merchandise_gmv"].where(
        seller_orders["is_late_delivery"] == 1, 0.0
    )
    actions = seller_orders.groupby(
        ["seller_id", "seller_state", "customer_state"], as_index=False
    ).agg(
        completed_orders=("order_id", "nunique"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        late_orders=("is_late_delivery", "sum"),
        delayed_merchandise_gmv=("delayed_merchandise_gmv", "sum"),
        average_dispatch_days=("dispatch_days", "mean"),
        average_delivery_days=("delivery_days", "mean"),
        average_review_score=("average_review_score", "mean"),
        negative_review_rate=("has_negative_review", "mean"),
    )
    actions = actions[actions["completed_orders"] >= minimum_orders].copy()
    actions["late_orders"] = actions["late_orders"].astype("Int64")
    actions["late_delivery_rate"] = actions["late_orders"] / actions["completed_orders"]
    actions["dispatch_share_of_delivery"] = actions["average_dispatch_days"].div(
        actions["average_delivery_days"].where(actions["average_delivery_days"] > 0)
    )
    actions["recommended_action"] = "carrier_lane_capacity_review"
    actions.loc[
        actions["dispatch_share_of_delivery"] >= SELLER_DISPATCH_SHARE_THRESHOLD,
        "recommended_action",
    ] = "seller_dispatch_sla_review"
    actions = actions.sort_values(
        ["late_orders", "late_delivery_rate", "merchandise_gmv"],
        ascending=[False, False, False],
        ignore_index=True,
    )
    actions.insert(0, "priority_rank", range(1, len(actions) + 1))
    actions["minimum_order_threshold"] = minimum_orders
    return actions


def _build_metrics(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """Build customer, commercial, seller, and logistics metrics."""
    orders = _read_processed(paths, "order_mart")
    items = _read_processed(paths, "item_mart")
    users = _read_processed(paths, "user_mart")
    sellers = _read_processed(paths, "seller_mart")
    _parse_datetime(
        orders,
        [
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    completed = orders[orders["order_status"] == COMPLETED_STATUS].copy()
    complete_months = completed[completed["order_month"] <= LAST_COMPLETE_TREND_MONTH]
    monthly = complete_months.groupby("order_month", as_index=False).agg(
        completed_orders=("order_id", "nunique"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        active_buyers=("customer_unique_id", "nunique"),
        average_order_value=("merchandise_gmv", "mean"),
    )
    category = (
        items[items["order_status"] == COMPLETED_STATUS]
        .groupby("category_name", as_index=False)
        .agg(
            completed_orders=("order_id", "nunique"),
            merchandise_gmv=("price", "sum"),
            average_item_price=("price", "mean"),
            average_freight_share=("freight_share", "mean"),
            average_review_score=("average_review_score", "mean"),
        )
        .sort_values("merchandise_gmv", ascending=False)
    )
    state = completed.groupby("customer_state", as_index=False).agg(
        completed_orders=("order_id", "nunique"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        late_orders=("is_late_delivery", "sum"),
        average_delivery_days=("delivery_days", "mean"),
        late_delivery_rate=("is_late_delivery", "mean"),
        average_review_score=("average_review_score", "mean"),
    )
    state = _apply_risk_ranking(state, "completed_orders", MIN_STATE_RISK_ORDERS)
    rfm = (
        users.groupby("rfm_segment", as_index=False)
        .agg(
            buyers=("customer_unique_id", "nunique"),
            merchandise_gmv=("merchandise_gmv", "sum"),
            average_order_count=("completed_order_count", "mean"),
            average_monetary=("monetary", "mean"),
            average_recency_days=("recency_days", "mean"),
        )
        .sort_values("merchandise_gmv", ascending=False)
    )
    seller = _apply_risk_ranking(
        sellers,
        "completed_order_count",
        MIN_SELLER_RISK_ORDERS,
    )
    logistics = pd.DataFrame(
        [
            {
                "metric": "completed_orders",
                "value": int(len(completed)),
            },
            {
                "metric": "average_dispatch_days",
                "value": completed["dispatch_days"].mean(),
            },
            {
                "metric": "average_delivery_days",
                "value": completed["delivery_days"].mean(),
            },
            {
                "metric": "late_delivery_rate",
                "value": completed["is_late_delivery"].mean(),
            },
            {
                "metric": "average_review_score",
                "value": completed["average_review_score"].mean(),
            },
        ]
    )
    delivery_review = completed.groupby("is_late_delivery", as_index=False).agg(
        orders=("order_id", "nunique"),
        average_review_score=("average_review_score", "mean"),
        negative_review_rate=("has_negative_review", "mean"),
    )
    delivery_review["delivery_status"] = delivery_review["is_late_delivery"].map(
        {0: "on_time", 1: "late"}
    )
    cohort_retention = _build_cohort_retention(orders)
    seller_state_actions = _build_seller_state_actions(orders, items)
    return {
        "monthly_metrics": monthly,
        "category_metrics": category,
        "state_metrics": state,
        "rfm_segments": rfm,
        "seller_metrics": seller,
        "logistics_summary": logistics,
        "delivery_review": delivery_review,
        "cohort_retention": cohort_retention,
        "seller_state_delivery_actions": seller_state_actions,
    }


def _write_report(paths: ProjectPaths, metrics: dict[str, pd.DataFrame]) -> None:
    """Write a concise first-pass business diagnosis in Markdown."""
    category = metrics["category_metrics"]
    rfm = metrics["rfm_segments"]
    cohort = metrics["cohort_retention"]
    state = metrics["state_metrics"]
    seller = metrics["seller_metrics"]
    actions = metrics["seller_state_delivery_actions"]
    logistics = metrics["logistics_summary"].set_index("metric")["value"]
    delivery = metrics["delivery_review"].set_index("delivery_status")
    month_1_retention = _weighted_cohort_rate(cohort, 1)
    month_3_retention = _weighted_cohort_rate(cohort, 3)
    month_6_retention = _weighted_cohort_rate(cohort, 6)
    qualified_states = int(state["risk_ranking_eligible"].sum())
    qualified_sellers = int(seller["risk_ranking_eligible"].sum())
    if actions.empty:
        top_lane_summary = "No seller-state lane meets the action threshold."
    else:
        top_lane = actions.iloc[0]
        top_lane_summary = (
            f"The top qualified lane is seller `{top_lane['seller_id']}` "
            f"({top_lane['seller_state']} to {top_lane['customer_state']}), "
            f"with {int(top_lane['late_orders'])} late orders across "
            f"{int(top_lane['completed_orders'])} completed orders."
        )
    report = f"""# Olist Brazil E-commerce Operations Diagnosis

## Scope

This first-pass report uses delivered orders as completed transactions and
uses purchase month through `{LAST_COMPLETE_TREND_MONTH}` for trend analysis.
The data does not contain campaign exposure, product cost, or commission data;
therefore, this report does not claim campaign causality, advertising ROI, or
accounting profit.
Risk rankings require at least {MIN_STATE_RISK_ORDERS} completed orders per
state, {MIN_SELLER_RISK_ORDERS} per seller, and
{MIN_SELLER_STATE_ACTION_ORDERS} per seller-state lane. These are operational
sample guards, not statistical-significance claims.

## Executive baseline

| Metric | Value |
|---|---:|
| Completed orders | {int(logistics['completed_orders']):,} |
| Merchandise GMV | {category['merchandise_gmv'].sum():,.2f} |
| Active buyers | {int(rfm['buyers'].sum()):,} |
| Average delivery days | {logistics['average_delivery_days']:.2f} |
| Late delivery rate | {logistics['late_delivery_rate']:.2%} |
| Average review score | {logistics['average_review_score']:.2f} / 5 |

## Initial findings

1. **Growth scaled materially during 2017.** The monthly GMV and order charts
   show a strong ramp-up, with the highest complete-month volume in November
   2017. This is a seasonal signal, not proof of a specific campaign effect.
2. **Retention is the clearest growth opportunity.** Weighted cohort retention
   is {month_1_retention:.2%} in month 1, {month_3_retention:.2%} in month 3,
   and {month_6_retention:.2%} in month 6. Use the cohort and RFM outputs
   together to design repeat-purchase journeys.
3. **Late delivery is closely associated with poor satisfaction.** On-time
   orders average {delivery.loc['on_time', 'average_review_score']:.2f} points,
   versus {delivery.loc['late', 'average_review_score']:.2f} for late orders.
   The relationship is diagnostic, not a causal experiment.
4. **Delivery risk is concentrated enough for targeted action.**
   {qualified_states} states and {qualified_sellers} sellers meet the minimum
   volume guards. {top_lane_summary}
5. **Category quality needs to be managed alongside sales.** The category
   output combines GMV, freight share, and ratings; high-volume, low-rating
   categories should not be optimized on sales alone.

## Recommended next actions

1. Use `cohort_retention.csv` to select acquisition cohorts with enough
   follow-up time, then use `rfm_segments.csv` to target new-active, loyal,
   champions, and at-risk users within the retention test.
2. Work through `seller_state_delivery_actions.csv` in priority order. Review
   seller dispatch SLA where dispatch consumes at least
   {SELLER_DISPATCH_SHARE_THRESHOLD:.0%} of delivery time; otherwise review
   carrier lane capacity and routing.
3. Review the top categories with low ratings or high freight share before
   proposing assortment or promotion changes.
4. Recalculate the action list after each intervention window and compare both
   late-order volume and customer review outcomes.

## Generated artifacts

- [Monthly GMV chart](analysis/monthly_gmv.svg)
- [Monthly orders chart](analysis/monthly_orders.svg)
- [Top categories chart](analysis/top_categories_gmv.svg)
- [State late-delivery chart](analysis/state_late_delivery.svg)
- [Customer cohort retention heatmap](analysis/cohort_retention.svg)
- `seller_state_delivery_actions.csv`: qualified lane-level action list

See `../docs/delivery_risk_methodology.md` for thresholds, ranking logic, and
interpretation limits.
"""
    (paths.outputs / "analysis_report.md").write_text(report, encoding="utf-8")


def generate_analysis(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """Generate metric tables, SVG charts, and a Markdown report."""
    paths.analysis.mkdir(parents=True, exist_ok=True)
    metrics = _build_metrics(paths)
    for name, frame in metrics.items():
        frame.to_csv(paths.analysis / f"{name}.csv", index=False)
    monthly = metrics["monthly_metrics"]
    _line_chart(
        paths.analysis / "monthly_gmv.svg",
        monthly["order_month"].tolist(),
        monthly["merchandise_gmv"].tolist(),
        "Monthly merchandise GMV",
    )
    _line_chart(
        paths.analysis / "monthly_orders.svg",
        monthly["order_month"].tolist(),
        monthly["completed_orders"].tolist(),
        "Monthly completed orders",
    )
    category = metrics["category_metrics"].head(10).sort_values("merchandise_gmv")
    _bar_chart(
        paths.analysis / "top_categories_gmv.svg",
        category["category_name"].tolist(),
        category["merchandise_gmv"].tolist(),
        "Top categories by merchandise GMV",
    )
    state = (
        metrics["state_metrics"]
        .loc[lambda frame: frame["risk_ranking_eligible"]]
        .head(10)
        .sort_values("late_delivery_rate")
    )
    _bar_chart(
        paths.analysis / "state_late_delivery.svg",
        state["customer_state"].tolist(),
        (state["late_delivery_rate"] * 100).tolist(),
        "Late delivery rate for priority customer states (%)",
        color="#e05a47",
    )
    _retention_heatmap(
        paths.analysis / "cohort_retention.svg",
        metrics["cohort_retention"],
        "Monthly customer cohort retention",
    )
    _write_report(paths, metrics)
    return metrics

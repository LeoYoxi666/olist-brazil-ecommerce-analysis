"""Unit tests for the Olist data-mart rules."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from olist_analysis.analytics import (
    _apply_risk_ranking,
    _build_analysis_validation,
    _build_cohort_retention,
    _build_cohort_rfm_targets,
    _build_executive_summary,
    _build_seller_state_actions,
)
from olist_analysis.pipeline import _build_order_mart, _build_user_mart, _score_series


def test_score_series_returns_five_ordered_buckets() -> None:
    """Percentile scoring should preserve ties and span five ordered buckets."""
    values = pd.Series([value for value in range(1, 6) for _ in range(20)])
    result = _score_series(values)
    assert set(result.unique()) == {1, 2, 3, 4, 5}
    assert result.groupby(values).nunique().eq(1).all()


def test_user_mart_does_not_label_one_time_buyers_as_loyal() -> None:
    """Tied one-time buyers must share one frequency score and segment safely."""
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3", "o4"],
            "order_status": ["delivered"] * 4,
            "customer_unique_id": ["u1", "u2", "u3", "u3"],
            "order_purchase_timestamp": pd.to_datetime(
                ["2018-01-01", "2018-07-01", "2018-06-01", "2018-07-15"]
            ),
            "merchandise_gmv": [10.0, 100.0, 50.0, 60.0],
            "total_order_value": [12.0, 110.0, 55.0, 66.0],
            "average_review_score": [5.0, 4.0, 4.0, 5.0],
            "delivery_days": [5.0, 6.0, 7.0, 4.0],
            "customer_state": ["SP", "RJ", "MG", "MG"],
        }
    )

    result = _build_user_mart(orders)
    one_time = result[result["completed_order_count"] == 1]

    assert one_time["f_score"].eq(1).all()
    assert not one_time["rfm_segment"].isin(["loyal", "champions"]).any()
    assert result.loc[result["customer_unique_id"] == "u3", "f_score"].iloc[0] == 2


def test_order_mart_aggregates_items_and_payments_once() -> None:
    """Multiple item and payment rows should remain one order row."""
    data = {
        "orders": pd.DataFrame(
            {
                "order_id": ["o1"],
                "customer_id": ["c1"],
                "order_status": ["delivered"],
                "order_purchase_timestamp": [pd.Timestamp("2018-01-01")],
                "order_approved_at": [pd.Timestamp("2018-01-01")],
                "order_delivered_carrier_date": [pd.Timestamp("2018-01-02")],
                "order_delivered_customer_date": [pd.Timestamp("2018-01-04")],
                "order_estimated_delivery_date": [pd.Timestamp("2018-01-05")],
            }
        ),
        "customers": pd.DataFrame(
            {
                "customer_id": ["c1"],
                "customer_unique_id": ["u1"],
                "customer_zip_code_prefix": ["01000"],
                "customer_city": ["city"],
                "customer_state": ["SP"],
            }
        ),
        "items": pd.DataFrame(
            {
                "order_id": ["o1", "o1"],
                "order_item_id": [1, 2],
                "product_id": ["p1", "p2"],
                "seller_id": ["s1", "s1"],
                "shipping_limit_date": [pd.Timestamp("2018-01-02")] * 2,
                "price": [10.0, 20.0],
                "freight_value": [2.0, 3.0],
            }
        ),
        "payments": pd.DataFrame(
            {
                "order_id": ["o1", "o1"],
                "payment_sequential": [1, 2],
                "payment_type": ["credit_card", "voucher"],
                "payment_installments": [1, 1],
                "payment_value": [15.0, 20.0],
            }
        ),
        "reviews": pd.DataFrame(
            {
                "order_id": ["o1"],
                "review_id": ["r1"],
                "review_score": [5],
                "has_review_comment": [0],
                "review_creation_date": [pd.Timestamp("2018-01-05")],
            }
        ),
        "geolocation_clean": pd.DataFrame(
            columns=[
                "zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state",
                "source_point_count",
            ]
        ),
    }
    result = _build_order_mart(data)
    assert len(result) == 1
    assert result.loc[0, "merchandise_gmv"] == 30.0
    assert result.loc[0, "paid_amount"] == 35.0


def test_cohort_retention_uses_first_completed_purchase_month() -> None:
    """Cohorts should use unique monthly buyers and exclude trailing months."""
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3", "o4", "o5", "o6", "o7"],
            "order_status": [
                "delivered",
                "delivered",
                "delivered",
                "delivered",
                "delivered",
                "canceled",
                "delivered",
            ],
            "order_purchase_timestamp": pd.to_datetime(
                [
                    "2018-01-05",
                    "2018-02-08",
                    "2018-03-12",
                    "2018-01-20",
                    "2018-02-03",
                    "2018-03-01",
                    "2018-09-01",
                ]
            ),
            "customer_unique_id": ["u1", "u1", "u1", "u2", "u3", "u3", "u4"],
        }
    )

    result = _build_cohort_retention(orders).set_index(["cohort_month", "month_number"])

    assert result.loc[("2018-01", 0), "cohort_size"] == 2
    assert result.loc[("2018-01", 1), "active_buyers"] == 1
    assert result.loc[("2018-01", 1), "retention_rate"] == 0.5
    assert result.loc[("2018-01", 2), "retention_rate"] == 0.5
    assert result.loc[("2018-02", 0), "cohort_size"] == 1
    assert "2018-09" not in result.index.get_level_values("cohort_month")


def test_cohort_rfm_targets_apply_volume_and_followup_guards() -> None:
    """Target ranks should require group volume and observable month 3."""
    users = pd.DataFrame(
        {
            "customer_unique_id": ["u1", "u2", "u3", "u4", "u5"],
            "first_purchase_at": [
                "2018-01-10",
                "2018-01-20",
                "2018-07-01",
                "2018-07-05",
                "2018-02-01",
            ],
            "last_purchase_at": [
                "2018-01-10",
                "2018-01-20",
                "2018-07-01",
                "2018-07-05",
                "2018-02-01",
            ],
            "completed_order_count": [1, 1, 1, 1, 1],
            "merchandise_gmv": [100.0, 200.0, 50.0, 60.0, 20.0],
            "recency_days": [200, 190, 30, 25, 180],
            "average_review_score": [5.0, 4.0, 5.0, 4.0, 3.0],
            "rfm_segment": [
                "high_value",
                "high_value",
                "new_active",
                "new_active",
                "standard",
            ],
            "is_repeat_buyer": [0, 0, 0, 0, 0],
        }
    )

    result = _build_cohort_rfm_targets(users, minimum_buyers=2, evaluation_months=3)
    january = result[
        (result["cohort_month"] == "2018-01") & (result["rfm_segment"] == "high_value")
    ].iloc[0]
    july = result[
        (result["cohort_month"] == "2018-07") & (result["rfm_segment"] == "new_active")
    ].iloc[0]

    assert january["target_customers"] == 2
    assert january["priority_rank"] == 1
    assert january["recommended_journey"] == "second_purchase_high_value_offer"
    assert not bool(july["evaluation_eligible"])
    assert pd.isna(july["priority_rank"])


def _sample_executive_metrics() -> dict[str, pd.DataFrame]:
    """Return compact frames shared by executive-summary validation tests."""
    return {
        "logistics_summary": pd.DataFrame(
            {
                "metric": [
                    "repeat_buyer_rate",
                    "late_delivery_rate",
                    "late_orders",
                    "delayed_merchandise_gmv",
                    "average_review_score",
                ],
                "value": [0.03, 0.08, 8, 900.0, 4.2],
            }
        ),
        "cohort_rfm_targets": pd.DataFrame(
            {
                "priority_rank": pd.Series([1, pd.NA], dtype="Int64"),
                "target_customers": [100, 50],
                "target_customer_gmv": [5000.0, 1000.0],
                "targeting_eligible": [True, False],
                "evaluation_eligible": [True, True],
            }
        ),
        "seller_state_delivery_actions": pd.DataFrame({"priority_rank": [1, 2]}),
        "category_metrics": pd.DataFrame(
            {
                "category_name": ["weak", "strong"],
                "completed_orders": [100, 80],
                "merchandise_gmv": [10000.0, 8000.0],
                "average_review_score": [3.8, 4.5],
            }
        ),
        "rfm_segments": pd.DataFrame(
            {
                "rfm_segment": ["standard", "loyal", "champions"],
                "buyers": [80, 15, 5],
                "repeat_buyers": [0, 15, 5],
                "one_time_buyers": [80, 0, 0],
            }
        ),
    }


def test_executive_summary_connects_scope_and_commercial_value() -> None:
    """Executive rows should expose retention, delivery, and category scope."""
    result = _build_executive_summary(_sample_executive_metrics()).set_index(
        "priority_area"
    )

    assert result.loc["retention_growth", "scope_count"] == 100
    assert result.loc["retention_growth", "commercial_value"] == 5000.0
    assert result.loc["delivery_service", "scope_count"] == 8
    assert result.loc["category_experience", "scope_count"] == 1


def test_analysis_validation_checks_rfm_and_target_ranks() -> None:
    """Business-rule validation should catch segmentation and ranking defects."""
    result = _build_analysis_validation(_sample_executive_metrics())

    assert result["rfm_population"]["buyers"] == 100
    assert result["rfm_population"]["one_time_buyers_in_loyal_or_champions"] == 0
    assert result["cohort_rfm_targeting"]["ranked_groups"] == 1
    assert result["cohort_rfm_targeting"]["duplicate_priority_ranks"] == 0


def test_risk_ranking_excludes_small_samples_and_ranks_late_volume() -> None:
    """Risk ranks should apply the denominator guard before sorting impact."""
    metrics = pd.DataFrame(
        {
            "name": ["small", "large", "medium"],
            "completed_orders": [10, 100, 30],
            "merchandise_gmv": [100.0, 1000.0, 500.0],
            "late_delivery_rate": [0.5, 0.1, 0.2],
        }
    )

    result = _apply_risk_ranking(metrics, "completed_orders", 20).set_index("name")

    assert not bool(result.loc["small", "risk_ranking_eligible"])
    assert pd.isna(result.loc["small", "risk_priority_rank"])
    assert result.loc["large", "risk_priority_rank"] == 1
    assert result.loc["medium", "risk_priority_rank"] == 2


def test_seller_state_actions_deduplicate_items_and_apply_threshold() -> None:
    """Lane actions should count seller orders rather than individual items."""
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3", "o4"],
            "order_status": ["delivered", "delivered", "delivered", "canceled"],
            "customer_state": ["RJ", "RJ", "MG", "RJ"],
            "dispatch_days": [5.0, 5.0, 1.0, 1.0],
            "delivery_days": [10.0, 10.0, 8.0, 8.0],
            "is_late_delivery": [1, 1, 0, 1],
            "average_review_score": [2.0, 3.0, 5.0, 1.0],
            "has_negative_review": [1, 0, 0, 1],
        }
    )
    items = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o3", "o4"],
            "seller_id": ["s1", "s1", "s1", "s2", "s1"],
            "seller_state": ["SP", "SP", "SP", "ES", "SP"],
            "price": [10.0, 5.0, 20.0, 30.0, 50.0],
            "order_status": [
                "delivered",
                "delivered",
                "delivered",
                "delivered",
                "canceled",
            ],
        }
    )

    result = _build_seller_state_actions(orders, items, minimum_orders=2)

    assert len(result) == 1
    assert result.loc[0, "seller_id"] == "s1"
    assert result.loc[0, "completed_orders"] == 2
    assert result.loc[0, "late_orders"] == 2
    assert result.loc[0, "merchandise_gmv"] == 35.0
    assert result.loc[0, "recommended_action"] == "seller_dispatch_sla_review"

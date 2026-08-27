"""Unit tests for the Olist data-mart rules."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from olist_analysis.pipeline import _build_order_mart, _score_series


def test_score_series_returns_five_ordered_buckets() -> None:
    """Quintile scoring should return values from one through five."""
    values = pd.Series(range(1, 101))
    result = _score_series(values)
    assert set(result.unique()) == {1, 2, 3, 4, 5}


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

"""Load, clean, model, and persist Olist marketplace data."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

import pandas as pd

from olist_analysis.config import (
    COMPLETED_STATUS,
    NEGATIVE_REVIEW_MAX_SCORE,
    ProjectPaths,
)

FILE_NAMES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "translations": "product_category_name_translation.csv",
}


def _first_mode(series: pd.Series) -> str | None:
    """Return the first mode, or None when a series has no values."""
    values = series.dropna()
    if values.empty:
        return None
    modes = values.mode()
    return str(modes.iloc[0]) if not modes.empty else str(values.iloc[0])


def _parse_dates(frame: pd.DataFrame, columns: list[str]) -> None:
    """Convert selected columns to datetime in place."""
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")


def _read_sources(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """Read all nine raw CSV files with identifier-safe dtypes."""
    source = paths.raw
    data = {
        "customers": pd.read_csv(
            source / FILE_NAMES["customers"],
            dtype={"customer_zip_code_prefix": "string"},
        ),
        "geolocation": pd.read_csv(
            source / FILE_NAMES["geolocation"],
            dtype={"geolocation_zip_code_prefix": "string"},
        ),
        "items": pd.read_csv(source / FILE_NAMES["items"]),
        "payments": pd.read_csv(source / FILE_NAMES["payments"]),
        "reviews": pd.read_csv(source / FILE_NAMES["reviews"]),
        "orders": pd.read_csv(source / FILE_NAMES["orders"]),
        "products": pd.read_csv(source / FILE_NAMES["products"]),
        "sellers": pd.read_csv(
            source / FILE_NAMES["sellers"],
            dtype={"seller_zip_code_prefix": "string"},
        ),
        "translations": pd.read_csv(source / FILE_NAMES["translations"]),
    }
    return data


def _clean_sources(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply non-destructive type, text, date, and geography cleaning."""
    customers = data["customers"]
    customers["customer_zip_code_prefix"] = customers[
        "customer_zip_code_prefix"
    ].str.zfill(5)

    sellers = data["sellers"]
    sellers["seller_zip_code_prefix"] = sellers["seller_zip_code_prefix"].str.zfill(5)

    geo = data["geolocation"].drop_duplicates().copy()
    geo["geolocation_zip_code_prefix"] = geo["geolocation_zip_code_prefix"].str.zfill(5)
    geo["geolocation_city"] = geo["geolocation_city"].str.strip().str.lower()
    geo["geolocation_state"] = geo["geolocation_state"].str.strip().str.upper()
    geo_clean = (
        geo.groupby("geolocation_zip_code_prefix", as_index=False)
        .agg(
            geolocation_lat=("geolocation_lat", "median"),
            geolocation_lng=("geolocation_lng", "median"),
            geolocation_city=("geolocation_city", _first_mode),
            geolocation_state=("geolocation_state", _first_mode),
            source_point_count=("geolocation_lat", "size"),
        )
        .rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"})
    )

    orders = data["orders"]
    _parse_dates(
        orders,
        [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    orders["order_status"] = orders["order_status"].str.strip().str.lower()
    orders["is_completed_order"] = (orders["order_status"] == COMPLETED_STATUS).astype(
        int
    )
    orders["is_cancelled_or_unavailable"] = (
        orders["order_status"].isin(["canceled", "unavailable"]).astype(int)
    )

    items = data["items"]
    _parse_dates(items, ["shipping_limit_date"])
    for column in ["price", "freight_value"]:
        items[column] = pd.to_numeric(items[column], errors="coerce")

    payments = data["payments"]
    payments["payment_value"] = pd.to_numeric(
        payments["payment_value"], errors="coerce"
    )

    reviews = data["reviews"]
    _parse_dates(reviews, ["review_creation_date", "review_answer_timestamp"])
    reviews["has_review_comment"] = (
        reviews["review_comment_title"].notna()
        | reviews["review_comment_message"].notna()
    ).astype(int)

    products = data["products"].merge(
        data["translations"], on="product_category_name", how="left"
    )
    products["category_name"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    )
    products["category_name"] = products["category_name"].fillna("uncategorized")
    products["category_translation_status"] = "translated"
    products.loc[
        products["product_category_name"].isna(), "category_translation_status"
    ] = "uncategorized"
    products.loc[
        products["product_category_name"].notna()
        & products["product_category_name_english"].isna(),
        "category_translation_status",
    ] = "untranslated"

    return {
        "customers": customers,
        "geolocation_clean": geo_clean,
        "orders": orders,
        "items": items,
        "payments": payments,
        "reviews": reviews,
        "products": products,
        "sellers": sellers,
        "translations": data["translations"],
    }


def _build_order_mart(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create one row per order after aggregating one-to-many facts."""
    items = data["items"].assign(
        item_total=lambda frame: frame["price"] + frame["freight_value"]
    )
    item_order = items.groupby("order_id", as_index=False).agg(
        item_count=("order_item_id", "count"),
        distinct_product_count=("product_id", "nunique"),
        distinct_seller_count=("seller_id", "nunique"),
        merchandise_gmv=("price", "sum"),
        freight_amount=("freight_value", "sum"),
        total_order_value=("item_total", "sum"),
    )
    payment_order = (
        data["payments"]
        .groupby("order_id", as_index=False)
        .agg(
            payment_count=("payment_sequential", "count"),
            paid_amount=("payment_value", "sum"),
            max_installments=("payment_installments", "max"),
            primary_payment_type=("payment_type", _first_mode),
        )
    )
    review_order = (
        data["reviews"]
        .groupby("order_id", as_index=False)
        .agg(
            review_count=("review_id", "count"),
            average_review_score=("review_score", "mean"),
            minimum_review_score=("review_score", "min"),
            has_negative_review=(
                "review_score",
                lambda value: int((value <= NEGATIVE_REVIEW_MAX_SCORE).any()),
            ),
            has_review_comment=("has_review_comment", "max"),
            latest_review_date=("review_creation_date", "max"),
        )
    )
    orders = (
        data["orders"]
        .merge(data["customers"], on="customer_id", how="left")
        .merge(item_order, on="order_id", how="left")
        .merge(payment_order, on="order_id", how="left")
        .merge(review_order, on="order_id", how="left")
    )
    geo = data["geolocation_clean"].rename(
        columns={
            "zip_code_prefix": "customer_geo_zip_code_prefix",
            "geolocation_lat": "customer_lat",
            "geolocation_lng": "customer_lng",
            "geolocation_city": "customer_geo_city",
            "geolocation_state": "customer_geo_state",
            "source_point_count": "customer_geo_point_count",
        }
    )
    orders = orders.merge(
        geo,
        left_on="customer_zip_code_prefix",
        right_on="customer_geo_zip_code_prefix",
        how="left",
    )
    orders["order_month"] = (
        orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )
    orders["approval_hours"] = (
        orders["order_approved_at"] - orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 3600
    orders["dispatch_days"] = (
        orders["order_delivered_carrier_date"] - orders["order_approved_at"]
    ).dt.total_seconds() / 86400
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_approved_at"]
    ).dt.total_seconds() / 86400
    orders["is_late_delivery"] = (
        (orders["order_status"] == COMPLETED_STATUS)
        & (
            orders["order_delivered_customer_date"]
            > orders["order_estimated_delivery_date"]
        )
    ).astype(int)
    return orders


def _build_item_mart(
    data: dict[str, pd.DataFrame], orders: pd.DataFrame
) -> pd.DataFrame:
    """Create one row per order item with order, product, and seller attributes."""
    order_columns = [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_month",
        "customer_unique_id",
        "customer_state",
        "average_review_score",
        "is_late_delivery",
        "delivery_days",
    ]
    item_mart = (
        data["items"]
        .merge(orders[order_columns], on="order_id", how="left")
        .merge(data["products"], on="product_id", how="left")
        .merge(data["sellers"], on="seller_id", how="left")
    )
    item_mart["item_total"] = item_mart["price"] + item_mart["freight_value"]
    item_mart["freight_share"] = item_mart["freight_value"].div(
        item_mart["item_total"].replace(0, pd.NA)
    )
    return item_mart


def _score_series(series: pd.Series) -> pd.Series:
    """Assign stable quintile scores from 1 to 5."""
    ranked = series.rank(method="first")
    return pd.qcut(ranked, 5, labels=False).astype(int).add(1)


def _build_user_mart(orders: pd.DataFrame) -> pd.DataFrame:
    """Create one row per unique buyer with RFM and lifecycle fields."""
    completed = orders[orders["order_status"] == COMPLETED_STATUS].copy()
    user_mart = completed.groupby("customer_unique_id", as_index=False).agg(
        completed_order_count=("order_id", "nunique"),
        first_purchase_at=("order_purchase_timestamp", "min"),
        last_purchase_at=("order_purchase_timestamp", "max"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        total_order_value=("total_order_value", "sum"),
        average_order_value=("merchandise_gmv", "mean"),
        average_review_score=("average_review_score", "mean"),
        average_delivery_days=("delivery_days", "mean"),
        customer_state=("customer_state", _first_mode),
    )
    reference_date = completed["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    user_mart["recency_days"] = (reference_date - user_mart["last_purchase_at"]).dt.days
    user_mart["frequency"] = user_mart["completed_order_count"]
    user_mart["monetary"] = user_mart["merchandise_gmv"]
    user_mart["r_score"] = 6 - _score_series(user_mart["recency_days"])
    user_mart["f_score"] = _score_series(user_mart["frequency"])
    user_mart["m_score"] = _score_series(user_mart["monetary"])
    user_mart["rfm_score"] = (
        user_mart["r_score"].astype(str)
        + user_mart["f_score"].astype(str)
        + user_mart["m_score"].astype(str)
    )
    conditions = [
        (user_mart["r_score"] >= 4)
        & (user_mart["f_score"] >= 4)
        & (user_mart["m_score"] >= 4),
        user_mart["f_score"] >= 4,
        user_mart["m_score"] >= 4,
        (user_mart["r_score"] <= 2)
        & ((user_mart["f_score"] >= 3) | (user_mart["m_score"] >= 3)),
        (user_mart["r_score"] >= 4) & (user_mart["f_score"] <= 2),
    ]
    labels = ["champions", "loyal", "high_value", "at_risk", "new_active"]
    user_mart["rfm_segment"] = pd.Series(pd.NA, index=user_mart.index, dtype="string")
    for condition, label in zip(conditions, labels):
        user_mart.loc[condition, "rfm_segment"] = label
    user_mart["rfm_segment"] = user_mart["rfm_segment"].fillna("standard")
    user_mart["is_repeat_buyer"] = (user_mart["completed_order_count"] >= 2).astype(int)
    return user_mart


def _build_seller_mart(
    data: dict[str, pd.DataFrame], items: pd.DataFrame
) -> pd.DataFrame:
    """Create one row per seller from delivered seller-order performance."""
    completed_items = items[items["order_status"] == COMPLETED_STATUS]
    seller_order = completed_items.groupby(
        ["seller_id", "order_id"], as_index=False
    ).agg(
        merchandise_gmv=("price", "sum"),
        average_review_score=("average_review_score", "mean"),
        is_late_delivery=("is_late_delivery", "max"),
        delivery_days=("delivery_days", "mean"),
    )
    seller_mart = seller_order.groupby("seller_id", as_index=False).agg(
        completed_order_count=("order_id", "nunique"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        average_order_value=("merchandise_gmv", "mean"),
        average_review_score=("average_review_score", "mean"),
        late_delivery_rate=("is_late_delivery", "mean"),
        average_delivery_days=("delivery_days", "mean"),
    )
    return seller_mart.merge(data["sellers"], on="seller_id", how="left")


def build_analysis_tables(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """Build cleaned source tables and four analysis marts."""
    data = _clean_sources(_read_sources(paths))
    orders = _build_order_mart(data)
    items = _build_item_mart(data, orders)
    return {
        **data,
        "order_mart": orders,
        "item_mart": items,
        "user_mart": _build_user_mart(orders),
        "seller_mart": _build_seller_mart(data, items),
    }


def _quality_report(tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Return row counts, null counts, and key duplication checks."""
    key_map = {
        "customers": ["customer_id"],
        "orders": ["order_id"],
        "items": ["order_id", "order_item_id"],
        "payments": ["order_id", "payment_sequential"],
        "reviews": ["review_id"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
        "translations": ["product_category_name"],
    }
    report: dict[str, Any] = {"tables": {}, "checks": {}}
    for name, frame in tables.items():
        report["tables"][name] = {
            "rows": int(len(frame)),
            "columns": int(len(frame.columns)),
            "null_counts": {
                column: int(count)
                for column, count in frame.isna().sum().items()
                if count
            },
        }
    for name, keys in key_map.items():
        frame = tables[name]
        report["checks"][f"{name}_duplicate_key_rows"] = int(
            frame.duplicated(keys).sum()
        )
    report["checks"]["orders_without_customers"] = int(
        (
            ~tables["orders"]["customer_id"].isin(tables["customers"]["customer_id"])
        ).sum()
    )
    report["checks"]["items_without_orders"] = int(
        (~tables["items"]["order_id"].isin(tables["orders"]["order_id"])).sum()
    )
    report["checks"]["items_without_products"] = int(
        (~tables["items"]["product_id"].isin(tables["products"]["product_id"])).sum()
    )
    report["checks"]["items_without_sellers"] = int(
        (~tables["items"]["seller_id"].isin(tables["sellers"]["seller_id"])).sum()
    )
    return report


def persist_tables(
    paths: ProjectPaths, tables: dict[str, pd.DataFrame]
) -> dict[str, Any]:
    """Write CSV marts, SQLite tables, and a JSON quality report."""
    paths.processed.mkdir(parents=True, exist_ok=True)
    paths.outputs.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(paths.processed / f"{name}.csv", index=False)
    database = paths.processed / "olist_analysis.sqlite"
    if database.exists():
        database.unlink()
    with sqlite3.connect(database) as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="replace", index=False)
        connection.executescript("""
            CREATE INDEX idx_orders_order_id ON orders(order_id);
            CREATE INDEX idx_orders_customer_id ON orders(customer_id);
            CREATE INDEX idx_items_order_id ON items(order_id);
            CREATE INDEX idx_items_product_id ON items(product_id);
            CREATE INDEX idx_items_seller_id ON items(seller_id);
            CREATE INDEX idx_payments_order_id ON payments(order_id);
            CREATE INDEX idx_reviews_order_id ON reviews(order_id);
            CREATE INDEX idx_order_mart_month ON order_mart(order_month);
            CREATE INDEX idx_order_mart_customer ON order_mart(customer_unique_id);
            CREATE INDEX idx_item_mart_category ON item_mart(category_name);
            CREATE INDEX idx_item_mart_seller ON item_mart(seller_id);
            """)
    report = _quality_report(tables)
    report["database"] = str(database)
    (paths.outputs / "data_quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report

"""校验并发布 Power BI 使用的轻量聚合数据集。"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Final

import pandas as pd

from olist_analysis.config import ProjectPaths

# 每张导出表只声明 Power BI 页面真正依赖的字段；新增分析字段不会破坏刷新。
POWERBI_EXPORTS: Final[dict[str, tuple[str, ...]]] = {
    "executive_summary.csv": (
        "priority_rank",
        "priority_area",
        "signal_value",
        "scope_count",
        "commercial_value",
        "recommended_action",
    ),
    "monthly_metrics.csv": (
        "order_month",
        "completed_orders",
        "merchandise_gmv",
        "active_buyers",
        "average_order_value",
    ),
    "rfm_segments.csv": (
        "rfm_segment",
        "buyers",
        "repeat_buyers",
        "merchandise_gmv",
        "average_recency_days",
    ),
    "cohort_retention.csv": (
        "cohort_month",
        "cohort_size",
        "month_number",
        "active_buyers",
        "retention_rate",
    ),
    "cohort_rfm_targets.csv": (
        "priority_rank",
        "cohort_month",
        "rfm_segment",
        "priority_tier",
        "recommended_journey",
        "target_customers",
        "target_customer_gmv",
        "targeting_eligible",
        "evaluation_eligible",
    ),
    "category_metrics.csv": (
        "category_name",
        "completed_orders",
        "merchandise_gmv",
        "average_item_price",
        "average_freight_share",
        "average_review_score",
    ),
    "state_metrics.csv": (
        "customer_state",
        "completed_orders",
        "merchandise_gmv",
        "late_orders",
        "average_delivery_days",
        "late_delivery_rate",
        "average_review_score",
    ),
    "seller_metrics.csv": (
        "seller_id",
        "completed_order_count",
        "merchandise_gmv",
        "average_review_score",
        "late_delivery_rate",
        "seller_state",
        "risk_ranking_eligible",
        "risk_priority_rank",
    ),
    "seller_state_delivery_actions.csv": (
        "priority_rank",
        "seller_id",
        "seller_state",
        "customer_state",
        "completed_orders",
        "late_orders",
        "delayed_merchandise_gmv",
        "late_delivery_rate",
        "recommended_action",
    ),
    "delivery_review.csv": (
        "is_late_delivery",
        "orders",
        "average_review_score",
        "negative_review_rate",
        "delivery_status",
    ),
    "logistics_summary.csv": ("metric", "value"),
}


def _validate_export(source: Path, required_columns: tuple[str, ...]) -> int:
    """验证分析表存在且字段完整，并返回当前行数。"""
    if not source.is_file():
        raise FileNotFoundError(
            f"Power BI source is missing: {source}. Run analysis first."
        )

    frame = pd.read_csv(source)
    missing = sorted(set(required_columns).difference(frame.columns))
    if missing:
        raise ValueError(f"Missing Power BI columns in {source.name}: {missing}")
    return len(frame)


def export_powerbi_data(paths: ProjectPaths) -> dict[str, int]:
    """原子化发布全部 Power BI 聚合 CSV，并返回各表行数。"""
    # 先完整验证清单，避免中途失败后留下新旧版本混合的数据目录。
    row_counts = {
        filename: _validate_export(paths.analysis / filename, required_columns)
        for filename, required_columns in POWERBI_EXPORTS.items()
    }

    paths.powerbi_data.mkdir(parents=True, exist_ok=True)
    for filename in POWERBI_EXPORTS:
        source = paths.analysis / filename
        destination = paths.powerbi_data / filename
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        try:
            shutil.copyfile(source, temporary)
            os.replace(temporary, destination)
        finally:
            # 仅在复制或替换失败时才会遗留临时文件。
            if temporary.exists():
                temporary.unlink()

    return row_counts

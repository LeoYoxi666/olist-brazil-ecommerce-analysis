"""生成可复现的业务指标、SVG 图表和中文分析报告。"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import pandas as pd

from olist_analysis.config import (
    COHORT_RFM_EVALUATION_MONTHS,
    COMPLETED_STATUS,
    LAST_COMPLETE_TREND_MONTH,
    MIN_COHORT_RFM_BUYERS,
    MIN_SELLER_RISK_ORDERS,
    MIN_SELLER_STATE_ACTION_ORDERS,
    MIN_STATE_RISK_ORDERS,
    SELLER_DISPATCH_SHARE_THRESHOLD,
    ProjectPaths,
)

# 分析表保留稳定的英文取值，以下映射只负责报告、图表和仪表盘的中文展示。
RFM_SEGMENT_LABELS = {
    "champions": "冠军用户",
    "at_risk": "流失风险用户",
    "loyal": "忠诚用户",
    "high_value": "高价值用户",
    "new_active": "新近活跃用户",
    "standard": "普通用户",
}

PRIORITY_AREA_LABELS = {
    "retention_growth": "用户留存增长",
    "delivery_service": "配送服务改善",
    "category_experience": "品类体验优化",
}

SCOPE_UNIT_LABELS = {
    "qualified_target_customers": "名合格目标用户",
    "late_orders": "笔延迟订单",
    "top_gmv_below_average_categories": "个高 GMV 且评分低于平台均值的品类",
}

ACTION_LABELS = {
    "run_segmented_retention_holdout_tests": "按客群开展带留出组的留存实验",
    "execute_lane_and_dispatch_reviews": "复核卖家发货与承运线路",
    "review_quality_and_freight_before_growth": "增长前先复核商品质量与运费",
    "seller_dispatch_sla_review": "复核卖家发货 SLA",
    "carrier_lane_capacity_review": "复核承运线路容量与路由",
}

JOURNEY_LABELS = {
    "win_back_service_recovery": "服务补救与流失召回",
    "second_purchase_high_value_offer": "高价值用户二次购买激励",
    "early_second_purchase_nudge": "早期二次购买引导",
    "loyalty_reinforcement": "忠诚关系强化",
    "vip_advocacy": "VIP 口碑与推荐",
    "category_replenishment_nurture": "品类复购培育",
    "manual_review": "人工复核",
}


def _read_processed(paths: ProjectPaths, name: str) -> pd.DataFrame:
    """读取一张处理后的 CSV 表。"""
    return pd.read_csv(paths.processed / f"{name}.csv")


def _parse_datetime(frame: pd.DataFrame, columns: list[str]) -> None:
    """原地解析日期字段，并将无效值转换为空值。"""
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], errors="coerce", format="mixed")


def _write_svg(path: Path, body: str, title: str) -> None:
    """写出不依赖外部资源的 SVG 文档。"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680"
 viewBox="0 0 1200 680">
<rect width="1200" height="680" fill="#ffffff"/>
<text x="70" y="58" font-family="Arial, Microsoft YaHei, sans-serif" font-size="26" font-weight="700"
 fill="#172033">{html.escape(title)}</text>
{body}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def _line_chart(path: Path, labels: list[str], values: list[float], title: str) -> None:
    """将简单折线图渲染为 SVG 文件。"""
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
                f'text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="12">'
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
    """将水平条形图渲染为 SVG 文件。"""
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
            f'text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13">'
            f"{html.escape(str(label))}</text>"
        )
        body.append(
            f'<text x="{left + bar_width + 8:.1f}" '
            f'y="{y + bar_height * 0.75:.1f}" font-family="Arial, Microsoft YaHei, sans-serif" '
            f'font-size="12">{value:,.0f}</text>'
        )
    _write_svg(path, "\n".join(body), title)


def _build_cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:
    """构建整洁格式的月度用户 cohort 留存指标。"""
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

    # 即使同一买家当月有多笔订单，每个活跃月份也只计数一次。
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
    """将近期月度 cohort 留存渲染为 SVG 热力图。"""
    if retention.empty:
        _write_svg(
            path,
            '<text x="70" y="130" font-family="Arial, Microsoft YaHei, sans-serif" font-size="18">'
            "暂无 cohort 数据</text>",
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
            f'font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" fill="#596579">'
            f"M{month_number}</text>"
        )

    for row_index, (cohort_month, row) in enumerate(matrix.iterrows()):
        y = top + row_index * cell_height
        body.append(
            f'<text x="{left - 12}" y="{y + cell_height * 0.7:.1f}" '
            f'text-anchor="end" font-family="Arial, Microsoft YaHei, sans-serif" font-size="13" '
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
                    f'font-family="Arial, Microsoft YaHei, sans-serif" font-size="11" fill="{text_color}">'
                    f"{label}</text>"
                )
    _write_svg(path, "\n".join(body), title)


def _weighted_cohort_rate(retention: pd.DataFrame, month_number: int) -> float:
    """返回指定月份按 cohort 初始人数加权的留存率。"""
    selected = retention[retention["month_number"] == month_number]
    if selected.empty or selected["cohort_size"].sum() == 0:
        return float("nan")
    return float(selected["active_buyers"].sum() / selected["cohort_size"].sum())


def _build_cohort_rfm_targets(
    users: pd.DataFrame,
    minimum_buyers: int = MIN_COHORT_RFM_BUYERS,
    evaluation_months: int = COHORT_RFM_EVALUATION_MONTHS,
) -> pd.DataFrame:
    """组合获客 cohort 与 RFM 客群，生成目标用户队列。"""
    required = {
        "customer_unique_id",
        "first_purchase_at",
        "last_purchase_at",
        "completed_order_count",
        "merchandise_gmv",
        "recency_days",
        "average_review_score",
        "rfm_segment",
        "is_repeat_buyer",
    }
    missing = required.difference(users.columns)
    if missing:
        raise ValueError(f"Missing cohort-RFM columns: {sorted(missing)}")

    columns = [
        "priority_rank",
        "cohort_month",
        "rfm_segment",
        "priority_tier",
        "recommended_journey",
        "buyers",
        "target_customers",
        "repeat_buyers",
        "repeat_buyer_rate",
        "completed_orders",
        "merchandise_gmv",
        "target_customer_gmv",
        "average_customer_gmv",
        "average_recency_days",
        "average_review_score",
        "cohort_buyer_share",
        "cohort_gmv_share",
        "observable_followup_months",
        "targeting_eligible",
        "evaluation_eligible",
    ]
    data = users.loc[:, sorted(required)].copy()
    _parse_datetime(data, ["first_purchase_at", "last_purchase_at"])
    data = data[
        data["first_purchase_at"].notna()
        & data["customer_unique_id"].notna()
        & data["rfm_segment"].notna()
    ].copy()
    if data.empty:
        return pd.DataFrame(columns=columns)

    cutoff = pd.Period(LAST_COMPLETE_TREND_MONTH, freq="M")
    data["cohort_period"] = data["first_purchase_at"].dt.to_period("M")
    data = data[data["cohort_period"] <= cutoff].copy()
    data["cohort_month"] = data["cohort_period"].astype(str)
    data["observable_followup_months"] = cutoff.ordinal - data["cohort_period"].astype(
        "int64"
    )
    data["one_time_buyer"] = 1 - data["is_repeat_buyer"].astype(int)
    data["one_time_buyer_gmv"] = data["merchandise_gmv"].where(
        data["one_time_buyer"] == 1, 0.0
    )
    targets = data.groupby(["cohort_month", "rfm_segment"], as_index=False).agg(
        buyers=("customer_unique_id", "nunique"),
        one_time_buyers=("one_time_buyer", "sum"),
        repeat_buyers=("is_repeat_buyer", "sum"),
        completed_orders=("completed_order_count", "sum"),
        merchandise_gmv=("merchandise_gmv", "sum"),
        one_time_buyer_gmv=("one_time_buyer_gmv", "sum"),
        average_customer_gmv=("merchandise_gmv", "mean"),
        average_recency_days=("recency_days", "mean"),
        average_review_score=("average_review_score", "mean"),
        observable_followup_months=("observable_followup_months", "first"),
    )
    # 一次购买型客群只选择尚未复购的用户；复购型客群保留该组全部用户。
    one_time_segments = {"new_active", "high_value", "standard"}
    targets["target_customers"] = targets["buyers"]
    targets["target_customer_gmv"] = targets["merchandise_gmv"]
    one_time_mask = targets["rfm_segment"].isin(one_time_segments)
    targets.loc[one_time_mask, "target_customers"] = targets.loc[
        one_time_mask, "one_time_buyers"
    ]
    targets.loc[one_time_mask, "target_customer_gmv"] = targets.loc[
        one_time_mask, "one_time_buyer_gmv"
    ]
    targets["repeat_buyer_rate"] = targets["repeat_buyers"] / targets["buyers"]
    targets["cohort_buyer_share"] = targets["buyers"] / targets.groupby("cohort_month")[
        "buyers"
    ].transform("sum")
    targets["cohort_gmv_share"] = targets["merchandise_gmv"] / targets.groupby(
        "cohort_month"
    )["merchandise_gmv"].transform("sum")

    # 层级数字越小越优先；同层级先按可触达用户数排序，再以历史商品 GMV
    # 作为次级排序依据。
    tiers = {
        "at_risk": 1,
        "high_value": 1,
        "new_active": 2,
        "loyal": 2,
        "champions": 3,
        "standard": 3,
    }
    journeys = {
        "at_risk": "win_back_service_recovery",
        "high_value": "second_purchase_high_value_offer",
        "new_active": "early_second_purchase_nudge",
        "loyal": "loyalty_reinforcement",
        "champions": "vip_advocacy",
        "standard": "category_replenishment_nurture",
    }
    targets["priority_tier"] = targets["rfm_segment"].map(tiers).fillna(3).astype(int)
    targets["recommended_journey"] = (
        targets["rfm_segment"].map(journeys).fillna("manual_review")
    )
    targets["targeting_eligible"] = targets["buyers"] >= minimum_buyers
    targets["evaluation_eligible"] = (
        targets["observable_followup_months"] >= evaluation_months
    )
    targets["priority_rank"] = pd.Series(pd.NA, index=targets.index, dtype="Int64")
    eligible_index = (
        targets[
            targets["targeting_eligible"]
            & targets["evaluation_eligible"]
            & (targets["target_customers"] > 0)
        ]
        .sort_values(
            ["priority_tier", "target_customers", "target_customer_gmv"],
            ascending=[True, False, False],
        )
        .index
    )
    targets.loc[eligible_index, "priority_rank"] = range(1, len(eligible_index) + 1)
    return targets.loc[:, columns].sort_values(
        ["priority_rank", "cohort_month", "rfm_segment"],
        ascending=[True, False, True],
        na_position="last",
        ignore_index=True,
    )


def _apply_risk_ranking(
    frame: pd.DataFrame,
    completed_orders_column: str,
    minimum_orders: int,
) -> pd.DataFrame:
    """增加样本资格判断和影响优先的配送风险排名。"""
    result = frame.copy()
    if "late_orders" not in result:
        result["late_orders"] = (
            result[completed_orders_column] * result["late_delivery_rate"]
        ).round()
    result["late_orders"] = result["late_orders"].astype("Int64")
    result["risk_ranking_eligible"] = result[completed_orders_column] >= minimum_orders
    result["risk_priority_rank"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    # 排序先考虑运营影响：延迟订单数是主排序字段，延迟率和商品 GMV
    # 依次作为并列情况下的辅助排序字段。
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
    """生成满足样本量门槛的卖家—用户州延迟行动队列。"""
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
    # 计算线路指标前，先合并同一卖家在同一订单中的多件商品，避免多商品
    # 购物篮虚增订单数量。
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
    # 发货阶段占比较高时先检查卖家 SLA，其他线路先检查承运容量和路由；
    # 两类标签都只是调查起点，不代表已经证明因果关系。
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


def _build_executive_summary(
    metrics: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """根据分析结果生成三条面向管理决策的摘要。"""
    logistics = metrics["logistics_summary"].set_index("metric")["value"]
    cohort_rfm = metrics["cohort_rfm_targets"]
    seller_actions = metrics["seller_state_delivery_actions"]
    category = metrics["category_metrics"]
    ranked_targets = cohort_rfm[cohort_rfm["priority_rank"].notna()]
    top_categories = category.nlargest(10, "merchandise_gmv")
    category_focus = top_categories[
        top_categories["average_review_score"]
        < float(logistics["average_review_score"])
    ]
    # 如果头部品类评分都不低于平台均值，仍保留一个品类供管理摘要展示。
    if category_focus.empty:
        category_focus = top_categories.head(1)
    focus_orders = category_focus["completed_orders"].sum()
    focus_review = (
        category_focus["average_review_score"]
        .mul(category_focus["completed_orders"])
        .sum()
        / focus_orders
    )
    rows = [
        {
            "priority_rank": 1,
            "priority_area": "retention_growth",
            "signal_name": "repeat_buyer_rate",
            "signal_value": float(logistics["repeat_buyer_rate"]),
            "signal_unit": "rate",
            "scope_count": int(ranked_targets["target_customers"].sum()),
            "scope_unit": "qualified_target_customers",
            "commercial_value": float(ranked_targets["target_customer_gmv"].sum()),
            "evidence_scope": f"{len(ranked_targets)} qualified cohort-RFM groups",
            "recommended_action": "run_segmented_retention_holdout_tests",
        },
        {
            "priority_rank": 2,
            "priority_area": "delivery_service",
            "signal_name": "late_delivery_rate",
            "signal_value": float(logistics["late_delivery_rate"]),
            "signal_unit": "rate",
            "scope_count": int(logistics["late_orders"]),
            "scope_unit": "late_orders",
            "commercial_value": float(logistics["delayed_merchandise_gmv"]),
            "evidence_scope": f"{len(seller_actions)} qualified seller-state lanes",
            "recommended_action": "execute_lane_and_dispatch_reviews",
        },
        {
            "priority_rank": 3,
            "priority_area": "category_experience",
            "signal_name": "priority_category_review_score",
            "signal_value": float(focus_review),
            "signal_unit": "score_out_of_5",
            "scope_count": int(len(category_focus)),
            "scope_unit": "top_gmv_below_average_categories",
            "commercial_value": float(category_focus["merchandise_gmv"].sum()),
            "evidence_scope": "top 10 GMV categories versus platform review average",
            "recommended_action": "review_quality_and_freight_before_growth",
        },
    ]
    return pd.DataFrame(rows)


def _build_analysis_validation(
    metrics: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """汇总关键业务规则的验证结果。"""
    rfm = metrics["rfm_segments"]
    cohort_rfm = metrics["cohort_rfm_targets"]
    loyal_segments = rfm[rfm["rfm_segment"].isin(["loyal", "champions"])]
    return {
        "rfm_population": {
            "buyers": int(rfm["buyers"].sum()),
            "repeat_buyers": int(rfm["repeat_buyers"].sum()),
            "one_time_buyers": int(rfm["one_time_buyers"].sum()),
            "segments": {
                str(row["rfm_segment"]): int(row["buyers"]) for _, row in rfm.iterrows()
            },
            "one_time_buyers_in_loyal_or_champions": int(
                loyal_segments["one_time_buyers"].sum()
            ),
        },
        "cohort_rfm_targeting": {
            "groups": int(len(cohort_rfm)),
            "volume_eligible_groups": int(cohort_rfm["targeting_eligible"].sum()),
            "followup_eligible_groups": int(cohort_rfm["evaluation_eligible"].sum()),
            "ranked_groups": int(cohort_rfm["priority_rank"].notna().sum()),
            "duplicate_priority_ranks": int(
                cohort_rfm["priority_rank"].dropna().duplicated().sum()
            ),
        },
    }


def _update_analysis_quality_report(
    paths: ProjectPaths,
    metrics: dict[str, pd.DataFrame],
) -> None:
    """将分析层业务规则检查追加到数据管道质量报告。"""
    report_path = paths.outputs / "data_quality_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        report = {}
    report["analysis_checks"] = _build_analysis_validation(metrics)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _build_metrics(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """构建用户、交易、卖家和物流指标。"""
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
            repeat_buyers=("is_repeat_buyer", "sum"),
            merchandise_gmv=("merchandise_gmv", "sum"),
            average_order_count=("completed_order_count", "mean"),
            average_monetary=("monetary", "mean"),
            average_recency_days=("recency_days", "mean"),
        )
        .sort_values("merchandise_gmv", ascending=False)
    )
    rfm["one_time_buyers"] = rfm["buyers"] - rfm["repeat_buyers"]
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
                "metric": "active_buyers",
                "value": int(users["customer_unique_id"].nunique()),
            },
            {
                "metric": "repeat_buyers",
                "value": int(users["is_repeat_buyer"].sum()),
            },
            {
                "metric": "repeat_buyer_rate",
                "value": users["is_repeat_buyer"].mean(),
            },
            {
                "metric": "late_orders",
                "value": int(completed["is_late_delivery"].sum()),
            },
            {
                "metric": "delayed_merchandise_gmv",
                "value": completed["merchandise_gmv"]
                .where(completed["is_late_delivery"] == 1, 0.0)
                .sum(),
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
    cohort_rfm_targets = _build_cohort_rfm_targets(users)
    seller_state_actions = _build_seller_state_actions(orders, items)
    metrics = {
        "monthly_metrics": monthly,
        "category_metrics": category,
        "state_metrics": state,
        "rfm_segments": rfm,
        "seller_metrics": seller,
        "logistics_summary": logistics,
        "delivery_review": delivery_review,
        "cohort_retention": cohort_retention,
        "cohort_rfm_targets": cohort_rfm_targets,
        "seller_state_delivery_actions": seller_state_actions,
    }
    metrics["executive_summary"] = _build_executive_summary(metrics)
    return metrics


def _write_report(paths: ProjectPaths, metrics: dict[str, pd.DataFrame]) -> None:
    """写出简明的中文 Markdown 业务诊断报告。"""
    category = metrics["category_metrics"]
    rfm = metrics["rfm_segments"]
    cohort = metrics["cohort_retention"]
    cohort_rfm = metrics["cohort_rfm_targets"]
    state = metrics["state_metrics"]
    seller = metrics["seller_metrics"]
    actions = metrics["seller_state_delivery_actions"]
    executive = metrics["executive_summary"]
    logistics = metrics["logistics_summary"].set_index("metric")["value"]
    delivery = metrics["delivery_review"].set_index("delivery_status")
    month_1_retention = _weighted_cohort_rate(cohort, 1)
    month_3_retention = _weighted_cohort_rate(cohort, 3)
    month_6_retention = _weighted_cohort_rate(cohort, 6)
    qualified_states = int(state["risk_ranking_eligible"].sum())
    qualified_sellers = int(seller["risk_ranking_eligible"].sum())
    ranked_retention_groups = cohort_rfm[cohort_rfm["priority_rank"].notna()]
    if ranked_retention_groups.empty:
        top_retention_summary = "暂无 cohort-RFM 客群满足排名门槛。"
    else:
        top_retention = ranked_retention_groups.iloc[0]
        segment_label = RFM_SEGMENT_LABELS.get(
            str(top_retention["rfm_segment"]), str(top_retention["rfm_segment"])
        )
        top_retention_summary = (
            f"首要目标为 {top_retention['cohort_month']} 的“{segment_label}”客群，"
            f"包含 {int(top_retention['target_customers']):,} 名目标用户，"
            f"对应 R${top_retention['target_customer_gmv']:,.2f} 商品 GMV。"
        )
    if actions.empty:
        top_lane_summary = "暂无卖家—州线路满足行动门槛。"
    else:
        top_lane = actions.iloc[0]
        top_lane_summary = (
            f"首要合格线路为卖家 `{top_lane['seller_id']}` "
            f"（{top_lane['seller_state']} 至 {top_lane['customer_state']}），"
            f"{int(top_lane['completed_orders'])} 笔已完成订单中有 "
            f"{int(top_lane['late_orders'])} 笔延迟。"
        )
    executive_rows = []
    for row in executive.sort_values("priority_rank").to_dict("records"):
        signal = (
            f"{row['signal_value']:.2%}"
            if row["signal_unit"] == "rate"
            else f"{row['signal_value']:.2f} / 5"
        )
        executive_rows.append(
            f"| {int(row['priority_rank'])} | "
            f"{PRIORITY_AREA_LABELS.get(str(row['priority_area']), row['priority_area'])} | "
            f"{signal} | {int(row['scope_count']):,} "
            f"{SCOPE_UNIT_LABELS.get(str(row['scope_unit']), row['scope_unit'])} | "
            f"R${row['commercial_value']:,.2f} | "
            f"{ACTION_LABELS.get(str(row['recommended_action']), row['recommended_action'])} |"
        )
    executive_table = "\n".join(executive_rows)
    report = f"""# Olist 巴西电商运营诊断报告

## 1. 分析范围

本报告以已交付订单作为完成交易基准，趋势分析截至
`{LAST_COMPLETE_TREND_MONTH}`。数据不包含广告曝光、商品成本或平台佣金，
因此不对广告活动因果关系、广告投资回报率或会计利润作出结论。

风险排名要求每个州至少有 {MIN_STATE_RISK_ORDERS} 笔已完成订单、每个卖家至少有
{MIN_SELLER_RISK_ORDERS} 笔已完成订单、每条卖家—州线路至少有
{MIN_SELLER_STATE_ACTION_ORDERS} 笔已完成订单。这些是运营样本量门槛，
不代表统计显著性检验。

## 2. 管理指标基准

| 指标 | 数值 |
|---|---:|
| 已完成订单 | {int(logistics['completed_orders']):,} |
| 商品 GMV | R${category['merchandise_gmv'].sum():,.2f} |
| 活跃买家 | {int(rfm['buyers'].sum()):,} |
| 平均交付天数 | {logistics['average_delivery_days']:.2f} |
| 延迟交付率 | {logistics['late_delivery_rate']:.2%} |
| 平均评价得分 | {logistics['average_review_score']:.2f} / 5 |

## 3. 管理决策优先级

| 排名 | 优先领域 | 当前信号 | 历史范围 | 商品 GMV | 建议下一步行动 |
|---:|---|---:|---:|---:|---|
{executive_table}

商业价值表示诊断范围内的历史商品 GMV，不是预测增量、可挽回收入或会计利润。

## 4. 主要发现

1. **2017 年业务规模明显增长。** 月度 GMV 与订单图显示业务快速上升，
   2017 年 11 月是完整月份中的高点。这是季节性信号，不是某次营销活动产生效果的证明。
2. **用户留存是最明确的增长机会。** 加权 cohort 留存率在第 1、3、6 个月分别为
   {month_1_retention:.2%}、{month_3_retention:.2%} 和 {month_6_retention:.2%}；
   共有 {len(ranked_retention_groups)} 个 cohort-RFM 客群满足样本量和观察期门槛。
   {top_retention_summary}
3. **延迟交付与较差满意度密切相关。** 准时订单平均评分为
   {delivery.loc['on_time', 'average_review_score']:.2f}，延迟订单为
   {delivery.loc['late', 'average_review_score']:.2f}。该关系用于运营诊断，
   不能解释为因果实验结果。
4. **配送风险足够集中，可以定向处理。** 共有 {qualified_states} 个州和
   {qualified_sellers} 个卖家满足最低样本量门槛。{top_lane_summary}
5. **品类质量需要与销售规模共同管理。** 品类结果同时纳入 GMV、运费占比和评分；
   对高销量、低评分品类不能只按销售规模进行优化。

## 5. 建议行动

1. 按优先级处理 `cohort_rfm_targets.csv`。将建议旅程作为实验假设，保留留出组，
   衡量增量复购和增量 GMV，而不是只比较活动后的原始总量。
2. 按优先级处理 `seller_state_delivery_actions.csv`。当发货环节占交付时间至少
   {SELLER_DISPATCH_SHARE_THRESHOLD:.0%} 时复核卖家发货 SLA，否则优先复核承运线路容量与路由。
3. 提出选品或促销调整前，先复核高 GMV 但评分偏低或运费占比较高的重点品类。
4. 每个干预窗口结束后重新计算行动队列，同时比较延迟订单量和用户评价变化。

## 6. 生成产物

- [月度 GMV 图](analysis/monthly_gmv.svg)
- [月度订单图](analysis/monthly_orders.svg)
- [重点品类图](analysis/top_categories_gmv.svg)
- [各州延迟交付图](analysis/state_late_delivery.svg)
- [用户 cohort 留存热力图](analysis/cohort_retention.svg)
- [cohort-RFM 留存优先级图](analysis/cohort_rfm_targets.svg)
- `executive_summary.csv`：三行管理决策摘要
- `cohort_rfm_targets.csv`：满足样本量和观察期门槛的留存行动队列
- `seller_state_delivery_actions.csv`：满足门槛的线路级行动队列

排名逻辑和解释边界见 `../docs/executive_summary_methodology.md`、
`../docs/cohort_rfm_targeting_methodology.md` 和
`../docs/delivery_risk_methodology.md`。
"""
    (paths.outputs / "analysis_report.md").write_text(report, encoding="utf-8")


def generate_analysis(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """生成指标表、SVG 图表和 Markdown 报告。"""
    paths.analysis.mkdir(parents=True, exist_ok=True)
    metrics = _build_metrics(paths)
    for name, frame in metrics.items():
        frame.to_csv(paths.analysis / f"{name}.csv", index=False)
    _update_analysis_quality_report(paths, metrics)
    monthly = metrics["monthly_metrics"]
    _line_chart(
        paths.analysis / "monthly_gmv.svg",
        monthly["order_month"].tolist(),
        monthly["merchandise_gmv"].tolist(),
        "月度商品 GMV",
    )
    _line_chart(
        paths.analysis / "monthly_orders.svg",
        monthly["order_month"].tolist(),
        monthly["completed_orders"].tolist(),
        "月度已完成订单",
    )
    category = metrics["category_metrics"].head(10).sort_values("merchandise_gmv")
    _bar_chart(
        paths.analysis / "top_categories_gmv.svg",
        category["category_name"].tolist(),
        category["merchandise_gmv"].tolist(),
        "商品 GMV 最高的品类",
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
        "重点用户州延迟交付率（%）",
        color="#e05a47",
    )
    _retention_heatmap(
        paths.analysis / "cohort_retention.svg",
        metrics["cohort_retention"],
        "月度用户 cohort 留存率",
    )
    cohort_rfm = (
        metrics["cohort_rfm_targets"]
        .loc[lambda frame: frame["priority_rank"].notna()]
        .head(10)
        .sort_values("target_customers")
        .copy()
    )
    _bar_chart(
        paths.analysis / "cohort_rfm_targets.svg",
        (
            cohort_rfm["cohort_month"]
            + " | "
            + cohort_rfm["rfm_segment"].map(RFM_SEGMENT_LABELS)
        ).tolist(),
        cohort_rfm["target_customers"].astype(float).tolist(),
        "cohort-RFM 留存目标客群",
        color="#7158e2",
    )
    _write_report(paths, metrics)
    return metrics

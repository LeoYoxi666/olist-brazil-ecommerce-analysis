"""构建轻量且无外部依赖的 HTML 运营仪表盘。"""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from olist_analysis.analytics import (
    ACTION_LABELS,
    JOURNEY_LABELS,
    PRIORITY_AREA_LABELS,
    RFM_SEGMENT_LABELS,
    SCOPE_UNIT_LABELS,
)
from olist_analysis.config import COMPLETED_STATUS, ProjectPaths

# CSV 分析结果中的字段名保持稳定，仅在这里翻译展示标签，
# 使展示层调整与指标表结构保持分离。
COLUMN_LABELS = {
    "priority_rank": "优先级",
    "risk_priority_rank": "风险优先级",
    "category_name": "品类名称",
    "customer_state": "用户州",
    "seller_state": "卖家州",
    "seller_id": "卖家 ID",
    "completed_orders": "已完成订单",
    "late_orders": "延迟订单",
    "merchandise_gmv": "商品 GMV",
    "average_review_score": "平均评分",
    "late_delivery_rate": "延迟交付率",
    "average_delivery_days": "平均交付天数",
    "average_dispatch_days": "平均发货天数",
    "recommended_action": "建议行动",
    "order_month": "订单月份",
    "active_buyers": "活跃买家",
    "average_order_value": "平均订单金额",
    "cohort_month": "cohort 月份",
    "cohort_size": "cohort 用户数",
    "month_1_retention": "第 1 月留存率",
    "month_3_retention": "第 3 月留存率",
    "month_6_retention": "第 6 月留存率",
    "rfm_segment": "RFM 客群",
    "target_customers": "目标用户",
    "target_customer_gmv": "目标用户 GMV",
    "repeat_buyer_rate": "复购买家率",
    "observable_followup_months": "可观察后续月数",
    "recommended_journey": "建议用户旅程",
}


def _read(paths: ProjectPaths, name: str) -> pd.DataFrame:
    """读取一张生成的分析表。"""
    return pd.read_csv(paths.analysis / f"{name}.csv")


def _table_html(frame: pd.DataFrame, columns: list[str], limit: int) -> str:
    """将指定 DataFrame 切片转义并渲染为 HTML 表格。"""
    view = frame.loc[:, columns].head(limit).copy()
    if "rfm_segment" in view.columns:
        view["rfm_segment"] = view["rfm_segment"].map(
            lambda value: RFM_SEGMENT_LABELS.get(str(value), str(value))
        )
    if "recommended_action" in view.columns:
        view["recommended_action"] = view["recommended_action"].map(
            lambda value: ACTION_LABELS.get(str(value), str(value))
        )
    if "recommended_journey" in view.columns:
        view["recommended_journey"] = view["recommended_journey"].map(
            lambda value: JOURNEY_LABELS.get(str(value), str(value))
        )
    view.columns = [COLUMN_LABELS.get(column, column) for column in view.columns]
    return str(
        view.to_html(index=False, classes="data-table", border=0, justify="left")
    )


def _cohort_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """生成包含第 1、3、6 月留存率的紧凑 cohort 摘要表。"""
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
    """根据管理摘要表渲染面向决策的卡片。"""
    cards = []
    for row in frame.sort_values("priority_rank").to_dict("records"):
        signal = (
            f"{row['signal_value']:.2%}"
            if row["signal_unit"] == "rate"
            else f"{row['signal_value']:.2f} / 5"
        )
        area = PRIORITY_AREA_LABELS.get(
            str(row["priority_area"]), str(row["priority_area"])
        )
        scope = SCOPE_UNIT_LABELS.get(str(row["scope_unit"]), str(row["scope_unit"]))
        action = ACTION_LABELS.get(
            str(row["recommended_action"]), str(row["recommended_action"])
        )
        cards.append(
            '<article class="decision-card">'
            f'<div class="decision-rank">优先级 {int(row["priority_rank"])}</div>'
            f"<h3>{html.escape(area)}</h3>"
            f'<div class="decision-signal">{html.escape(signal)}</div>'
            f'<div class="decision-detail">{int(row["scope_count"]):,} '
            f"{html.escape(scope)}</div>"
            f'<div class="decision-detail">R${row["commercial_value"]:,.2f} '
            "历史商品 GMV</div>"
            f'<div class="decision-action">{html.escape(action)}</div>'
            "</article>"
        )
    return "".join(cards)


def build_dashboard(paths: ProjectPaths) -> Path:
    """写出独立 HTML 仪表盘并返回文件路径。"""
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
        ("已完成订单", f"{len(completed):,}"),
        ("商品 GMV", f"R${gmv:,.2f}"),
        ("活跃买家", f"{user_mart['customer_unique_id'].nunique():,}"),
        ("平均订单金额", f"R${aov:,.2f}"),
        ("复购买家率", f"{repeat_rate:.2%}"),
        ("延迟交付率", f"{late_rate:.2%}"),
        ("平均交付天数", f"{delivery_days:.2f}"),
        ("平均评价得分", f"{score:.2f} / 5"),
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
    # 小样本或测试数据可能没有任何线路达到门槛；从空 CSV 读回的列会是
    # object 类型，因此先显式转为数值，保证不同 pandas 版本都能安全舍入。
    action_view["average_dispatch_days"] = pd.to_numeric(
        action_view["average_dispatch_days"], errors="coerce"
    ).round(2)
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
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Olist 巴西电商运营仪表盘</title>
<style>
body {{ margin: 0; background: #f4f6fa; color: #172033;
font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; }}
.wrap {{ max-width: 1220px; margin: 0 auto; padding: 32px; }}
h1 {{ margin: 0 0 6px; font-size: 30px; }}
.subtitle {{ color: #596579; margin-bottom: 24px; }}
.section-title {{ font-size: 22px; margin: 28px 0 14px; }}
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
<h1>Olist 巴西电商运营仪表盘</h1>
<div class="subtitle">以已交付订单为基准；趋势窗口截至 2018 年 8 月</div>
<section class="cards">{card_html}</section>
<h2 class="section-title">1. 管理决策优先级</h2>
<section class="executive">{executive_html}</section>
<section class="grid">
<div class="panel"><h2>2. 月度商品 GMV</h2>
<img class="chart" src="analysis/monthly_gmv.svg" alt="月度商品 GMV"></div>
<div class="panel"><h2>3. 月度已完成订单</h2>
<img class="chart" src="analysis/monthly_orders.svg" alt="月度已完成订单"></div>
<div class="panel wide"><h2>4. 月度用户 cohort 留存</h2>
<img class="chart-wide" src="analysis/cohort_retention.svg"
 alt="月度用户 cohort 留存热力图"></div>
<div class="panel wide"><h2>5. cohort-RFM 留存目标客群</h2>
<img class="chart" src="analysis/cohort_rfm_targets.svg"
 alt="cohort-RFM 留存目标客群"></div>
<div class="panel"><h2>6. 商品 GMV 最高的品类</h2>
<img class="chart" src="analysis/top_categories_gmv.svg" alt="商品 GMV 最高的品类"></div>
<div class="panel"><h2>7. 各州延迟交付率</h2>
<img class="chart" src="analysis/state_late_delivery.svg" alt="各州延迟交付率"></div>
<div class="panel"><h2>8. 重点品类明细</h2>
{category_table}</div>
<div class="panel"><h2>9. 州级服务风险</h2>
{state_table}</div>
<div class="panel"><h2>10. 近期月度表现</h2>
{monthly_table}</div>
<div class="panel wide"><h2>11. cohort 留存摘要</h2>
{cohort_table}</div>
<div class="panel wide"><h2>12. cohort-RFM 留存行动队列</h2>
<div class="table-scroll action-table">{retention_target_table}</div></div>
<div class="panel wide"><h2>13. 卖家—州延迟交付行动队列</h2>
<div class="table-scroll action-table">{action_table}</div></div>
</section></main></body></html>"""
    output = paths.outputs / "dashboard.html"
    output.write_text(dashboard, encoding="utf-8")
    return output

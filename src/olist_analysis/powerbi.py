"""校验并发布 Power BI 使用的轻量聚合数据集。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import pandas as pd

from olist_analysis.config import ProjectPaths

# 每张导出表只声明 Power BI 页面真正依赖的字段；新增分析字段不会破坏刷新。
POWERBI_EXPORTS: Final[dict[str, tuple[str, ...]]] = {
    "executive_summary.csv": (
        "priority_rank",
        "priority_area",
        "signal_name",
        "signal_value",
        "signal_unit",
        "scope_count",
        "scope_unit",
        "commercial_value",
        "evidence_scope",
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

# Power BI 专用 CSV 使用中文表头，避免在 Desktop 中逐字段手工改名。
POWERBI_COLUMN_LABELS: Final[dict[str, str]] = {
    "active_buyers": "活跃买家",
    "average_customer_gmv": "平均客户商品GMV",
    "average_delivery_days": "平均送达天数",
    "average_dispatch_days": "平均发货天数",
    "average_freight_share": "平均运费占比",
    "average_item_price": "平均商品价格",
    "average_monetary": "平均客户商品GMV",
    "average_order_count": "平均订单数",
    "average_order_value": "平均订单价值",
    "average_recency_days": "平均距最近购买天数",
    "average_review_score": "平均评价得分",
    "buyers": "买家数",
    "category_name": "品类名称",
    "cohort_buyer_share": "同期群买家占比",
    "cohort_gmv_share": "同期群GMV占比",
    "cohort_month": "首购同期群月份",
    "cohort_size": "同期群人数",
    "commercial_value": "相关商品GMV",
    "completed_order_count": "已完成订单",
    "completed_orders": "已完成订单",
    "customer_state": "客户州",
    "delayed_merchandise_gmv": "延迟订单商品GMV",
    "delivery_status": "配送状态",
    "dispatch_share_of_delivery": "发货耗时占配送耗时比例",
    "evaluation_eligible": "是否符合评估条件",
    "evidence_scope": "证据范围",
    "is_late_delivery": "是否延迟",
    "late_delivery_rate": "延迟交付率",
    "late_orders": "延迟订单",
    "merchandise_gmv": "商品GMV",
    "metric": "指标",
    "minimum_order_threshold": "最低订单量门槛",
    "month_number": "留存月序",
    "negative_review_rate": "低分评价率",
    "observable_followup_months": "可观察后续月数",
    "one_time_buyers": "一次购买买家",
    "order_month": "订单月份",
    "orders": "订单数",
    "priority_area": "优先事项",
    "priority_rank": "优先级排名",
    "priority_tier": "优先级层级",
    "recommended_action": "建议行动",
    "recommended_journey": "建议客户旅程",
    "repeat_buyer_rate": "复购买家率",
    "repeat_buyers": "复购买家",
    "retention_rate": "留存率",
    "rfm_segment": "RFM客群",
    "risk_priority_rank": "风险优先级排名",
    "risk_ranking_eligible": "是否符合风险排名条件",
    "scope_count": "影响对象数",
    "scope_unit": "影响对象单位",
    "seller_id": "卖家ID",
    "seller_state": "卖家州",
    "signal_name": "核心信号",
    "signal_unit": "信号单位",
    "signal_value": "信号值",
    "target_customer_gmv": "目标客户商品GMV",
    "target_customers": "目标客户数",
    "targeting_eligible": "是否符合目标条件",
    "value": "指标值",
}

# 文件名继续使用英文以兼容代码；下列名称用于 Power BI 模型中的查询名称。
POWERBI_TABLE_LABELS: Final[dict[str, str]] = {
    "executive_summary.csv": "经营决策摘要",
    "monthly_metrics.csv": "月度经营指标",
    "rfm_segments.csv": "用户RFM分群",
    "cohort_retention.csv": "月度同期群留存",
    "cohort_rfm_targets.csv": "同期群RFM目标",
    "category_metrics.csv": "品类经营指标",
    "state_metrics.csv": "州级经营指标",
    "seller_metrics.csv": "卖家经营指标",
    "seller_state_delivery_actions.csv": "卖家州配送行动",
    "delivery_review.csv": "配送评价关联",
    "logistics_summary.csv": "物流指标摘要",
}

_RFM_LABELS: Final[dict[object, object]] = {
    "champions": "冠军客户",
    "loyal": "忠诚客户",
    "high_value": "高价值客户",
    "at_risk": "流失风险客户",
    "new_active": "新近活跃客户",
    "standard": "一般客户",
}

_CATEGORY_LABELS: Final[dict[object, object]] = {
    "agro_industry_and_commerce": "农业与商业",
    "air_conditioning": "空调",
    "art": "艺术品",
    "arts_and_craftmanship": "手工艺品",
    "audio": "音频设备",
    "auto": "汽车用品",
    "baby": "婴儿用品",
    "bed_bath_table": "床上用品与家居布艺",
    "books_general_interest": "通识图书",
    "books_imported": "进口图书",
    "books_technical": "技术图书",
    "cds_dvds_musicals": "音乐CD与DVD",
    "christmas_supplies": "圣诞用品",
    "cine_photo": "影视摄影",
    "computers": "电脑",
    "computers_accessories": "电脑配件",
    "consoles_games": "游戏机与游戏",
    "construction_tools_construction": "建筑工具",
    "construction_tools_lights": "照明工具",
    "construction_tools_safety": "安全防护工具",
    "cool_stuff": "创意用品",
    "costruction_tools_garden": "园艺施工工具",
    "costruction_tools_tools": "通用施工工具",
    "diapers_and_hygiene": "尿布与卫生用品",
    "drinks": "饮料",
    "dvds_blu_ray": "DVD与蓝光",
    "electronics": "电子产品",
    "fashio_female_clothing": "女装",
    "fashion_bags_accessories": "箱包配饰",
    "fashion_childrens_clothes": "童装",
    "fashion_male_clothing": "男装",
    "fashion_shoes": "鞋履",
    "fashion_sport": "运动时尚",
    "fashion_underwear_beach": "内衣与泳装",
    "fixed_telephony": "固定电话设备",
    "flowers": "鲜花",
    "food": "食品",
    "food_drink": "食品与饮料",
    "furniture_bedroom": "卧室家具",
    "furniture_decor": "家具装饰",
    "furniture_living_room": "客厅家具",
    "furniture_mattress_and_upholstery": "床垫与软装",
    "garden_tools": "园艺工具",
    "health_beauty": "健康美容",
    "home_appliances": "家用电器",
    "home_appliances_2": "大型家用电器",
    "home_comfort_2": "家居舒适用品（二）",
    "home_confort": "家居舒适用品",
    "home_construction": "家装建材",
    "housewares": "家居用品",
    "industry_commerce_and_business": "工商用品",
    "kitchen_dining_laundry_garden_furniture": "厨房餐厅洗衣及户外家具",
    "la_cuisine": "厨房用品",
    "luggage_accessories": "箱包旅行配件",
    "market_place": "综合市场商品",
    "music": "音乐",
    "musical_instruments": "乐器",
    "office_furniture": "办公家具",
    "party_supplies": "派对用品",
    "pc_gamer": "游戏电脑",
    "perfumery": "香水",
    "pet_shop": "宠物用品",
    "portateis_cozinha_e_preparadores_de_alimentos": "便携厨房与食品加工设备",
    "security_and_services": "安保与服务",
    "signaling_and_security": "标识与安防",
    "small_appliances": "小家电",
    "small_appliances_home_oven_and_coffee": "家用烤箱与咖啡小家电",
    "sports_leisure": "运动休闲",
    "stationery": "文具",
    "tablets_printing_image": "平板电脑与打印影像",
    "telephony": "手机通讯",
    "toys": "玩具",
    "uncategorized": "未分类",
    "watches_gifts": "手表礼品",
}

_POWERBI_VALUE_LABELS: Final[dict[str, dict[object, object]]] = {
    "category_name": _CATEGORY_LABELS,
    "delivery_status": {"on_time": "准时", "late": "延迟"},
    "evaluation_eligible": {True: "是", False: "否"},
    "is_late_delivery": {0: "准时", 1: "延迟", False: "准时", True: "延迟"},
    "metric": {
        "completed_orders": "已完成订单",
        "active_buyers": "活跃买家",
        "repeat_buyers": "复购买家",
        "repeat_buyer_rate": "复购买家率",
        "late_orders": "延迟订单",
        "late_delivery_rate": "延迟交付率",
        "average_dispatch_days": "平均发货天数",
        "average_delivery_days": "平均送达天数",
        "average_review_score": "平均评价得分",
        "delayed_merchandise_gmv": "延迟订单商品GMV",
    },
    "priority_area": {
        "retention_growth": "用户留存增长",
        "delivery_service": "配送服务",
        "category_experience": "品类体验",
    },
    "recommended_action": {
        "run_segmented_retention_holdout_tests": "开展分客群留存对照实验",
        "execute_lane_and_dispatch_reviews": "开展线路与发货专项复核",
        "review_quality_and_freight_before_growth": "增长前复核质量与运费",
        "carrier_lane_capacity_review": "复核承运线路容量与路由",
        "seller_dispatch_sla_review": "复核卖家发货SLA",
    },
    "recommended_journey": {
        "win_back_service_recovery": "服务补救与流失召回",
        "second_purchase_high_value_offer": "高价值二次购买激励",
        "category_replenishment_nurture": "品类复购培育",
        "early_second_purchase_nudge": "早期二次购买引导",
        "loyalty_reinforcement": "忠诚关系强化",
        "vip_advocacy": "VIP口碑激励",
    },
    "rfm_segment": _RFM_LABELS,
    "risk_ranking_eligible": {True: "是", False: "否"},
    "scope_unit": {
        "qualified_target_customers": "合格目标客户",
        "late_orders": "延迟订单",
        "top_gmv_below_average_categories": "高GMV且评价低于均值的品类",
    },
    "signal_name": {
        "repeat_buyer_rate": "复购买家率",
        "late_delivery_rate": "延迟交付率",
        "priority_category_review_score": "重点品类平均评价得分",
    },
    "signal_unit": {"rate": "比例", "score_out_of_5": "五分制评分"},
    "targeting_eligible": {True: "是", False: "否"},
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


def _localize_export(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    """筛选报表字段，并将所有可见表头与业务分类值转换为中文。"""
    localized = frame.loc[:, list(columns)].copy()
    if "evidence_scope" in localized.columns:
        evidence = localized["evidence_scope"].astype("string")
        evidence = evidence.str.replace(
            r"^(\d+) qualified cohort-RFM groups$",
            r"\1 个合格同期群-RFM客群",
            regex=True,
        ).str.replace(
            r"^(\d+) qualified seller-state lanes$",
            r"\1 条合格卖家-州配送线路",
            regex=True,
        )
        evidence = evidence.replace(
            {
                "top 10 GMV categories versus platform review average": (
                    "GMV前十品类与平台平均评价对比"
                )
            }
        )
        if evidence.str.contains("qualified|categories versus", na=False).any():
            raise ValueError("Missing Chinese Power BI labels for evidence_scope")
        localized["evidence_scope"] = evidence

    for column, labels in _POWERBI_VALUE_LABELS.items():
        if column in localized.columns:
            if column == "category_name":
                localized[column] = localized[column].map(labels).fillna("未翻译品类")
                continue
            unknown = set(localized[column].dropna().unique()).difference(labels)
            if unknown:
                raise ValueError(
                    f"Missing Chinese Power BI labels for {column}: "
                    f"{sorted(map(str, unknown))}"
                )
            localized[column] = localized[column].replace(labels)
    return localized.rename(columns=POWERBI_COLUMN_LABELS)


def export_powerbi_data(paths: ProjectPaths) -> dict[str, int]:
    """原子化发布全部 Power BI 聚合 CSV，并返回各表行数。"""
    # 先完整验证清单，避免中途失败后留下新旧版本混合的数据目录。
    row_counts = {
        filename: _validate_export(paths.analysis / filename, required_columns)
        for filename, required_columns in POWERBI_EXPORTS.items()
    }

    paths.powerbi_data.mkdir(parents=True, exist_ok=True)
    for filename, required_columns in POWERBI_EXPORTS.items():
        source = paths.analysis / filename
        destination = paths.powerbi_data / filename
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        try:
            frame = pd.read_csv(source)
            localized = _localize_export(frame, required_columns)
            # 使用 UTF-8 BOM，确保 Windows Power BI 自动识别中文且不出现乱码。
            localized.to_csv(temporary, index=False, encoding="utf-8-sig")
            os.replace(temporary, destination)
        finally:
            # 仅在复制或替换失败时才会遗留临时文件。
            if temporary.exists():
                temporary.unlink()

    return row_counts

"""集中管理项目路径和已记录的业务分析参数。

业务阈值统一放在这里，确保数据管道、分析、测试和文档采用同一套定义。
修改这些数值可能改变报告人群和排序结果，因此必须同步更新相关方法文档与测试。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class ProjectPaths:
    """各工作流阶段共用的项目相对路径。"""

    root: Path  # 项目根目录，是调用方唯一需要提供的路径。
    raw: Path  # 数据集提供的不可变原始 CSV 文件目录。
    processed: Path  # 可复现的清洗表、数据集市和 SQLite 数据库目录。
    outputs: Path  # 生成的报告、仪表盘和质量摘要目录。
    analysis: Path  # 生成的指标表和 SVG 图表目录。
    powerbi: Path  # Power BI 搭建说明、主题和刷新入口目录。
    powerbi_data: Path  # 供 Power BI Import 模式读取的轻量聚合 CSV 目录。

    @classmethod
    def from_root(cls, root: Path) -> "ProjectPaths":
        """根据项目根目录构造所有标准路径。"""
        return cls(
            root=root,
            raw=root / "data" / "raw",
            processed=root / "data" / "processed",
            outputs=root / "outputs",
            analysis=root / "outputs" / "analysis",
            powerbi=root / "powerbi",
            powerbi_data=root / "powerbi" / "data",
        )


# 原始数据在 2018 年 9 月中途结束，因此趋势分析排除该不完整月份。
LAST_COMPLETE_TREND_MONTH: Final = "2018-08"

# 只有已交付订单才计入完成交易口径。
COMPLETED_STATUS: Final = "delivered"

# 五分制中，1 分或 2 分定义为负面评价。
NEGATIVE_REVIEW_MAX_SCORE: Final = 2

# 州进入配送风险排名前必须达到的最少已完成订单数。
MIN_STATE_RISK_ORDERS: Final = 100

# 卖家进入配送风险排名前必须达到的最少已完成订单数。
MIN_SELLER_RISK_ORDERS: Final = 20

# 卖家—用户州线路进入行动队列前必须达到的最少订单数。
MIN_SELLER_STATE_ACTION_ORDERS: Final = 10

# 发货阶段占总配送时间至少 35% 时，优先检查卖家发货 SLA。
SELLER_DISPATCH_SHARE_THRESHOLD: Final = 0.35

# cohort-RFM 客群进入目标队列前必须达到的最少买家数。
MIN_COHORT_RFM_BUYERS: Final = 100

# 至少保留三个可观察后续月份，目标客群才具备效果评估条件。
COHORT_RFM_EVALUATION_MONTHS: Final = 3

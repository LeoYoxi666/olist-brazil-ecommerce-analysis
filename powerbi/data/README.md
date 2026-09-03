# Power BI 聚合数据说明

本目录由 `python scripts/export_powerbi.py` 自动生成，数据来源是
`outputs/analysis/` 中经过测试的业务指标表。不要手工修改 CSV。

## 1. 数据清单

| 文件 | 行数 | 粒度 | 主要用途 |
|---|---:|---|---|
| `executive_summary.csv` | 3 | 一项管理优先级一行 | 经营总览与行动建议 |
| `monthly_metrics.csv` | 23 | 一个月一行 | GMV、订单、买家和客单价趋势 |
| `rfm_segments.csv` | 6 | 一个 RFM 分群一行 | 用户规模、价值与复购结构 |
| `cohort_retention.csv` | 219 | cohort 月份与观察月组合一行 | 留存矩阵与曲线 |
| `cohort_rfm_targets.csv` | 88 | 一个 cohort-RFM 组合一行 | 留存行动客群排序 |
| `category_metrics.csv` | 74 | 一个标准化品类一行 | GMV、评价与运费负担 |
| `state_metrics.csv` | 27 | 一个用户州一行 | 地区业务和配送风险 |
| `seller_metrics.csv` | 2,970 | 一个卖家一行 | 卖家规模、评价和配送表现 |
| `seller_state_delivery_actions.csv` | 1,886 | 一条卖家—用户州线路一行 | 配送复核行动队列 |
| `delivery_review.csv` | 2 | 一种准时状态一行 | 延迟与评价关系 |
| `logistics_summary.csv` | 10 | 一个物流指标一行 | 交付周期摘要 |

## 2. 使用限制

这些 CSV 是 Olist 数据集的聚合衍生结果，只用于非商业学习、作品集展示和研究。
分享时应署名 Olist，并遵守
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 的非商业和相同方式共享要求。

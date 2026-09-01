# Portfolio and Interview Summary

Use the following descriptions as concise, evidence-based project summaries.
The business values are historical analytical scopes, not measured causal
uplift or accounting profit.

## 中文简历版

- 基于 9 张 Olist 巴西电商原始数据表，使用 Python、pandas 与 SQLite
  搭建可复现的端到端分析流程，产出 13 张清洗/主题数据表、12 项数据质量检查、
  11 张业务分析表及独立 HTML 运营仪表盘。
- 围绕 96,478 个已交付订单和 R$13.22M 商品 GMV，完成用户 RFM、月度留存、
  品类、卖家、地区、配送和评价分析，识别 41 个合格 cohort-RFM 客群及 1,886
  条卖家—州配送风险行动队列。
- 修正并测试 RFM 并列值和一次购买用户误分类问题，引入样本量门槛、影响优先级、
  留存 holdout 建议和商业解释边界；通过 pytest、Black、isort、Flake8、mypy
  与 GitHub Actions CI 保证可维护性。

## English resume version

- Built a reproducible end-to-end Olist marketplace analytics pipeline using
  Python, pandas, and SQLite, transforming nine raw datasets into 13 clean and
  analytical tables, 12 data-quality checks, 11 business outputs, and a
  standalone HTML operations dashboard.
- Analyzed 96,478 delivered orders and R$13.22M in merchandise GMV across RFM,
  cohort retention, categories, sellers, regions, delivery, and reviews;
  produced 41 qualified cohort-RFM target groups and 1,886 seller-state
  delivery-risk action lanes.
- Corrected tie-sensitive RFM scoring and one-time-buyer misclassification,
  added volume guards and impact-first prioritization, and automated pytest,
  Black, isort, Flake8, and mypy checks through GitHub Actions CI.

## 30-second interview answer — Chinese

这个项目的目标不是只做几张图，而是把 9 张相互关联的电商原始表变成一个可复现、
可解释、可以继续迭代的运营分析项目。我先建立清洗、关联、质量检查和 SQLite 数据层，
再围绕已交付订单分析用户留存、RFM、品类、卖家和配送表现。过程中我发现传统分位数
RFM 会把相同的一次购买用户随机分到不同等级，因此改成并列值稳定的评分规则并增加
测试。最终项目给出了 41 个留存目标客群和 1,886 条配送行动队列，并通过在线仪表盘、
方法文档和 CI 保证结果可展示、可复现、可维护。

## 30-second interview answer — English

I treated the project as an operational analytics product rather than a single
notebook. I built a reproducible data and quality layer for nine related Olist
datasets, then analyzed delivered orders across retention, RFM, categories,
sellers, geography, and delivery performance. One important issue I found was
that naive quantile RFM scoring could assign identical one-time buyers to
different segments, so I replaced it with tie-stable rules and added tests.
The final output includes 41 qualified retention target groups, 1,886 delivery
action lanes, a public dashboard, documented metric definitions, and automated
CI checks.

## Evidence to show in an interview

1. Start with the public dashboard and explain the three executive priorities.
2. Open the data dictionary and methodology documents to show metric control.
3. Explain the tie-stable RFM correction and its automated tests.
4. Show the cohort-RFM and seller-state action tables as decision outputs.
5. Show the GitHub Actions runs to demonstrate reproducibility and engineering
   discipline.

## Interpretation boundary

Do not describe the scoped GMV as revenue recovered, predicted uplift, profit,
or campaign ROI. The dataset supports operational prioritization and test
design, but it does not contain campaign exposure, advertising spend, product
cost, commission, or browsing-event data.

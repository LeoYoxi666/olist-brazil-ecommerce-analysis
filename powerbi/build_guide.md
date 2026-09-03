# Olist Power BI 仪表盘搭建指南

本指南将现有 Python 分析结果搭建成 6 页中文 Power BI 运营看板。页面结构参考淘宝
用户分析项目的工作方式：使用经过验证的聚合数据、统一主题、明确筛选器和可复现刷新
流程，不直接在 Power BI 中清洗原始大表。

## 1. 导入与模型设置

### 1.1 刷新聚合数据

在项目根目录运行：

```powershell
.\powerbi\refresh_exports.ps1
```

### 1.2 导入 CSV

在 Power BI Desktop 中依次选择 **主页 → 获取数据 → 文本/CSV**，导入
`powerbi/data/` 中除 `README.md` 外的全部 11 张 CSV。选择 Import 模式。

### 1.3 关闭自动关系

这些表分别是月度、品类、州、卖家、RFM 和 cohort 等不同聚合粒度。进入模型视图，
删除自动建立的关系，并在设置中关闭当前文件的自动关系检测，避免多对多关系导致重复
计算。每一页只使用对应粒度的数据表。

### 1.4 导入主题与度量值

通过 **视图 → 主题 → 浏览主题** 导入 `powerbi/olist_theme.json`。然后按照
`powerbi/measures.dax` 创建度量值，并完成金额、百分比和整数格式设置。

## 2. 页面一：经营总览

### 2.1 页面目标

让面试官或业务负责人在一页内看到经营规模、用户价值、配送风险和三项优先行动。

### 2.2 视觉对象

| 位置 | 视觉对象 | 表与字段 |
|---|---|---|
| 顶部 | 6 个卡片 | `已完成订单`、`商品 GMV`、`活跃买家`、`平均订单价值`、`复购买家率`、`延迟交付率` |
| 中部左 | 折线图 | `monthly_metrics[order_month]`、`商品 GMV` |
| 中部右 | 折线图 | `monthly_metrics[order_month]`、`已完成订单` |
| 底部 | 表格 | `executive_summary` 的优先级、信号、影响范围、商业金额和建议行动 |

页面筛选器只保留月份范围。商品 GMV 使用 `R$`，比例保留两位小数。

## 3. 页面二：月度经营趋势

### 3.1 视觉对象

- 折线和簇状柱形组合图：X 轴 `order_month`，柱为 `completed_orders`，线为
  `merchandise_gmv`。
- 折线图：X 轴 `order_month`，值为 `active_buyers` 和 `average_order_value`。
- 月份切片器：`order_month`，默认选择完整趋势窗口至 2018 年 8 月。
- 明细表：月份、订单、GMV、活跃买家和平均订单价值。

### 3.2 解读限制

2018 年 9 月为不完整月份，已在 Python 分析层排除。趋势峰值可以支持季节性资源规划，
但不能证明营销活动造成了增长。

## 4. 页面三：用户价值与留存

### 4.1 RFM 分群

- 横向条形图：Y 轴 `rfm_segment`，X 轴 `buyers`。
- 组合图：各分群 `merchandise_gmv` 与 `average_recency_days`。
- 卡片：`活跃买家`、`复购买家`、`复购买家率`。
- RFM 分群切片器：`rfm_segment`。

### 4.2 cohort 留存

- 矩阵：行 `cohort_month`，列 `month_number`，值 `加权 cohort 留存率`。
- 对 `retention_rate` 或度量值应用由浅蓝到深蓝的背景色条件格式。
- 折线图：X 轴 `month_number`，图例 `cohort_month`，值 `加权 cohort 留存率`。

### 4.3 留存行动客群

- 表格：`priority_rank`、`cohort_month`、`rfm_segment`、`priority_tier`、
  `target_customers`、`target_customer_gmv`、`recommended_journey`。
- 页面筛选条件：`targeting_eligible = TRUE`。
- 卡片：`合格目标客户`、`合格目标客户 GMV`。

留存率是精确月留存，不是累计生存率；近期 cohort 的未来月份为空值，不能填成 0。

## 5. 页面四：品类销售与体验

### 5.1 视觉对象

- 横向条形图：Top 10 `category_name`，按 `merchandise_gmv` 降序。
- 散点图：X 轴 `average_review_score`，Y 轴 `merchandise_gmv`，气泡大小
  `completed_orders`，详细信息 `category_name`。
- 横向条形图：Top 10 品类的 `average_freight_share`。
- 品类表格：订单、GMV、平均商品价格、运费占比和评价得分。

高 GMV 且评价低于平台均值的品类优先检查质量与物流，不应直接解释为推广机会。

## 6. 页面五：区域配送与评价

### 6.1 州级地图与排名

- 填充地图：位置 `customer_state`，颜色饱和度 `late_delivery_rate`，工具提示包含
  `completed_orders`、`merchandise_gmv`、`average_delivery_days` 和
  `average_review_score`。
- 风险条形图：按 `late_orders` 排序，只保留 `risk_ranking_eligible = TRUE`。
- 州代码切片器：`customer_state`。

将州代码的数据类别设置为“州或省”，并在工具提示或页面说明中标注国家为 Brazil，
避免 Power BI 把两位代码解析到其他国家。

### 6.2 延迟与评价关系

- 簇状柱形图：轴 `delivery_status`，值 `average_review_score`。
- 折线或卡片：`negative_review_rate`。
- 卡片：`延迟订单`、`延迟交付率`、`平均评价得分`。

该页面展示诊断性关联，不能将低评分全部归因于配送延迟。

## 7. 页面六：卖家与配送行动

### 7.1 卖家风险

- 散点图：X 轴 `late_delivery_rate`，Y 轴 `merchandise_gmv`，气泡大小
  `completed_order_count`，详细信息 `seller_id`。
- 卖家州切片器：`seller_state`。
- 页面筛选条件：`risk_ranking_eligible = TRUE`。
- 卡片：`合格风险卖家`。

### 7.2 卖家—州行动队列

- 表格：`priority_rank`、`seller_id`、`seller_state`、`customer_state`、
  `completed_orders`、`late_orders`、`delayed_merchandise_gmv`、
  `late_delivery_rate`、`recommended_action`。
- 按 `priority_rank` 升序；对延迟率和延迟 GMV 使用条件格式。
- 行动类型切片器：`recommended_action`。
- 卡片：`行动线路数`。

行动标签只表示排查起点：发货占比较高时优先复核卖家 SLA，否则优先检查承运线路容量
和路由，不能直接用于责任认定。

## 8. 统一页面样式

1. 画布使用 16:9，背景色 `#F4F6FA`，卡片使用白色圆角背景。
2. 主色使用 `#2F6FED`，正常状态使用 `#14B8A6`，风险强调使用 `#D86A52`。
3. 页面标题统一为“模块序号｜中文业务主题”，左上对齐。
4. 所有金额保留两位小数并显示 `R$`；百分比保留两位；数量使用千位分隔符。
5. 每页右上角放置“数据截至 2018-08”和“已交付订单口径”。
6. 表格默认按业务优先级排序，不以字母顺序代替风险排序。

## 9. 发布前验收

- 6 个页面名称、标题、字段标签和工具提示均为中文。
- 总订单为 96,478，商品 GMV 约为 R$13.22M，活跃买家为 93,358。
- 复购买家率为 3.00%，延迟交付率为 8.11%，平均评价得分约为 4.16。
- 月度趋势最后一个完整月份为 2018-08。
- cohort 矩阵的未来不可观察月份保持为空。
- 州代码保持 `SP`、`RJ`、`MG` 等原始缩写，不被翻译。
- 行动队列只包含达到 10 笔订单门槛的卖家—州线路。
- 点击“刷新”后 11 张表均成功加载，页面无视觉对象错误。
- 保存 `.pbix` 后，在 `docs/assets/` 导出 6 张页面截图并补入 Markdown 项目报告。

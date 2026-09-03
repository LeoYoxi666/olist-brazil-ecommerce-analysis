# Olist Power BI 可视化数据层

本目录提供与 Python 分析口径一致的 Power BI 聚合数据、刷新入口、DAX 度量值、
主题文件和中文搭建说明。Power BI 只负责交互展示，不在报表内部重新定义业务规则。

## 1. 当前状态

- `data/` 包含 11 张经过字段校验的轻量聚合 CSV，总量小于 1 MB。
- `refresh_exports.ps1` 可以从九张原始表重新运行完整流程并刷新全部聚合数据。
- `measures.dax` 提供总订单、GMV、复购、配送和评价等统一度量值。
- `olist_theme.json` 提供与现有 HTML 仪表盘一致的蓝色主视觉和风险强调色。
- `build_guide.md` 定义 6 个中文页面的字段、筛选器、视觉对象和验收规则。
- 本机当前未安装 Power BI Desktop，因此 `.pbix` 尚未生成；安装后按搭建指南导入即可。

## 2. 目录结构

```text
powerbi/
|-- README.md
|-- build_guide.md
|-- measures.dax
|-- olist_theme.json
|-- refresh_exports.ps1
`-- data/
    |-- README.md
    `-- 11 张聚合 CSV
```

## 3. 刷新数据

先将九张 Olist 原始 CSV 放入 `data/raw/`，并确保项目虚拟环境已经安装依赖。
在项目根目录执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\powerbi\refresh_exports.ps1
```

脚本依次运行数据处理、业务分析和 Power BI 导出。只有全部来源表通过字段检查后，
才会逐张替换 `powerbi/data/` 中的公开数据。

如果分析结果已经是最新版本，可以只执行：

```powershell
python scripts/export_powerbi.py
```

## 4. Power BI 导入原则

在 Power BI Desktop 中选择 **主页 → 获取数据 → 文本/CSV**，导入 `data/` 中的
11 张 CSV，使用 Import 模式。各表统计粒度不同，默认不要自动创建表关系；每个页面
使用对应聚合表，避免跨粒度重复汇总。

导入后完成以下设置：

1. 将金额字段设置为货币 `R$` 或小数两位。
2. 将名称包含 `rate`、`share` 的字段设置为百分比、小数两位。
3. 将 `order_month`、`cohort_month` 转为日期或保留 `YYYY-MM` 文本并升序排序。
4. 将 `priority_rank`、`risk_priority_rank` 和 `month_number` 设置为整数且不汇总。
5. 将州代码、卖家 ID、RFM 分群和行动标签设置为文本且不汇总。
6. 删除 Power BI 自动检测的关系，除非后续建立经过验证的共享维度表。

## 5. 数据刷新责任边界

不要直接修改 `powerbi/data/*.csv` 中的值。业务口径变化应先修改
`src/olist_analysis/`、测试和方法文档，然后依次重新生成分析结果和 Power BI 数据。
Power BI 仅处理筛选、聚合和展示，不承担清洗、RFM 分群、cohort 资格判断或配送风险
排序。

## 6. 数据与代码许可

`powerbi/data/` 是 Olist 原始数据的聚合衍生结果，使用和分享时遵循原数据集的
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 条款。
刷新代码、DAX、主题和搭建说明属于本项目原创内容，按仓库根目录的 MIT License 使用。

"""完整工作流、异常输入和版本化链接的集成测试。"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from olist_analysis.analytics import _build_cohort_rfm_targets, generate_analysis
from olist_analysis.config import ProjectPaths
from olist_analysis.dashboard import build_dashboard
from olist_analysis.pipeline import (
    FILE_NAMES,
    _clean_sources,
    build_analysis_tables,
    persist_tables,
)
from olist_analysis.powerbi import (
    POWERBI_COLUMN_LABELS,
    POWERBI_EXPORTS,
    POWERBI_TABLE_LABELS,
    export_powerbi_data,
)


def _sample_sources() -> dict[str, pd.DataFrame]:
    """构造覆盖复购、准时、延迟和品类回退规则的最小原始数据集。"""
    return {
        "customers": pd.DataFrame(
            {
                "customer_id": ["c1", "c2", "c3", "c4"],
                "customer_unique_id": ["u1", "u1", "u2", "u3"],
                "customer_zip_code_prefix": pd.Series(
                    ["1000", "1000", "2000", "3000"], dtype="string"
                ),
                "customer_city": ["sao paulo", "sao paulo", "rio", "belo"],
                "customer_state": ["SP", "SP", "RJ", "MG"],
            }
        ),
        "geolocation": pd.DataFrame(
            {
                "geolocation_zip_code_prefix": pd.Series(
                    ["1000", "1000", "2000", "3000"], dtype="string"
                ),
                "geolocation_lat": [-23.5, -23.6, -22.9, -19.9],
                "geolocation_lng": [-46.6, -46.7, -43.2, -43.9],
                "geolocation_city": [" Sao Paulo ", "sao paulo", "Rio", "Belo"],
                "geolocation_state": ["sp", "SP", "rj", "mg"],
            }
        ),
        "items": pd.DataFrame(
            {
                "order_id": ["o1", "o2", "o3", "o4"],
                "order_item_id": [1, 1, 1, 1],
                "product_id": ["p1", "p2", "p1", "p3"],
                "seller_id": ["s1", "s1", "s2", "s2"],
                "shipping_limit_date": [
                    "2018-01-04",
                    "2018-03-04",
                    "2018-02-04",
                    "2018-07-04",
                ],
                "price": [100.0, 80.0, 50.0, 120.0],
                "freight_value": [10.0, 8.0, 5.0, 12.0],
            }
        ),
        "payments": pd.DataFrame(
            {
                "order_id": ["o1", "o2", "o3", "o4"],
                "payment_sequential": [1, 1, 1, 1],
                "payment_type": ["credit_card", "voucher", "credit_card", "boleto"],
                "payment_installments": [1, 1, 2, 1],
                "payment_value": [110.0, 88.0, 55.0, 132.0],
            }
        ),
        "reviews": pd.DataFrame(
            {
                "review_id": ["r1", "r2", "r3", "r4"],
                "order_id": ["o1", "o2", "o3", "o4"],
                "review_score": [5, 2, 4, 1],
                "review_comment_title": [pd.NA, "late", pd.NA, "late"],
                "review_comment_message": [pd.NA, "slow", pd.NA, "slow"],
                "review_creation_date": [
                    "2018-01-08",
                    "2018-03-20",
                    "2018-02-09",
                    "2018-07-20",
                ],
                "review_answer_timestamp": [
                    "2018-01-09",
                    "2018-03-21",
                    "2018-02-10",
                    "2018-07-21",
                ],
            }
        ),
        "orders": pd.DataFrame(
            {
                "order_id": ["o1", "o2", "o3", "o4"],
                "customer_id": ["c1", "c2", "c3", "c4"],
                "order_status": ["delivered", "delivered", "delivered", "delivered"],
                "order_purchase_timestamp": [
                    "2018-01-01",
                    "2018-03-01",
                    "2018-02-01",
                    "2018-07-01",
                ],
                "order_approved_at": [
                    "2018-01-02",
                    "2018-03-02",
                    "2018-02-02",
                    "2018-07-02",
                ],
                "order_delivered_carrier_date": [
                    "2018-01-03",
                    "2018-03-05",
                    "2018-02-03",
                    "2018-07-05",
                ],
                "order_delivered_customer_date": [
                    "2018-01-06",
                    "2018-03-18",
                    "2018-02-07",
                    "2018-07-18",
                ],
                "order_estimated_delivery_date": [
                    "2018-01-07",
                    "2018-03-15",
                    "2018-02-08",
                    "2018-07-15",
                ],
            }
        ),
        "products": pd.DataFrame(
            {
                "product_id": ["p1", "p2", "p3"],
                "product_category_name": ["beleza", "sem_traducao", pd.NA],
            }
        ),
        "sellers": pd.DataFrame(
            {
                "seller_id": ["s1", "s2"],
                "seller_zip_code_prefix": pd.Series(["1000", "2000"], dtype="string"),
                "seller_city": ["sao paulo", "rio"],
                "seller_state": ["SP", "RJ"],
            }
        ),
        "translations": pd.DataFrame(
            {
                "product_category_name": ["beleza"],
                "product_category_name_english": ["health_beauty"],
            }
        ),
    }


def _write_raw_fixture(root: Path) -> ProjectPaths:
    """按项目约定写出九张临时原始 CSV，并返回标准路径。"""
    paths = ProjectPaths.from_root(root)
    paths.raw.mkdir(parents=True)
    for name, frame in _sample_sources().items():
        frame.to_csv(paths.raw / FILE_NAMES[name], index=False)
    return paths


def test_small_dataset_runs_complete_workflow(tmp_path: Path) -> None:
    """最小九表数据应贯通清洗、建模、分析、报告和仪表盘。"""
    paths = _write_raw_fixture(tmp_path)

    tables = build_analysis_tables(paths)
    quality = persist_tables(paths, tables)
    metrics = generate_analysis(paths)
    powerbi_tables = export_powerbi_data(paths)
    dashboard = build_dashboard(paths)

    assert len(tables) == 13
    assert len(metrics) == 11
    assert len(powerbi_tables) == 11
    assert quality["checks"]["orders_duplicate_key_rows"] == 0
    assert quality["database"] == "data/processed/olist_analysis.sqlite"
    assert dashboard.is_file()
    assert (paths.outputs / "analysis_report.md").is_file()
    assert len(list(paths.analysis.glob("*.svg"))) == 6
    assert len(list(paths.powerbi_data.glob("*.csv"))) == 11

    with sqlite3.connect(paths.processed / "olist_analysis.sqlite") as connection:
        table_count = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'"
        ).fetchone()[0]
    assert table_count == 13

    report = json.loads(
        (paths.outputs / "data_quality_report.json").read_text(encoding="utf-8")
    )
    assert "analysis_checks" in report
    assert "Olist 巴西电商运营仪表盘" in dashboard.read_text(encoding="utf-8")


def test_cleaning_coerces_bad_values_and_preserves_fallbacks() -> None:
    """异常日期和金额应显式转为空值，邮编及品类回退规则应保持稳定。"""
    sources = _sample_sources()
    sources["items"].loc[0, "shipping_limit_date"] = "not-a-date"
    sources["items"]["price"] = sources["items"]["price"].astype("object")
    sources["items"].loc[0, "price"] = "not-a-number"
    sources["payments"]["payment_value"] = sources["payments"]["payment_value"].astype(
        "object"
    )
    sources["payments"].loc[0, "payment_value"] = "invalid"

    cleaned = _clean_sources(sources)
    products = cleaned["products"].set_index("product_id")

    assert cleaned["customers"].loc[0, "customer_zip_code_prefix"] == "01000"
    assert pd.isna(cleaned["items"].loc[0, "shipping_limit_date"])
    assert pd.isna(cleaned["items"].loc[0, "price"])
    assert pd.isna(cleaned["payments"].loc[0, "payment_value"])
    assert products.loc["p2", "category_name"] == "sem_traducao"
    assert products.loc["p2", "category_translation_status"] == "untranslated"
    assert products.loc["p3", "category_name"] == "uncategorized"


def test_missing_required_analysis_columns_fail_clearly() -> None:
    """关键输入字段缺失时应给出可定位问题的异常，而不是静默生成错误结果。"""
    incomplete_users = pd.DataFrame(
        {
            "customer_unique_id": ["u1"],
            "first_purchase_at": ["2018-01-01"],
        }
    )

    with pytest.raises(ValueError, match="Missing cohort-RFM columns"):
        _build_cohort_rfm_targets(incomplete_users)


def test_powerbi_export_rejects_missing_required_columns(tmp_path: Path) -> None:
    """Power BI 来源字段缺失时必须中止，避免发布结构错误的数据。"""
    paths = ProjectPaths.from_root(tmp_path)
    paths.analysis.mkdir(parents=True)

    for filename, columns in POWERBI_EXPORTS.items():
        pd.DataFrame([{column: 1 for column in columns}]).to_csv(
            paths.analysis / filename, index=False
        )

    broken_name = "monthly_metrics.csv"
    pd.DataFrame({"order_month": ["2018-01"]}).to_csv(
        paths.analysis / broken_name, index=False
    )

    with pytest.raises(ValueError, match="Missing Power BI columns"):
        export_powerbi_data(paths)
    assert not paths.powerbi_data.exists()


def test_versioned_local_links_and_dashboard_assets_exist() -> None:
    """README、报告和仪表盘引用的本地版本化资源必须真实存在。"""
    root = Path(__file__).resolve().parents[1]
    markdown_files = [root / "README.md", root / "outputs" / "analysis_report.md"]
    markdown_files.extend(sorted((root / "docs").glob("*.md")))
    markdown_files.extend(sorted((root / "powerbi").rglob("*.md")))
    link_pattern = re.compile(r"!?\[[^]]*]\(([^)]+)\)")

    for document in markdown_files:
        for raw_target in link_pattern.findall(document.read_text(encoding="utf-8")):
            target = raw_target.split(maxsplit=1)[0].strip("<>")
            parsed = urlparse(target)
            if parsed.scheme or target.startswith("#"):
                continue
            linked_path = document.parent / unquote(parsed.path)
            assert linked_path.exists(), f"失效链接：{document} -> {target}"

    dashboard = root / "outputs" / "dashboard.html"
    source_pattern = re.compile(r'\bsrc="([^"]+)"')
    for target in source_pattern.findall(dashboard.read_text(encoding="utf-8")):
        parsed = urlparse(target)
        if parsed.scheme:
            continue
        assert (
            dashboard.parent / unquote(parsed.path)
        ).exists(), f"仪表盘资源不存在：{target}"


def test_versioned_powerbi_assets_are_complete() -> None:
    """版本化 Power BI 数据、中文模型、主题和搭建说明必须保持完整可读。"""
    root = Path(__file__).resolve().parents[1]
    data_directory = root / "powerbi" / "data"

    actual_exports = {path.name for path in data_directory.glob("*.csv")}
    assert actual_exports == set(POWERBI_EXPORTS)
    for filename, required_columns in POWERBI_EXPORTS.items():
        columns = set(pd.read_csv(data_directory / filename, nrows=0).columns)
        expected_columns = {
            POWERBI_COLUMN_LABELS[column] for column in required_columns
        }
        assert columns == expected_columns

    assert set(POWERBI_TABLE_LABELS) == set(POWERBI_EXPORTS)
    assert all(
        re.search(r"[\u4e00-\u9fff]", label) for label in POWERBI_TABLE_LABELS.values()
    )

    categories = pd.read_csv(data_directory / "category_metrics.csv")
    assert "健康美容" in set(categories["品类名称"])
    assert "health_beauty" not in set(categories["品类名称"])

    rfm = pd.read_csv(data_directory / "rfm_segments.csv")
    assert set(rfm["RFM客群"]) == {
        "一般客户",
        "冠军客户",
        "忠诚客户",
        "新近活跃客户",
        "流失风险客户",
        "高价值客户",
    }

    delivery = pd.read_csv(data_directory / "delivery_review.csv")
    assert set(delivery["配送状态"]) == {"准时", "延迟"}

    theme = json.loads(
        (root / "powerbi" / "olist_theme.json").read_text(encoding="utf-8")
    )
    assert theme["name"] == "Olist 运营分析"
    guide = (root / "powerbi" / "build_guide.md").read_text(encoding="utf-8")
    assert all(f"页面{number}" in guide for number in "一二三四五六七八")
    assert "字段窗格中不出现 snake_case 字段" in guide

    measures = (root / "powerbi" / "measures.dax").read_text(encoding="utf-8")
    assert "'月度经营指标'[已完成订单]" in measures
    assert "'monthly_metrics'" not in measures

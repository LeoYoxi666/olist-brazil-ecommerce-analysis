"""校验并刷新 Power BI 使用的聚合 CSV 数据层。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from olist_analysis.config import ProjectPaths
from olist_analysis.powerbi import export_powerbi_data


def main() -> None:
    """将最新分析结果发布到项目的 Power BI 数据目录。"""
    paths = ProjectPaths.from_root(PROJECT_ROOT)
    exported = export_powerbi_data(paths)
    print(f"Exported {len(exported)} Power BI tables to {paths.powerbi_data}")


if __name__ == "__main__":
    main()

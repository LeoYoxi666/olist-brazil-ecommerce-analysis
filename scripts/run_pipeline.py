"""运行 Olist 数据清洗与数据集市管道。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from olist_analysis.config import ProjectPaths
from olist_analysis.pipeline import build_analysis_tables, persist_tables


def main() -> None:
    """构建并持久化全部清洗表和数据集市。"""
    paths = ProjectPaths.from_root(PROJECT_ROOT)
    tables = build_analysis_tables(paths)
    report = persist_tables(paths, tables)
    print(f"Built {len(tables)} tables in {report['database']}")
    print(f"Quality checks: {len(report['checks'])}")


if __name__ == "__main__":
    main()

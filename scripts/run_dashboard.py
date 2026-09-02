"""构建独立 HTML 运营仪表盘。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from olist_analysis.config import ProjectPaths
from olist_analysis.dashboard import build_dashboard


def main() -> None:
    """根据分析结果生成 HTML 仪表盘。"""
    output = build_dashboard(ProjectPaths.from_root(PROJECT_ROOT))
    print(f"Generated {output}")


if __name__ == "__main__":
    main()

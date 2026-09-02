"""Generate analysis tables, charts, and the Chinese business report."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from olist_analysis.analytics import generate_analysis
from olist_analysis.config import ProjectPaths


def main() -> None:
    """Run the analysis stage from processed project data."""
    paths = ProjectPaths.from_root(PROJECT_ROOT)
    metrics = generate_analysis(paths)
    print(f"Generated {len(metrics)} analysis tables in {paths.analysis}")


if __name__ == "__main__":
    main()

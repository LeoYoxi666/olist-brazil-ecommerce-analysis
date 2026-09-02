"""Centralize project paths and documented business-analysis parameters.

Business thresholds live here so the pipeline, analysis, tests, and
documentation use one definition. Changing one of these values can change
reported populations and rankings, so update the related methodology document
and tests at the same time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class ProjectPaths:
    """Repository-relative locations shared by every workflow stage."""

    root: Path  # Repository root; the only path callers need to provide.
    raw: Path  # Immutable source CSV files supplied by the dataset.
    processed: Path  # Reproducible cleaned tables, marts, and SQLite database.
    outputs: Path  # Generated reports, dashboard, and quality summary.
    analysis: Path  # Generated metric tables and SVG chart assets.

    @classmethod
    def from_root(cls, root: Path) -> "ProjectPaths":
        """Create project paths from a repository root."""
        return cls(
            root=root,
            raw=root / "data" / "raw",
            processed=root / "data" / "processed",
            outputs=root / "outputs",
            analysis=root / "outputs" / "analysis",
        )


# Exclude September 2018 because the source dataset ends during that month.
LAST_COMPLETE_TREND_MONTH: Final = "2018-08"

# Treat only delivered orders as completed commercial transactions.
COMPLETED_STATUS: Final = "delivered"

# Scores of 1 or 2 on the five-point scale define a negative review.
NEGATIVE_REVIEW_MAX_SCORE: Final = 2

# Minimum completed orders required before a state enters risk ranking.
MIN_STATE_RISK_ORDERS: Final = 100

# Minimum completed orders required before a seller enters risk ranking.
MIN_SELLER_RISK_ORDERS: Final = 20

# Minimum seller-to-customer-state orders required for an action lane.
MIN_SELLER_STATE_ACTION_ORDERS: Final = 10

# Dispatch consuming at least 35% of delivery time triggers seller SLA review.
SELLER_DISPATCH_SHARE_THRESHOLD: Final = 0.35

# Minimum buyers required for a cohort-RFM group to enter the target queue.
MIN_COHORT_RFM_BUYERS: Final = 100

# Require three observable months so a target group can support evaluation.
COHORT_RFM_EVALUATION_MONTHS: Final = 3

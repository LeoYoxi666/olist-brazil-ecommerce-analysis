"""Project paths and analysis constants."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """All filesystem locations used by the pipeline."""

    root: Path
    raw: Path
    processed: Path
    outputs: Path
    analysis: Path

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


LAST_COMPLETE_TREND_MONTH = "2018-08"
COMPLETED_STATUS = "delivered"
NEGATIVE_REVIEW_MAX_SCORE = 2
MIN_STATE_RISK_ORDERS = 100
MIN_SELLER_RISK_ORDERS = 20
MIN_SELLER_STATE_ACTION_ORDERS = 10
SELLER_DISPATCH_SHARE_THRESHOLD = 0.35
MIN_COHORT_RFM_BUYERS = 100
COHORT_RFM_EVALUATION_MONTHS = 3

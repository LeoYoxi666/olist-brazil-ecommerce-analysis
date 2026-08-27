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

"""SHACL UI Widget Scoring Library

This library implements the SHACL UI Widget Scoring algorithm as specified
in the SHACL UI Community Group specification.
"""

__version__ = "0.1.0"

from .models import WidgetScore, ScoringResult
from .exceptions import (
    ShuiWidgetScoringError,
    MalformedScoreError,
    InvalidValueNodeError,
    MissingGraphError,
)
from .namespaces import SHUI, SH
from .core import score_widgets

__all__ = [
    "score_widgets",
    "WidgetScore",
    "ScoringResult",
    "ShuiWidgetScoringError",
    "MalformedScoreError",
    "InvalidValueNodeError",
    "MissingGraphError",
    "SHUI",
    "SH",
]

"""Data structures for SHACL UI Widget Scoring."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Union

from rdflib import URIRef, BNode


@dataclass(frozen=True)
class WidgetScore:
    """Represents a widget with its calculated score."""
    widget: Union[URIRef, BNode]
    score: Decimal

    def __lt__(self, other: 'WidgetScore') -> bool:
        """Enable sorting: first by score (desc), then by widget IRI (asc)."""
        if not isinstance(other, WidgetScore):
            return NotImplemented

        if self.score != other.score:
            return self.score > other.score  # Descending
        return str(self.widget) < str(other.widget)  # Ascending (lexicographic)


@dataclass(frozen=True)
class ScoringResult:
    """Result of widget scoring algorithm."""
    widget_scores: List[WidgetScore]

    @property
    def default_widget(self) -> Optional[Union[URIRef, BNode]]:
        """Return the highest-scoring widget, or None if no results."""
        return self.widget_scores[0].widget if self.widget_scores else None

    @property
    def default_score(self) -> Optional[Decimal]:
        """Return the highest score, or None if no results."""
        return self.widget_scores[0].score if self.widget_scores else None

    def get_widgets_with_min_score(self, min_score: Decimal = Decimal('0')) -> List[WidgetScore]:
        """Filter widgets with score >= min_score."""
        return [ws for ws in self.widget_scores if ws.score >= min_score]

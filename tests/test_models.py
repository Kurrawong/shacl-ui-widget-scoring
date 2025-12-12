"""Tests for data structures (WidgetScore and ScoringResult)."""

from decimal import Decimal

import pytest
from rdflib import URIRef

from shui_widget_scoring.models import WidgetScore, ScoringResult


class TestWidgetScore:
    """Tests for WidgetScore dataclass."""

    def test_widget_score_creation(self):
        """Test creating a WidgetScore instance."""
        widget = URIRef("http://example.org/TextEditor")
        score = Decimal("10.5")

        ws = WidgetScore(widget=widget, score=score)

        assert ws.widget == widget
        assert ws.score == score

    def test_widget_score_frozen(self):
        """Test that WidgetScore is immutable."""
        ws = WidgetScore(widget=URIRef("http://example.org/Widget"), score=Decimal("5"))

        with pytest.raises(AttributeError):
            ws.score = Decimal("10")

    def test_widget_score_sorting_by_score_descending(self):
        """Test that WidgetScore sorts by score in descending order."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))
        ws3 = WidgetScore(widget=URIRef("http://example.org/C"), score=Decimal("15"))

        sorted_scores = sorted([ws1, ws2, ws3])

        assert sorted_scores[0].score == Decimal("15")
        assert sorted_scores[1].score == Decimal("10")
        assert sorted_scores[2].score == Decimal("5")

    def test_widget_score_sorting_by_iri_when_equal_scores(self):
        """Test that WidgetScore sorts by widget IRI lexicographically when scores are equal."""
        ws1 = WidgetScore(
            widget=URIRef("http://example.org/ZEditor"), score=Decimal("10")
        )
        ws2 = WidgetScore(
            widget=URIRef("http://example.org/AEditor"), score=Decimal("10")
        )
        ws3 = WidgetScore(
            widget=URIRef("http://example.org/MEditor"), score=Decimal("10")
        )

        sorted_scores = sorted([ws1, ws2, ws3])

        assert str(sorted_scores[0].widget) == "http://example.org/AEditor"
        assert str(sorted_scores[1].widget) == "http://example.org/MEditor"
        assert str(sorted_scores[2].widget) == "http://example.org/ZEditor"

    def test_widget_score_decimal_precision(self):
        """Test that WidgetScore maintains decimal precision."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10.1"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("10.2"))

        assert ws2 < ws1  # ws2 has higher score


class TestScoringResult:
    """Tests for ScoringResult dataclass."""

    def test_scoring_result_creation(self):
        """Test creating a ScoringResult instance."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))

        result = ScoringResult(widget_scores=[ws1, ws2])

        assert len(result.widget_scores) == 2
        assert result.widget_scores[0] == ws1
        assert result.widget_scores[1] == ws2

    def test_scoring_result_frozen(self):
        """Test that ScoringResult is immutable."""
        result = ScoringResult(widget_scores=[])

        with pytest.raises(AttributeError):
            result.widget_scores = []

    def test_default_widget_with_results(self):
        """Test default_widget property with results."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))

        result = ScoringResult(widget_scores=[ws1, ws2])

        assert result.default_widget == URIRef("http://example.org/A")

    def test_default_widget_empty_results(self):
        """Test default_widget property with empty results."""
        result = ScoringResult(widget_scores=[])

        assert result.default_widget is None

    def test_default_score_with_results(self):
        """Test default_score property with results."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))

        result = ScoringResult(widget_scores=[ws1, ws2])

        assert result.default_score == Decimal("10")

    def test_default_score_empty_results(self):
        """Test default_score property with empty results."""
        result = ScoringResult(widget_scores=[])

        assert result.default_score is None

    def test_get_widgets_with_min_score_zero_default(self):
        """Test get_widgets_with_min_score with default min_score of 0."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))
        ws3 = WidgetScore(widget=URIRef("http://example.org/C"), score=Decimal("-2"))

        result = ScoringResult(widget_scores=[ws1, ws2, ws3])
        positive_scores = result.get_widgets_with_min_score()

        assert len(positive_scores) == 2
        assert ws1 in positive_scores
        assert ws2 in positive_scores
        assert ws3 not in positive_scores

    def test_get_widgets_with_min_score_custom_threshold(self):
        """Test get_widgets_with_min_score with custom threshold."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("10"))
        ws2 = WidgetScore(widget=URIRef("http://example.org/B"), score=Decimal("5"))
        ws3 = WidgetScore(widget=URIRef("http://example.org/C"), score=Decimal("3"))

        result = ScoringResult(widget_scores=[ws1, ws2, ws3])
        high_scores = result.get_widgets_with_min_score(min_score=Decimal("5"))

        assert len(high_scores) == 2
        assert ws1 in high_scores
        assert ws2 in high_scores
        assert ws3 not in high_scores

    def test_get_widgets_with_min_score_includes_equal(self):
        """Test that get_widgets_with_min_score includes widgets with exactly min_score."""
        ws1 = WidgetScore(widget=URIRef("http://example.org/A"), score=Decimal("5"))

        result = ScoringResult(widget_scores=[ws1])
        filtered = result.get_widgets_with_min_score(min_score=Decimal("5"))

        assert len(filtered) == 1
        assert ws1 in filtered

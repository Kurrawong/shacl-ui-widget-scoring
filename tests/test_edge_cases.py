"""Tests for edge cases from the SHACL UI Widget Scoring specification."""

from decimal import Decimal

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF

from shui_widget_scoring import score_widgets
from shui_widget_scoring.namespaces import SHUI

EX = Namespace("http://example.org/")


class TestEmptyScoreConditions:
    """Test edge case 6.1: Empty Score Conditions from spec."""

    def test_score_with_no_conditions_always_valid(self, logger):
        """Test that a Score with no dataGraphShape or shapesGraphShape is always valid."""
        scoring_graph = Graph()

        # Score with no conditions (no dataGraphShape or shapesGraphShape)
        scoring_graph.add((EX.DefaultScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.DefaultScore, SHUI.widget, EX.TextEditor))
        scoring_graph.add((EX.DefaultScore, SHUI.score, Literal(Decimal("1"))))

        result = score_widgets(
            focus_node=Literal("any value"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        # Score should be applicable for any value
        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.TextEditor
        assert result.default_score == Decimal("1")

    def test_multiple_values_match_unconditional_score(self, logger):
        """Test that unconditional Score matches various value types."""
        scoring_graph = Graph()

        scoring_graph.add((EX.DefaultScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.DefaultScore, SHUI.widget, EX.DefaultWidget))
        scoring_graph.add((EX.DefaultScore, SHUI.score, Literal(Decimal("5"))))

        # Test with boolean
        result1 = score_widgets(
            Literal(True), scoring_graph, scoring_graph, scoring_graph, logger=logger
        )
        assert result1.default_widget == EX.DefaultWidget

        # Test with string
        result2 = score_widgets(
            Literal("test"), scoring_graph, scoring_graph, scoring_graph, logger=logger
        )
        assert result2.default_widget == EX.DefaultWidget

        # Test with integer
        result3 = score_widgets(
            Literal(42), scoring_graph, scoring_graph, scoring_graph, logger=logger
        )
        assert result3.default_widget == EX.DefaultWidget


class TestNegativeScores:
    """Test edge case 6.2: Negative Scores from spec."""

    def test_negative_scores_in_results(self, logger):
        """Test that negative scores appear in results."""
        scoring_graph = Graph()

        # Negative score
        scoring_graph.add((EX.NegativeScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.NegativeScore, SHUI.widget, EX.DeprioritizedWidget))
        scoring_graph.add((EX.NegativeScore, SHUI.score, Literal(Decimal("-5"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.widget_scores[0].score == Decimal("-5")

    def test_negative_scores_sorted_correctly(self, logger):
        """Test that negative scores are sorted correctly (lowest last)."""
        scoring_graph = Graph()

        # Positive score
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.Widget1))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))

        # Zero score
        scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score2, SHUI.widget, EX.Widget2))
        scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("0"))))

        # Negative score
        scoring_graph.add((EX.Score3, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score3, SHUI.widget, EX.Widget3))
        scoring_graph.add((EX.Score3, SHUI.score, Literal(Decimal("-5"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 3
        assert result.widget_scores[0].score == Decimal("10")
        assert result.widget_scores[1].score == Decimal("0")
        assert result.widget_scores[2].score == Decimal("-5")

    def test_all_negative_scores_returns_highest_negative(self, logger):
        """Test that when all scores are negative, the highest (least negative) is default."""
        scoring_graph = Graph()

        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.Widget1))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("-10"))))

        scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score2, SHUI.widget, EX.Widget2))
        scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("-2"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        assert result.default_widget == EX.Widget2
        assert result.default_score == Decimal("-2")


class TestZeroScores:
    """Test edge case 6.3: Zero Scores from spec."""

    def test_zero_scores_in_results(self, logger):
        """Test that zero scores appear in results."""
        scoring_graph = Graph()

        scoring_graph.add((EX.ZeroScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.ZeroScore, SHUI.widget, EX.NotSelectableWidget))
        scoring_graph.add((EX.ZeroScore, SHUI.score, Literal(Decimal("0"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.widget_scores[0].score == Decimal("0")

    def test_zero_score_filtered_by_min_score(self, logger):
        """Test that zero scores can be filtered using get_widgets_with_min_score."""
        scoring_graph = Graph()

        scoring_graph.add((EX.ZeroScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.ZeroScore, SHUI.widget, EX.ZeroWidget))
        scoring_graph.add((EX.ZeroScore, SHUI.score, Literal(Decimal("0"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        # Zero scores are included by default (>= 0)
        selectable = result.get_widgets_with_min_score(Decimal("0"))
        assert len(selectable) == 1

        # But excluded when min_score > 0
        selectable_positive = result.get_widgets_with_min_score(Decimal("0.01"))
        assert len(selectable_positive) == 0


class TestMultipleScoresPerWidget:
    """Test edge case 6.4: Multiple Scores for Same Widget from spec."""

    def test_multiple_scores_same_widget_returns_all(self, logger):
        """Test that when multiple Scores reference the same widget, ALL scores are returned."""
        scoring_graph = Graph()

        # First score for BooleanSelectEditor
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))

        # Second score for BooleanSelectEditor (lower)
        scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score2, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("5"))))

        # Third score for BooleanSelectEditor (even lower)
        scoring_graph.add((EX.Score3, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score3, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.Score3, SHUI.score, Literal(Decimal("2"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        # Should have ALL three results for BooleanSelectEditor
        assert len(result.widget_scores) == 3

        # Results should be sorted by score descending
        assert result.widget_scores[0].widget == EX.BooleanSelectEditor
        assert result.widget_scores[0].score == Decimal("10")

        assert result.widget_scores[1].widget == EX.BooleanSelectEditor
        assert result.widget_scores[1].score == Decimal("5")

        assert result.widget_scores[2].widget == EX.BooleanSelectEditor
        assert result.widget_scores[2].score == Decimal("2")

        # Default widget should still be highest score
        assert result.default_score == Decimal("10")

    def test_multiple_scores_different_conditions(self, logger):
        """Test multiple scores for same widget with different conditions.

        Per spec section 4.1: focus node must exist in data graph for dataGraphShape
        conditions to be applicable.
        """
        from rdflib.namespace import XSD
        from shui_widget_scoring.namespaces import SH

        scoring_graph = Graph()

        # Score 10 if value is boolean
        scoring_graph.add((EX.BooleanScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.BooleanScore, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.BooleanScore, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.BooleanScore, SHUI.dataGraphShape, EX.BooleanShape))

        # Boolean shape
        scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        # Score 5 for any value (fallback)
        scoring_graph.add((EX.FallbackScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.FallbackScore, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.FallbackScore, SHUI.score, Literal(Decimal("5"))))

        # Create data graph with the focus node (required per spec 4.1)
        focus_node = Literal(True)
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        # Test with boolean value - both scores should match, both returned
        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # Both scores should be returned
        assert len(result.widget_scores) == 2
        assert result.widget_scores[0].score == Decimal("10")
        assert result.widget_scores[1].score == Decimal("5")

        # Default should be highest score
        assert result.default_score == Decimal("10")


class TestLiteralVsNodeValueNodes:
    """Test handling of Literal vs URIRef/BNode value nodes."""

    def test_literal_focus_node_no_data_graph_needed(self, logger):
        """Test that Literal value nodes don't require data_graph."""
        scoring_graph = Graph()

        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.TextWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("5"))))

        # Should work without data_graph for Literal
        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.TextWidget

    def test_uriref_focus_node_requires_data_graph(self, logger):
        """Test that URIRef value nodes require data_graph."""
        from shui_widget_scoring.exceptions import MissingGraphError
        import pytest

        scoring_graph = Graph()

        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.NodeWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("5"))))

        # Should raise MissingGraphError without data_graph
        with pytest.raises(MissingGraphError):
            score_widgets(
                focus_node=EX.someNode,
                widget_scoring_graph=scoring_graph,
                data_graph_shapes_graph=scoring_graph,
                shapes_graph_shapes_graph=scoring_graph,
                logger=logger,
            )

    def test_uriref_focus_node_with_data_graph(self, logger):
        """Test that URIRef value nodes work with data_graph."""
        data_graph = Graph()
        data_graph.add((EX.item1, RDF.type, EX.Thing))

        scoring_graph = Graph()

        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.NodeWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("5"))))

        # Should work with data_graph
        result = score_widgets(
            focus_node=EX.item1,
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.NodeWidget


class TestDecimalPrecision:
    """Test that decimal precision is maintained."""

    def test_decimal_precision_in_scores(self, logger):
        """Test that decimal precision is maintained in score comparisons."""
        scoring_graph = Graph()

        # Score 10.1
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.Widget1))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10.1"))))

        # Score 10.2
        scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score2, SHUI.widget, EX.Widget2))
        scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("10.2"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            data_graph_shapes_graph=scoring_graph,
            shapes_graph_shapes_graph=scoring_graph,
            logger=logger,
        )

        # Widget2 should be first due to higher precise score
        assert result.widget_scores[0].widget == EX.Widget2
        assert result.widget_scores[0].score == Decimal("10.2")
        assert result.widget_scores[1].widget == EX.Widget1
        assert result.widget_scores[1].score == Decimal("10.1")

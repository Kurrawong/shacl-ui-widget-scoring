"""Tests for core widget scoring algorithm."""

from decimal import Decimal

import pytest
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, XSD

from shui_widget_scoring import score_widgets
from shui_widget_scoring.exceptions import (
    InvalidFocusNodeError,
    MissingGraphError,
    MalformedScoreError,
)
from shui_widget_scoring.namespaces import SHUI, SH

EX = Namespace("http://example.org/")


class TestScoreWidgetsBasic:
    """Basic tests for score_widgets function."""

    def test_score_widgets_with_literal_value(
        self, simple_widget_scoring_graph, logger
    ):
        """Test scoring widgets for a literal boolean value.

        Per spec section 4.1: focus node must exist in data graph for dataGraphShape
        conditions to be applicable.
        """
        # Create a data graph containing the focus node (literal must appear as object)
        data_graph = Graph()
        focus_node = Literal(True)
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        # Add the boolean shape to the scoring graph
        simple_widget_scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        simple_widget_scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=simple_widget_scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # Should return BooleanSelectEditor (score 10) and TextEditor (score 1)
        assert len(result.widget_scores) == 2
        assert result.default_widget == EX.BooleanSelectEditor
        assert result.default_score == Decimal("10")

    def test_score_widgets_empty_results(self, logger):
        """Test scoring when no widgets match due to shape mismatch."""
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.SpecialWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.dataGraphShape, EX.DateShape))

        # Add date shape to scoring graph
        scoring_graph.add((EX.DateShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.DateShape, SH.datatype, XSD.date))

        # Create data graph with the focus node
        focus_node = Literal(True)
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        result = score_widgets(
            focus_node=focus_node,  # Boolean, doesn't match date shape
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 0
        assert result.default_widget is None
        assert result.default_score is None

    def test_score_widgets_sorts_by_score_descending(self, logger):
        """Test that results are sorted by score in descending order."""
        scoring_graph = Graph()

        # Low score widget
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.LowWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("2"))))

        # High score widget
        scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score2, SHUI.widget, EX.HighWidget))
        scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("10"))))

        # Medium score widget
        scoring_graph.add((EX.Score3, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score3, SHUI.widget, EX.MediumWidget))
        scoring_graph.add((EX.Score3, SHUI.score, Literal(Decimal("5"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 3
        assert result.widget_scores[0].widget == EX.HighWidget
        assert result.widget_scores[0].score == Decimal("10")
        assert result.widget_scores[1].widget == EX.MediumWidget
        assert result.widget_scores[1].score == Decimal("5")
        assert result.widget_scores[2].widget == EX.LowWidget
        assert result.widget_scores[2].score == Decimal("2")

    def test_score_widgets_sorts_by_iri_when_equal_scores(self, logger):
        """Test that widgets with equal scores are sorted lexicographically by IRI."""
        scoring_graph = Graph()

        # Widget Z with score 10
        scoring_graph.add((EX.ScoreZ, RDF.type, SHUI.Score))
        scoring_graph.add(
            (EX.ScoreZ, SHUI.widget, URIRef("http://example.org/ZWidget"))
        )
        scoring_graph.add((EX.ScoreZ, SHUI.score, Literal(Decimal("10"))))

        # Widget A with score 10
        scoring_graph.add((EX.ScoreA, RDF.type, SHUI.Score))
        scoring_graph.add(
            (EX.ScoreA, SHUI.widget, URIRef("http://example.org/AWidget"))
        )
        scoring_graph.add((EX.ScoreA, SHUI.score, Literal(Decimal("10"))))

        # Widget M with score 10
        scoring_graph.add((EX.ScoreM, RDF.type, SHUI.Score))
        scoring_graph.add(
            (EX.ScoreM, SHUI.widget, URIRef("http://example.org/MWidget"))
        )
        scoring_graph.add((EX.ScoreM, SHUI.score, Literal(Decimal("10"))))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 3
        assert str(result.widget_scores[0].widget) == "http://example.org/AWidget"
        assert str(result.widget_scores[1].widget) == "http://example.org/MWidget"
        assert str(result.widget_scores[2].widget) == "http://example.org/ZWidget"


class TestScoreWidgetsInputValidation:
    """Tests for input validation in score_widgets."""

    def test_invalid_focus_node_type(self, simple_widget_scoring_graph):
        """Test that invalid focus_node type raises InvalidFocusNodeError."""
        with pytest.raises(InvalidFocusNodeError):
            score_widgets(
                focus_node="not a valid node",
                widget_scoring_graph=simple_widget_scoring_graph,
            )

    def test_uriref_focus_node_requires_data_graph(self, simple_widget_scoring_graph):
        """Test that URIRef focus_node requires data_graph."""
        with pytest.raises(MissingGraphError) as exc_info:
            score_widgets(
                focus_node=EX.someNode, widget_scoring_graph=simple_widget_scoring_graph
            )

        assert "data_graph" in str(exc_info.value)

    def test_bnode_focus_node_requires_data_graph(self, simple_widget_scoring_graph):
        """Test that BNode focus_node requires data_graph."""
        with pytest.raises(MissingGraphError) as exc_info:
            score_widgets(
                focus_node=BNode(), widget_scoring_graph=simple_widget_scoring_graph
            )

        assert "data_graph" in str(exc_info.value)

    def test_constraint_shape_requires_shapes_graph(self, simple_widget_scoring_graph):
        """Test that constraint_shape requires shapes_graph."""
        with pytest.raises(MissingGraphError) as exc_info:
            score_widgets(
                focus_node=Literal("test"),
                widget_scoring_graph=simple_widget_scoring_graph,
                constraint_shape=EX.SomeShape,
            )

        assert "shapes_graph" in str(exc_info.value)

    def test_malformed_scoring_graph_raises_error(
        self, malformed_scoring_graph_no_widget
    ):
        """Test that malformed widget scoring graph raises MalformedScoreError."""
        with pytest.raises(MalformedScoreError):
            score_widgets(
                focus_node=Literal("test"),
                widget_scoring_graph=malformed_scoring_graph_no_widget,
            )


class TestScoreWidgetsWithConstraintShapes:
    """Tests for score_widgets with constraint shapes."""

    def test_score_with_shapes_graph_shape(self, logger):
        """Test scoring with shapesGraphShape validation."""
        # Create shapes graph with a property shape that has sh:datatype
        shapes_graph = Graph()
        shapes_graph.add((EX.PropertyShape, RDF.type, SH.PropertyShape))
        shapes_graph.add((EX.PropertyShape, SH.path, EX.someProperty))
        shapes_graph.add((EX.PropertyShape, SH.datatype, XSD.string))

        # Create scoring graph with a Score that checks for sh:datatype in the shape
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.SpecialWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.shapesGraphShape, EX.HasDatatypeShape))

        # Shape that checks if the constraint shape has sh:datatype property
        scoring_graph.add((EX.HasDatatypeShape, RDF.type, SH.NodeShape))
        prop = BNode()
        scoring_graph.add((EX.HasDatatypeShape, SH.property, prop))
        scoring_graph.add((prop, SH.path, SH.datatype))
        scoring_graph.add((prop, SH.minCount, Literal(1)))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            constraint_shape=EX.PropertyShape,
            shapes_graph=shapes_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.SpecialWidget

    def test_score_with_shapesGraphShape_no_constraint_shape(self, logger):
        """Test that Score with shapesGraphShape is not applicable when no constraint_shape provided (per spec 6.2)."""
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.SpecialWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.shapesGraphShape, EX.SomeShape))

        # Add a minimal shape to the scoring graph
        scoring_graph.add((EX.SomeShape, RDF.type, SH.NodeShape))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            logger=logger,
        )

        # Score is not applicable - shapesGraphShape requires constraint_shape to be provided
        assert len(result.widget_scores) == 0


class TestScoreWidgetsDataGraphValidation:
    """Tests for data graph validation in score_widgets."""

    def test_score_with_uriref_focus_node(self, logger):
        """Test scoring with URIRef value node."""
        # Create data graph
        data_graph = Graph()
        data_graph.add((EX.item1, RDF.type, EX.Person))

        # Create scoring graph with shape that checks for type
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.PersonWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.dataGraphShape, EX.PersonShape))

        # Shape that checks for ex:Person type
        scoring_graph.add((EX.PersonShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.PersonShape, SH["class"], EX.Person))

        result = score_widgets(
            focus_node=EX.item1,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.PersonWidget

    def test_focus_node_not_in_data_graph_makes_score_inapplicable(self, logger):
        """Test per spec section 6.2: If focus node doesn't exist in data graph, score is not applicable."""
        # Create data graph WITHOUT the focus node
        data_graph = Graph()
        data_graph.add((EX.otherItem, EX.someProperty, Literal("other")))

        # Create scoring graph with dataGraphShape condition
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.BooleanWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.dataGraphShape, EX.BooleanShape))

        # Add boolean shape
        scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        # Also add a default score with no conditions (should still apply)
        scoring_graph.add((EX.DefaultScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.DefaultScore, SHUI.widget, EX.DefaultWidget))
        scoring_graph.add((EX.DefaultScore, SHUI.score, Literal(Decimal("1"))))

        result = score_widgets(
            focus_node=Literal(True),  # This literal is NOT in data_graph
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # Only DefaultScore should apply (no dataGraphShape condition)
        # BooleanWidget score should NOT apply because focus node not in data graph
        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.DefaultWidget
        assert result.default_score == Decimal("1")


class TestMultipleScoresForSameWidget:
    """Tests for spec section 6.5: Multiple scores for same widget."""

    def test_multiple_scores_same_widget_all_returned(self, logger):
        """Test per spec 6.5: When multiple Score instances reference the same widget, ALL matching scores are returned."""
        focus_node = Literal(True)

        # Create data graph with the focus node
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        # Create shapes graph with boolean datatype constraint
        shapes_graph = Graph()
        shapes_graph.add((EX.BooleanPropertyShape, RDF.type, SH.PropertyShape))
        shapes_graph.add((EX.BooleanPropertyShape, SH.path, EX.someProperty))
        shapes_graph.add((EX.BooleanPropertyShape, SH.datatype, XSD.boolean))

        # Create scoring graph with TWO scores for the same widget
        scoring_graph = Graph()

        # Score 10 if Focus Node is boolean (dataGraphShape condition)
        scoring_graph.add((EX.BooleanScore10, RDF.type, SHUI.Score))
        scoring_graph.add((EX.BooleanScore10, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.BooleanScore10, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.BooleanScore10, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Score 5 if Constraint Shape has boolean datatype (shapesGraphShape condition)
        scoring_graph.add((EX.BooleanScore5, RDF.type, SHUI.Score))
        scoring_graph.add((EX.BooleanScore5, SHUI.widget, EX.BooleanSelectEditor))
        scoring_graph.add((EX.BooleanScore5, SHUI.score, Literal(Decimal("5"))))
        scoring_graph.add((EX.BooleanScore5, SHUI.shapesGraphShape, EX.HasBooleanDatatypeShape))

        # Add the dataGraphShape: checks if focus node is boolean
        scoring_graph.add((EX.IsBooleanShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.IsBooleanShape, SH.datatype, XSD.boolean))

        # Add the shapesGraphShape: checks if constraint shape has sh:datatype xsd:boolean
        scoring_graph.add((EX.HasBooleanDatatypeShape, RDF.type, SH.NodeShape))
        prop = BNode()
        scoring_graph.add((EX.HasBooleanDatatypeShape, SH.property, prop))
        scoring_graph.add((prop, SH.path, SH.datatype))
        in_list = BNode()
        scoring_graph.add((prop, SH["in"], in_list))
        scoring_graph.add((in_list, RDF.first, XSD.boolean))
        scoring_graph.add((in_list, RDF.rest, RDF.nil))

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            constraint_shape=EX.BooleanPropertyShape,
            shapes_graph=shapes_graph,
            logger=logger,
        )

        # Both scores for BooleanSelectEditor should be returned
        boolean_scores = [
            ws for ws in result.widget_scores if ws.widget == EX.BooleanSelectEditor
        ]
        assert len(boolean_scores) == 2
        scores = sorted([ws.score for ws in boolean_scores], reverse=True)
        assert scores == [Decimal("10"), Decimal("5")]

        # Default widget is the one with highest score
        assert result.default_widget == EX.BooleanSelectEditor
        assert result.default_score == Decimal("10")


class TestNegativeAndZeroScores:
    """Tests for spec sections 6.3 (negative scores) and 6.4 (zero scores)."""

    def test_negative_scores_returned_in_results(self, logger):
        """Test per spec 6.3: Negative scores are valid and appear in results."""
        focus_node = Literal("2025-01-15", datatype=XSD.date)

        # Create data graph with the focus node
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        scoring_graph = Graph()

        # Positive score for date picker
        scoring_graph.add((EX.DatePickerScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.DatePickerScore, SHUI.widget, EX.DatePickerEditor))
        scoring_graph.add((EX.DatePickerScore, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.DatePickerScore, SHUI.dataGraphShape, EX.IsDateShape))

        # Negative score for text editor (deprioritize for dates)
        scoring_graph.add((EX.TextEditorNegative, RDF.type, SHUI.Score))
        scoring_graph.add((EX.TextEditorNegative, SHUI.widget, EX.TextEditor))
        scoring_graph.add((EX.TextEditorNegative, SHUI.score, Literal(Decimal("-5"))))
        scoring_graph.add((EX.TextEditorNegative, SHUI.dataGraphShape, EX.IsDateShape))

        # Add date shape
        scoring_graph.add((EX.IsDateShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.IsDateShape, SH.datatype, XSD.date))

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # Both scores should be returned
        assert len(result.widget_scores) == 2

        # Check results are sorted correctly (positive first, then negative)
        assert result.widget_scores[0].widget == EX.DatePickerEditor
        assert result.widget_scores[0].score == Decimal("10")
        assert result.widget_scores[1].widget == EX.TextEditor
        assert result.widget_scores[1].score == Decimal("-5")

        # Default should be the positive score
        assert result.default_widget == EX.DatePickerEditor

    def test_zero_scores_returned_in_results(self, logger):
        """Test per spec 6.4: Zero scores indicate widget is not selectable but still appear in results."""
        focus_node = Literal(True)

        # Create data graph with the focus node
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        scoring_graph = Graph()

        # Positive score
        scoring_graph.add((EX.PositiveScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.PositiveScore, SHUI.widget, EX.BooleanEditor))
        scoring_graph.add((EX.PositiveScore, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.PositiveScore, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Zero score (not selectable)
        scoring_graph.add((EX.ZeroScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.ZeroScore, SHUI.widget, EX.NotSelectableWidget))
        scoring_graph.add((EX.ZeroScore, SHUI.score, Literal(Decimal("0"))))
        scoring_graph.add((EX.ZeroScore, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Add boolean shape
        scoring_graph.add((EX.IsBooleanShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.IsBooleanShape, SH.datatype, XSD.boolean))

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # Both scores should be returned
        assert len(result.widget_scores) == 2

        # Zero-scored widget should be in results
        zero_scores = [ws for ws in result.widget_scores if ws.score == Decimal("0")]
        assert len(zero_scores) == 1
        assert zero_scores[0].widget == EX.NotSelectableWidget

        # Default should be the positive score
        assert result.default_widget == EX.BooleanEditor
        assert result.default_score == Decimal("10")

    def test_get_widgets_with_min_score_filters_correctly(self, logger):
        """Test that get_widgets_with_min_score filters out zero and negative scores."""
        focus_node = Literal(True)

        # Create data graph with the focus node
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        scoring_graph = Graph()

        # Positive score 10
        scoring_graph.add((EX.Score10, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score10, SHUI.widget, EX.WidgetA))
        scoring_graph.add((EX.Score10, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score10, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Positive score 5
        scoring_graph.add((EX.Score5, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score5, SHUI.widget, EX.WidgetB))
        scoring_graph.add((EX.Score5, SHUI.score, Literal(Decimal("5"))))
        scoring_graph.add((EX.Score5, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Zero score
        scoring_graph.add((EX.Score0, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score0, SHUI.widget, EX.WidgetC))
        scoring_graph.add((EX.Score0, SHUI.score, Literal(Decimal("0"))))
        scoring_graph.add((EX.Score0, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Negative score
        scoring_graph.add((EX.ScoreNeg, RDF.type, SHUI.Score))
        scoring_graph.add((EX.ScoreNeg, SHUI.widget, EX.WidgetD))
        scoring_graph.add((EX.ScoreNeg, SHUI.score, Literal(Decimal("-3"))))
        scoring_graph.add((EX.ScoreNeg, SHUI.dataGraphShape, EX.IsBooleanShape))

        # Add boolean shape
        scoring_graph.add((EX.IsBooleanShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.IsBooleanShape, SH.datatype, XSD.boolean))

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # All 4 should be in results
        assert len(result.widget_scores) == 4

        # Filter with min_score=0 should return only widgets with score >= 0
        selectable = result.get_widgets_with_min_score(Decimal("0"))
        assert len(selectable) == 3  # Excludes negative

        # Filter with min_score=1 should exclude zero and negative
        positive_only = result.get_widgets_with_min_score(Decimal("1"))
        assert len(positive_only) == 2
        widgets = [ws.widget for ws in positive_only]
        assert EX.WidgetA in widgets
        assert EX.WidgetB in widgets


class TestMalformedShapeValidation:
    """Tests for spec section 4.3: Error handling for malformed shapes."""

    def test_malformed_shape_makes_score_inapplicable(self, logger):
        """Test per spec 4.3: Malformed shape validation errors should cause validation to return false."""
        focus_node = Literal(True)

        # Create data graph with the focus node
        data_graph = Graph()
        data_graph.add((EX.someSubject, EX.someProperty, focus_node))

        scoring_graph = Graph()

        # Score with a reference to a shape that doesn't exist in the shapes graph
        scoring_graph.add((EX.BadScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.BadScore, SHUI.widget, EX.BadWidget))
        scoring_graph.add((EX.BadScore, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.BadScore, SHUI.dataGraphShape, EX.NonExistentShape))

        # Note: EX.NonExistentShape is NOT defined in scoring_graph
        # This should cause validation to fail for this score

        # Also add a valid score that should still work
        scoring_graph.add((EX.GoodScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.GoodScore, SHUI.widget, EX.GoodWidget))
        scoring_graph.add((EX.GoodScore, SHUI.score, Literal(Decimal("5"))))
        # No dataGraphShape - always applicable

        result = score_widgets(
            focus_node=focus_node,
            widget_scoring_graph=scoring_graph,
            data_graph=data_graph,
            logger=logger,
        )

        # BadScore should NOT be applicable (shape not defined)
        # GoodScore should be applicable
        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.GoodWidget
        assert result.default_score == Decimal("5")


class TestEmptyScoreConditions:
    """Tests for spec section 6.1: Empty score conditions."""

    def test_score_with_no_conditions_always_applicable(self, logger):
        """Test per spec 6.1: Score with no dataGraphShape or shapesGraphShape is always applicable."""
        # No data_graph provided, but score has no conditions
        scoring_graph = Graph()

        # Score with no conditions
        scoring_graph.add((EX.DefaultScore, RDF.type, SHUI.Score))
        scoring_graph.add((EX.DefaultScore, SHUI.widget, EX.TextEditor))
        scoring_graph.add((EX.DefaultScore, SHUI.score, Literal(Decimal("1"))))
        # No dataGraphShape, no shapesGraphShape

        result = score_widgets(
            focus_node=Literal("any value"),
            widget_scoring_graph=scoring_graph,
            logger=logger,
        )

        # Score should be applicable
        assert len(result.widget_scores) == 1
        assert result.default_widget == EX.TextEditor
        assert result.default_score == Decimal("1")

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
        """Test scoring widgets for a literal boolean value."""
        # Create a shapes graph with boolean shape
        shapes_graph = Graph()
        shapes_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        shapes_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        # Add the boolean shape to the scoring graph
        simple_widget_scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        simple_widget_scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        result = score_widgets(
            focus_node=Literal(True),
            widget_scoring_graph=simple_widget_scoring_graph,
            logger=logger,
        )

        # Should return BooleanSelectEditor (score 10) and TextEditor (score 1)
        assert len(result.widget_scores) == 2
        assert result.default_widget == EX.BooleanSelectEditor
        assert result.default_score == Decimal("10")

    def test_score_widgets_empty_results(self, logger):
        """Test scoring when no widgets match."""
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.SpecialWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.dataGraphShape, EX.DateShape))

        # Add date shape to scoring graph
        scoring_graph.add((EX.DateShape, RDF.type, SH.NodeShape))
        scoring_graph.add((EX.DateShape, SH.datatype, XSD.date))

        result = score_widgets(
            focus_node=Literal(True),  # Boolean, doesn't match date shape
            widget_scoring_graph=scoring_graph,
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
        """Test that Score with shapesGraphShape validates using shape's own targets when no constraint_shape provided."""
        scoring_graph = Graph()
        scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        scoring_graph.add((EX.Score1, SHUI.widget, EX.SpecialWidget))
        scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))
        scoring_graph.add((EX.Score1, SHUI.shapesGraphShape, EX.SomeShape))

        # Add a minimal shape to the scoring graph (no targets, so it validates trivially)
        scoring_graph.add((EX.SomeShape, RDF.type, SH.NodeShape))

        result = score_widgets(
            focus_node=Literal("test"),
            widget_scoring_graph=scoring_graph,
            logger=logger,
        )

        # Score should be applicable - the shape validates without requiring constraint_shape
        assert len(result.widget_scores) == 1
        assert result.widget_scores[0].widget == EX.SpecialWidget
        assert result.widget_scores[0].score == Decimal("10")


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

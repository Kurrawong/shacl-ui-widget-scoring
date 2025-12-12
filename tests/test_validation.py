"""Tests for validation functions."""

from decimal import Decimal

import pytest
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD

from shui_widget_scoring.validation import (
    validate_widget_scoring_graph,
    validate_score_instance,
    extract_score_instances,
)
from shui_widget_scoring.exceptions import MalformedScoreError
from shui_widget_scoring.namespaces import SHUI


class TestValidateWidgetScoringGraph:
    """Tests for validate_widget_scoring_graph function."""

    def test_valid_widget_scoring_graph(self, simple_widget_scoring_graph):
        """Test that a valid widget scoring graph passes validation."""
        # Should not raise any exception
        validate_widget_scoring_graph(simple_widget_scoring_graph)

    def test_malformed_score_no_widget(self, malformed_scoring_graph_no_widget, logger):
        """Test that Score with no widget raises MalformedScoreError."""
        with pytest.raises(MalformedScoreError) as exc_info:
            validate_widget_scoring_graph(
                malformed_scoring_graph_no_widget, logger=logger
            )

        assert "widget" in str(exc_info.value).lower()

    def test_malformed_score_multiple_widgets(
        self, malformed_scoring_graph_multiple_widgets, logger
    ):
        """Test that Score with multiple widgets raises MalformedScoreError."""
        with pytest.raises(MalformedScoreError) as exc_info:
            validate_widget_scoring_graph(
                malformed_scoring_graph_multiple_widgets, logger=logger
            )

        assert "widget" in str(exc_info.value).lower()

    def test_malformed_score_no_score(self, malformed_scoring_graph_no_score, logger):
        """Test that Score with no score raises MalformedScoreError."""
        with pytest.raises(MalformedScoreError) as exc_info:
            validate_widget_scoring_graph(
                malformed_scoring_graph_no_score, logger=logger
            )

        assert "score" in str(exc_info.value).lower()

    def test_malformed_score_invalid_score_datatype(
        self, malformed_scoring_graph_invalid_score_type, logger
    ):
        """Test that Score with invalid score datatype raises MalformedScoreError."""
        with pytest.raises(MalformedScoreError) as exc_info:
            validate_widget_scoring_graph(
                malformed_scoring_graph_invalid_score_type, logger=logger
            )

        # The validation should fail due to datatype mismatch
        assert (
            "score" in str(exc_info.value).lower()
            or "decimal" in str(exc_info.value).lower()
        )


class TestValidateScoreInstance:
    """Tests for validate_score_instance function."""

    def test_validate_valid_score_instance(self):
        """Test validating a valid Score instance."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))
        g.add((score_uri, SHUI.score, Literal(Decimal("10"))))

        result = validate_score_instance(score_uri, g)

        assert result["uri"] == score_uri
        assert result["widget"] == URIRef("http://example.org/Widget")
        assert result["score"] == Decimal("10")
        assert result["dataGraphShapes"] == []
        assert result["shapesGraphShapes"] == []

    def test_validate_score_with_shapes(self):
        """Test validating a Score instance with data and shapes graph shapes."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")
        dg_shape = URIRef("http://example.org/DataShape")
        sg_shape = URIRef("http://example.org/ShapesShape")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))
        g.add((score_uri, SHUI.score, Literal(Decimal("10"))))
        g.add((score_uri, SHUI.dataGraphShape, dg_shape))
        g.add((score_uri, SHUI.shapesGraphShape, sg_shape))

        result = validate_score_instance(score_uri, g)

        assert dg_shape in result["dataGraphShapes"]
        assert sg_shape in result["shapesGraphShapes"]

    def test_validate_score_missing_widget(self):
        """Test that missing widget raises MalformedScoreError."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.score, Literal(Decimal("10"))))

        with pytest.raises(MalformedScoreError) as exc_info:
            validate_score_instance(score_uri, g)

        assert "widget" in str(exc_info.value)

    def test_validate_score_multiple_widgets(self):
        """Test that multiple widgets raise MalformedScoreError."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget1")))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget2")))
        g.add((score_uri, SHUI.score, Literal(Decimal("10"))))

        with pytest.raises(MalformedScoreError) as exc_info:
            validate_score_instance(score_uri, g)

        assert "widget" in str(exc_info.value)
        assert "multiple" in str(exc_info.value).lower()

    def test_validate_score_missing_score(self):
        """Test that missing score raises MalformedScoreError."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))

        with pytest.raises(MalformedScoreError) as exc_info:
            validate_score_instance(score_uri, g)

        assert "score" in str(exc_info.value)

    def test_validate_score_invalid_score_value(self):
        """Test that invalid score value raises MalformedScoreError."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))
        g.add((score_uri, SHUI.score, Literal("not a number")))

        with pytest.raises(MalformedScoreError) as exc_info:
            validate_score_instance(score_uri, g)

        assert (
            "decimal" in str(exc_info.value).lower()
            or "integer" in str(exc_info.value).lower()
        )

    def test_validate_score_integer_value(self):
        """Test that integer scores are accepted."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))
        g.add((score_uri, SHUI.score, Literal(10, datatype=XSD.integer)))

        result = validate_score_instance(score_uri, g)

        assert result["score"] == Decimal("10")

    def test_validate_score_negative_value(self):
        """Test that negative scores are accepted."""
        g = Graph()
        score_uri = URIRef("http://example.org/score1")

        g.add((score_uri, RDF.type, SHUI.Score))
        g.add((score_uri, SHUI.widget, URIRef("http://example.org/Widget")))
        g.add((score_uri, SHUI.score, Literal(Decimal("-5"))))

        result = validate_score_instance(score_uri, g)

        assert result["score"] == Decimal("-5")


class TestExtractScoreInstances:
    """Tests for extract_score_instances function."""

    def test_extract_from_simple_graph(self, simple_widget_scoring_graph):
        """Test extracting Score instances from a simple graph."""
        scores = extract_score_instances(simple_widget_scoring_graph)

        assert len(scores) == 3  # BooleanScore, DateScore, DefaultTextScore

    def test_extract_from_empty_graph(self, empty_graph):
        """Test extracting from an empty graph returns empty list."""
        scores = extract_score_instances(empty_graph)

        assert len(scores) == 0

    def test_extract_validates_each_score(self, malformed_scoring_graph_no_widget):
        """Test that extraction validates each Score instance."""
        with pytest.raises(MalformedScoreError):
            extract_score_instances(malformed_scoring_graph_no_widget)

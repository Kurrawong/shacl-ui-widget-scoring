"""Pytest fixtures for SHACL UI Widget Scoring tests."""

import logging
from decimal import Decimal

import pytest
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDF, XSD

from shui_widget_scoring.namespaces import SHUI, SH


# Define test namespace
EX = Namespace("http://example.org/")


@pytest.fixture
def logger():
    """Provide a test logger."""
    return logging.getLogger("test")


@pytest.fixture
def empty_graph():
    """Provide an empty RDF graph."""
    return Graph()


@pytest.fixture
def sample_data_graph():
    """Provide a sample data graph with various node types."""
    g = Graph()

    # Boolean value
    g.add((EX.item1, EX.isActive, Literal(True)))

    # Date value
    g.add((EX.item2, EX.createdDate, Literal("2025-01-15", datatype=XSD.date)))

    # String value
    g.add((EX.item3, EX.name, Literal("Test Name")))

    # Integer value
    g.add((EX.item4, EX.count, Literal(42, datatype=XSD.integer)))

    # URIRef value
    g.add((EX.item5, EX.linkedTo, EX.otherItem))

    return g


@pytest.fixture
def sample_shapes_graph():
    """Provide a sample shapes graph with common constraints."""
    g = Graph()

    # Boolean datatype constraint
    g.add((EX.BooleanShape, RDF.type, SH.NodeShape))
    g.add((EX.BooleanShape, SH.datatype, XSD.boolean))

    # Date datatype constraint
    g.add((EX.DateShape, RDF.type, SH.NodeShape))
    g.add((EX.DateShape, SH.datatype, XSD.date))

    # String pattern constraint
    g.add((EX.StringShape, RDF.type, SH.NodeShape))
    g.add((EX.StringShape, SH.datatype, XSD.string))
    g.add((EX.StringShape, SH.pattern, Literal("^[A-Z]")))

    # Integer datatype constraint
    g.add((EX.IntegerShape, RDF.type, SH.NodeShape))
    g.add((EX.IntegerShape, SH.datatype, XSD.integer))

    # Property shape with sh:in constraint
    g.add((EX.PropertyWithIn, RDF.type, SH.PropertyShape))
    g.add((EX.PropertyWithIn, SH.path, EX.status))
    in_list = BNode()
    g.add((EX.PropertyWithIn, SH["in"], in_list))

    # Shape that checks for sh:datatype property
    g.add((EX.HasDatatypeShape, RDF.type, SH.NodeShape))
    prop = BNode()
    g.add((EX.HasDatatypeShape, SH.property, prop))
    g.add((prop, SH.path, SH.datatype))
    g.add((prop, SH.minCount, Literal(1)))

    return g


@pytest.fixture
def simple_widget_scoring_graph():
    """Provide a simple widget scoring graph with basic Score instances."""
    g = Graph()

    # Score for boolean values
    g.add((EX.BooleanScore, RDF.type, SHUI.Score))
    g.add((EX.BooleanScore, SHUI.widget, EX.BooleanSelectEditor))
    g.add((EX.BooleanScore, SHUI.score, Literal(Decimal("10"))))
    g.add((EX.BooleanScore, SHUI.dataGraphShape, EX.BooleanShape))

    # Score for date values
    g.add((EX.DateScore, RDF.type, SHUI.Score))
    g.add((EX.DateScore, SHUI.widget, EX.DatePickerEditor))
    g.add((EX.DateScore, SHUI.score, Literal(Decimal("8"))))
    g.add((EX.DateScore, SHUI.dataGraphShape, EX.DateShape))

    # Default text editor (no conditions, always applicable)
    g.add((EX.DefaultTextScore, RDF.type, SHUI.Score))
    g.add((EX.DefaultTextScore, SHUI.widget, EX.TextEditor))
    g.add((EX.DefaultTextScore, SHUI.score, Literal(Decimal("1"))))

    return g


@pytest.fixture
def malformed_scoring_graph_no_widget():
    """Provide a widget scoring graph with a Score missing shui:widget."""
    g = Graph()

    g.add((EX.MalformedScore, RDF.type, SHUI.Score))
    g.add((EX.MalformedScore, SHUI.score, Literal(Decimal("10"))))

    return g


@pytest.fixture
def malformed_scoring_graph_multiple_widgets():
    """Provide a widget scoring graph with a Score having multiple shui:widget values."""
    g = Graph()

    g.add((EX.MalformedScore, RDF.type, SHUI.Score))
    g.add((EX.MalformedScore, SHUI.widget, EX.Widget1))
    g.add((EX.MalformedScore, SHUI.widget, EX.Widget2))
    g.add((EX.MalformedScore, SHUI.score, Literal(Decimal("10"))))

    return g


@pytest.fixture
def malformed_scoring_graph_no_score():
    """Provide a widget scoring graph with a Score missing shui:score."""
    g = Graph()

    g.add((EX.MalformedScore, RDF.type, SHUI.Score))
    g.add((EX.MalformedScore, SHUI.widget, EX.SomeWidget))

    return g


@pytest.fixture
def malformed_scoring_graph_invalid_score_type():
    """Provide a widget scoring graph with a Score having invalid score datatype."""
    g = Graph()

    g.add((EX.MalformedScore, RDF.type, SHUI.Score))
    g.add((EX.MalformedScore, SHUI.widget, EX.SomeWidget))
    g.add((EX.MalformedScore, SHUI.score, Literal("not a number")))  # String, not decimal/integer

    return g


def create_score_instance(
    widget: URIRef,
    score: Decimal,
    data_graph_shapes: list = None,
    shapes_graph_shapes: list = None
) -> Graph:
    """
    Helper function to create a widget scoring graph with a single Score instance.

    Args:
        widget: The widget URI
        score: The numeric score
        data_graph_shapes: List of data graph shape URIs (optional)
        shapes_graph_shapes: List of shapes graph shape URIs (optional)

    Returns:
        Graph containing a single Score instance
    """
    g = Graph()
    score_uri = BNode()

    g.add((score_uri, RDF.type, SHUI.Score))
    g.add((score_uri, SHUI.widget, widget))
    g.add((score_uri, SHUI.score, Literal(score)))

    if data_graph_shapes:
        for shape in data_graph_shapes:
            g.add((score_uri, SHUI.dataGraphShape, shape))

    if shapes_graph_shapes:
        for shape in shapes_graph_shapes:
            g.add((score_uri, SHUI.shapesGraphShape, shape))

    return g

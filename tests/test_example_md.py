"""Tests matching the examples from example.md exactly."""

import pytest
from decimal import Decimal
from rdflib import Graph, Literal, Namespace

from shui_widget_scoring import score_widgets, SHUI

EX = Namespace("https://example.com/")
SCHEMA = Namespace("https://schema.org/")


class TestExampleMd:
    """Test cases matching example.md scenarios exactly."""

    @pytest.fixture
    def data_graph_shapes(self):
        """Create data graph shapes from example.md."""
        g = Graph()
        turtle = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX shui: <http://www.w3.org/ns/shacl-ui#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        shui:isBoolean a sh:NodeShape ;
            sh:datatype xsd:boolean .

        shui:isDate a sh:NodeShape ;
            sh:datatype xsd:date .

        shui:isNotLiteral a sh:NodeShape ;
            sh:nodeKind sh:BlankNodeOrIRI .
        """
        g.parse(data=turtle, format="turtle")
        return g

    @pytest.fixture
    def shapes_graph_shapes(self):
        """Create shapes graph shapes from example.md."""
        g = Graph()
        turtle = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX shui: <http://www.w3.org/ns/shacl-ui#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        shui:hasDatatype a sh:NodeShape ;
            sh:property [
                sh:path sh:datatype ;
                sh:minCount 1
            ] .

        shui:hasDateDatatype a sh:NodeShape ;
            sh:property [
                sh:path sh:datatype ;
                sh:in (xsd:date)
            ] .

        shui:literalNoDatatypeSpecified a sh:NodeShape ;
            sh:property [
                sh:path sh:nodeKind ;
                sh:hasValue sh:Literal
            ] ;
            sh:property [
                sh:path sh:datatype ;
                sh:maxCount 0
            ] .

        shui:hasNonLiteralNodeKind a sh:NodeShape ;
            sh:property [
                sh:path sh:nodeKind ;
                sh:in (sh:BlankNodeOrIRI sh:IRI sh:BlankNode)
            ] .
        """
        g.parse(data=turtle, format="turtle")
        return g

    @pytest.fixture
    def widget_scoring_graph(self):
        """Create widget scoring graph from example.md (Score instances only)."""
        g = Graph()
        turtle = """
        PREFIX shui: <http://www.w3.org/ns/shacl-ui#>

        shui:booleanSelectEditorScore10 a shui:Score ;
            shui:dataGraphShape shui:isBoolean ;
            shui:widget shui:BooleanSelectEditor ;
            shui:score 10 .

        # Score 0 if data graph value node is not a literal
        shui:booleanSelectEditorScore0-isNotLiteral a shui:Score ;
            shui:dataGraphShape shui:isNotLiteral ;
            shui:widget shui:BooleanSelectEditor ;
            shui:score 0 .

        # Score 0 if shapes graph constraint shape has sh:datatype
        shui:booleanSelectEditorScore0-hasDatatype a shui:Score ;
            shui:shapesGraphShape shui:hasDatatype ;
            shui:widget shui:BooleanSelectEditor ;
            shui:score 0 .

        # Score 0 if shapes graph constraint shape has sh:nodeKind with non-literal values
        shui:booleanSelectEditorScore0-hasNonLiteralNodeKind a shui:Score ;
            shui:shapesGraphShape shui:hasNonLiteralNodeKind ;
            shui:widget shui:BooleanSelectEditor ;
            shui:score 0 .

        shui:booleanSelectEditorScoreNull a shui:Score ;
            shui:shapesGraphShape shui:literalNoDatatypeSpecified ;
            shui:widget shui:BooleanSelectEditor ;
            shui:score -1 .

        shui:datePickerEditorScore10 a shui:Score ;
            shui:dataGraphShape shui:isDate ;
            shui:widget shui:DatePickerEditor ;
            shui:score 10 .

        shui:datePickerEditorScore5 a shui:Score ;
            shui:shapesGraphShape shui:hasDateDatatype ;
            shui:widget shui:DatePickerEditor ;
            shui:score 5 .
        """
        g.parse(data=turtle, format="turtle")
        return g

    @pytest.fixture
    def data_graph(self):
        """Create data graph from example.md."""
        g = Graph()
        turtle = """
        PREFIX ex: <https://example.com/>
        PREFIX schema: <https://schema.org/>

        ex:user-a a schema:Person ;
            ex:isAdmin true .
        """
        g.parse(data=turtle, format="turtle")
        return g

    def test_example_1_data_graph_only(
        self, widget_scoring_graph, data_graph_shapes, shapes_graph_shapes
    ):
        """Test Example 1: Data graph only.

        All shapesGraphShape scores without targets will pass validation.
        This includes scores with shui:hasDatatype, shui:hasDateDatatype,
        shui:literalNoDatatypeSpecified, and shui:hasNonLiteralNodeKind.
        """
        value_node = Literal(True)

        result = score_widgets(
            value_node=value_node,
            widget_scoring_graph=widget_scoring_graph,
            data_graph_shapes_graph=data_graph_shapes,
            shapes_graph_shapes_graph=shapes_graph_shapes,
        )

        # Should include all scores that pass validation
        # BooleanSelectEditor: score 10 (dataGraphShape), two scores 0 (shapesGraphShape), score -1 (shapesGraphShape)
        # DatePickerEditor: score 5 (shapesGraphShape)
        # Note: shapes without targets validate trivially against empty shapes graph
        assert len(result.widget_scores) == 5

        # Results should be sorted by score descending
        assert result.widget_scores[0].score == Decimal("10")
        assert result.widget_scores[0].widget == SHUI.BooleanSelectEditor

        # Default should be highest score
        assert result.default_widget == SHUI.BooleanSelectEditor
        assert result.default_score == Decimal("10")

    def test_example_2_with_non_literal_constraint(
        self, widget_scoring_graph, data_graph_shapes, shapes_graph_shapes
    ):
        """Test Example 2: With shapes graph constraining to non-literal - should return scores 10 and 0."""
        value_node = Literal(True)

        # Create shapes graph with non-literal constraint
        shapes_graph = Graph()
        turtle = """
        PREFIX ex: <https://example.com/>
        PREFIX sh: <http://www.w3.org/ns/shacl#>

        ex:PersonIsAdminShape a sh:PropertyShape ;
            sh:path ex:isAdmin ;
            sh:nodeKind sh:BlankNodeOrIRI .
        """
        shapes_graph.parse(data=turtle, format="turtle")

        result = score_widgets(
            value_node=value_node,
            widget_scoring_graph=widget_scoring_graph,
            constraint_shape=EX.PersonIsAdminShape,
            shapes_graph=shapes_graph,
            data_graph_shapes_graph=data_graph_shapes,
            shapes_graph_shapes_graph=shapes_graph_shapes,
        )

        # Verify we get BooleanSelectEditor with score 10 and 0
        boolean_scores = [
            ws for ws in result.widget_scores if ws.widget == SHUI.BooleanSelectEditor
        ]
        assert len(boolean_scores) >= 2
        scores = [ws.score for ws in boolean_scores]
        assert Decimal("10") in scores
        assert Decimal("0") in scores

        assert result.default_widget == SHUI.BooleanSelectEditor
        assert result.default_score == Decimal("10")

    def test_example_3_with_date_constraint(
        self, widget_scoring_graph, data_graph_shapes, shapes_graph_shapes
    ):
        """Test Example 3: With shapes graph constraining to date - should return BooleanSelectEditor (10) and DatePickerEditor (5)."""
        value_node = Literal(True)

        # Create shapes graph with date constraint
        shapes_graph = Graph()
        turtle = """
        PREFIX ex: <https://example.com/>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        ex:PersonIsAdminShape a sh:PropertyShape ;
            sh:path ex:isAdmin ;
            sh:datatype xsd:date .
        """
        shapes_graph.parse(data=turtle, format="turtle")

        result = score_widgets(
            value_node=value_node,
            widget_scoring_graph=widget_scoring_graph,
            constraint_shape=EX.PersonIsAdminShape,
            shapes_graph=shapes_graph,
            data_graph_shapes_graph=data_graph_shapes,
            shapes_graph_shapes_graph=shapes_graph_shapes,
        )

        # Should match booleanSelectEditorScore10 (10) and datePickerEditorScore5 (5)
        # May also match zero scores for BooleanSelectEditor
        all_scores = [(ws.widget, ws.score) for ws in result.widget_scores]

        # Check for expected scores
        assert (SHUI.BooleanSelectEditor, Decimal("10")) in all_scores
        assert (SHUI.DatePickerEditor, Decimal("5")) in all_scores

        assert result.default_widget == SHUI.BooleanSelectEditor
        assert result.default_score == Decimal("10")

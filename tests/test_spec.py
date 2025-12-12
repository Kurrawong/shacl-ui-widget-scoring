import unittest
from decimal import Decimal
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, XSD
from shui_widget_scoring import score_widgets, SHUI, SH

# Define example namespace
EX = Namespace("http://example.org/")


class TestSpecCompliance(unittest.TestCase):
    def setUp(self):
        self.scoring_graph = Graph()
        # Common shapes
        self.scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
        self.scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

        self.scoring_graph.add((EX.DateShape, RDF.type, SH.NodeShape))
        self.scoring_graph.add((EX.DateShape, SH.datatype, XSD.date))

        self.scoring_graph.add((EX.hasDateDatatype, RDF.type, SH.NodeShape))
        # Structure for hasDateDatatype as per spec example
        # sh:property [ sh:path sh:datatype ; sh:in (xsd:date) ]
        bn = URIRef(EX.bn1)  # using URI for stability or BNode
        self.scoring_graph.add((EX.hasDateDatatype, SH.property, bn))
        self.scoring_graph.add((bn, SH.path, SH.datatype))
        # Simplified for test: sh:hasValue xsd:date instead of sh:in (xsd:date) for easier setup if pyshacl supports it,
        # but spec says sh:in. Let's stick to simple property shape check first or just mock the shape graph content.
        # Actually, let's replicate the spec example exactly.
        # But wait, building the list for sh:in in rdflib is verbose.
        # Let's verify what core.py does. It uses pyshacl.

        # We need a shapes graph for semantic validation of Constraint Shapes.
        self.shapes_graph = Graph()
        self.shapes_graph.add((EX.MyPropShape, RDF.type, SH.PropertyShape))
        self.shapes_graph.add((EX.MyPropShape, SH.datatype, XSD.date))

        # Now define the meta-shape that matches this in the scoring graph
        # The spec example:
        # shui:hasDateDatatype a sh:NodeShape ;
        #     sh:property [
        #       sh:path sh:datatype ;
        #       sh:in (xsd:date)
        #     ] .
        # The Constraint Shape (EX.MyPropShape) has (SH.datatype, XSD.date).
        # So we want to check if EX.MyPropShape has sh:datatype being xsd:date.
        # The meta-shape checks the shape definition.

        # Let's simplify the meta-shape for the test to just "sh:property [ sh:path sh:datatype ; sh:hasValue xsd:date ]"
        # because constructing sh:in list in pure RDFLib without helper is annoying.
        bn2 = URIRef(EX.bn2)
        self.scoring_graph.add((EX.hasDateDatatype, SH.property, bn2))
        self.scoring_graph.add((bn2, SH.path, SH.datatype))
        self.scoring_graph.add((bn2, SH.hasValue, XSD.date))

    def test_spec_example_5_2_boolean(self):
        """Test the boolean example from Spec 5.2"""
        # shui:booleanSelectEditorScore10
        self.scoring_graph.add((EX.BooleanScore, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.BooleanScore, SHUI.dataGraphShape, EX.BooleanShape))
        self.scoring_graph.add((EX.BooleanScore, SHUI.widget, EX.BooleanSelectEditor))
        self.scoring_graph.add((EX.BooleanScore, SHUI.score, Literal(Decimal("10"))))

        # Test with boolean literal
        value_node = Literal(True)
        result = score_widgets(
            value_node=value_node, widget_scoring_graph=self.scoring_graph
        )

        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_widget, EX.BooleanSelectEditor)
        self.assertEqual(result.default_score, Decimal("10"))

    def test_spec_example_5_2_date_constraint(self):
        """Test the date constraint example from Spec 5.2"""
        # shui:datePickerEditorScore5
        self.scoring_graph.add((EX.DateScore, RDF.type, SHUI.Score))
        self.scoring_graph.add(
            (EX.DateScore, SHUI.shapesGraphShape, EX.hasDateDatatype)
        )
        self.scoring_graph.add((EX.DateScore, SHUI.widget, EX.DatePickerEditor))
        self.scoring_graph.add((EX.DateScore, SHUI.score, Literal(Decimal("5"))))

        # Value node can be anything, but we need a constraint shape
        value_node = Literal("2025-01-01", datatype=XSD.date)

        # Constraint Shape: EX.MyPropShape has sh:datatype xsd:date
        result = score_widgets(
            value_node=value_node,
            widget_scoring_graph=self.scoring_graph,
            constraint_shape=EX.MyPropShape,
            shapes_graph=self.shapes_graph,
        )

        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_widget, EX.DatePickerEditor)
        self.assertEqual(result.default_score, Decimal("5"))


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.scoring_graph = Graph()
        self.scoring_graph.add(
            (EX.AlwaysTrue, RDF.type, SH.NodeShape)
        )  # Empty shape matches everything in theory?
        # Actually pyshacl might require something.
        # Let's use no shape in Score to test "Empty Score Conditions" (6.1)

    def test_6_1_empty_score_conditions(self):
        """Test 6.1: Score with no shapes is always valid"""
        self.scoring_graph.add((EX.DefaultScore, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.DefaultScore, SHUI.widget, EX.TextEditor))
        self.scoring_graph.add((EX.DefaultScore, SHUI.score, Literal(Decimal("1"))))

        result = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )
        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_widget, EX.TextEditor)
        self.assertEqual(result.default_score, Decimal("1"))

    def test_6_2_negative_scores(self):
        """Test 6.2: Negative scores are valid and sorted correctly"""
        # Score 10
        self.scoring_graph.add((EX.High, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.High, SHUI.widget, EX.TopWidget))
        self.scoring_graph.add((EX.High, SHUI.score, Literal(Decimal("10"))))

        # Score -5
        self.scoring_graph.add((EX.Negative, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.Negative, SHUI.widget, EX.BottomWidget))
        self.scoring_graph.add((EX.Negative, SHUI.score, Literal(Decimal("-5"))))

        result = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )

        self.assertEqual(len(result.widget_scores), 2)
        self.assertEqual(result.widget_scores[0].widget, EX.TopWidget)
        self.assertEqual(result.widget_scores[1].widget, EX.BottomWidget)
        self.assertEqual(result.widget_scores[1].score, Decimal("-5"))

    def test_6_3_zero_scores(self):
        """Test 6.3: Zero scores are valid"""
        self.scoring_graph.add((EX.Zero, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.Zero, SHUI.widget, EX.ZeroWidget))
        self.scoring_graph.add((EX.Zero, SHUI.score, Literal(Decimal("0"))))

        result = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )
        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_score, Decimal("0"))

    def test_6_4_multiple_scores_same_widget(self):
        """Test 6.4: Max score precedence for same widget"""
        # Score 10 for WidgetA
        self.scoring_graph.add((EX.Score1, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.Score1, SHUI.widget, EX.WidgetA))
        self.scoring_graph.add((EX.Score1, SHUI.score, Literal(Decimal("10"))))

        # Score 5 for WidgetA
        self.scoring_graph.add((EX.Score2, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.Score2, SHUI.widget, EX.WidgetA))
        self.scoring_graph.add((EX.Score2, SHUI.score, Literal(Decimal("5"))))

        result = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )

        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_widget, EX.WidgetA)
        self.assertEqual(result.default_score, Decimal("10"))

    def test_6_5_missing_constraint_shape(self):
        """Test 6.5: Score requiring shapesGraphShape fails if no constraint shape provided"""
        self.scoring_graph.add((EX.ShapeScore, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.ShapeScore, SHUI.widget, EX.ShapeWidget))
        self.scoring_graph.add((EX.ShapeScore, SHUI.score, Literal(Decimal("5"))))
        self.scoring_graph.add((EX.ShapeScore, SHUI.shapesGraphShape, EX.SomeShape))

        # Define EX.SomeShape so it's valid RDF, even if empty
        self.scoring_graph.add((EX.SomeShape, RDF.type, SH.NodeShape))

        # Call WITHOUT constraint_shape
        result = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )

        # Should be empty because the condition cannot be evaluated
        self.assertEqual(len(result.widget_scores), 0)

    def test_complex_shacl_hasValue_constraint(self):
        """Test strict spec example correctness using sh:hasValue"""
        prop_shape = BNode()
        self.scoring_graph.add((EX.HasValueShape, RDF.type, SH.NodeShape))
        self.scoring_graph.add((EX.HasValueShape, SH.property, prop_shape))
        self.scoring_graph.add((prop_shape, SH.path, SH.datatype))
        self.scoring_graph.add((prop_shape, SH.hasValue, XSD.date))

        self.scoring_graph.add((EX.HasValueScore, RDF.type, SHUI.Score))
        self.scoring_graph.add(
            (EX.HasValueScore, SHUI.shapesGraphShape, EX.HasValueShape)
        )
        self.scoring_graph.add((EX.HasValueScore, SHUI.widget, EX.HasValueWidget))
        self.scoring_graph.add((EX.HasValueScore, SHUI.score, Literal(Decimal("5"))))

        # Good Shape
        constraint_shape = EX.GoodShape2
        self.shapes_graph = Graph()
        self.shapes_graph.add((constraint_shape, RDF.type, SH.PropertyShape))
        self.shapes_graph.add((constraint_shape, SH.datatype, XSD.date))

        result = score_widgets(
            value_node=Literal("foo"),
            widget_scoring_graph=self.scoring_graph,
            constraint_shape=constraint_shape,
            shapes_graph=self.shapes_graph,
        )
        self.assertEqual(len(result.widget_scores), 1)

        # Bad Shape
        constraint_shape_bad = EX.BadShape2
        self.shapes_graph.add((constraint_shape_bad, RDF.type, SH.PropertyShape))
        self.shapes_graph.add((constraint_shape_bad, SH.datatype, XSD.string))

        result_bad = score_widgets(
            value_node=Literal("foo"),
            widget_scoring_graph=self.scoring_graph,
            constraint_shape=constraint_shape_bad,
            shapes_graph=self.shapes_graph,
        )
        self.assertEqual(len(result_bad.widget_scores), 0)

    def test_complex_shacl_in_constraint(self):
        """Test strict spec example correctness using sh:in list"""
        # shui:hasDateDatatype a sh:NodeShape ;
        #     sh:property [
        #       sh:path sh:datatype ;
        #       sh:in (xsd:date)
        #     ] .

        # Creating the list structure for sh:in (xsd:date)
        # list node -> first: xsd:date, rest: rdf:nil
        list_node = BNode()
        self.scoring_graph.add((list_node, RDF.first, XSD.date))
        self.scoring_graph.add((list_node, RDF.rest, RDF.nil))

        prop_shape = BNode()
        self.scoring_graph.add((EX.ComplexShape, RDF.type, SH.NodeShape))
        self.scoring_graph.add((EX.ComplexShape, SH.property, prop_shape))
        self.scoring_graph.add((prop_shape, SH.path, SH.datatype))
        self.scoring_graph.add((prop_shape, SH["in"], list_node))

        self.scoring_graph.add((EX.ComplexScore, RDF.type, SHUI.Score))
        self.scoring_graph.add(
            (EX.ComplexScore, SHUI.shapesGraphShape, EX.ComplexShape)
        )
        self.scoring_graph.add((EX.ComplexScore, SHUI.widget, EX.ComplexWidget))
        self.scoring_graph.add((EX.ComplexScore, SHUI.score, Literal(Decimal("5"))))

        # Constraint Shape with correct datatype
        constraint_shape = EX.GoodShape
        self.shapes_graph = Graph()
        self.shapes_graph.add((constraint_shape, RDF.type, SH.PropertyShape))
        self.shapes_graph.add((constraint_shape, SH.datatype, XSD.date))

        result = score_widgets(
            value_node=Literal("foo"),  # Irrelevant for shapesGraphShape check
            widget_scoring_graph=self.scoring_graph,
            constraint_shape=constraint_shape,
            shapes_graph=self.shapes_graph,
        )
        self.assertEqual(len(result.widget_scores), 1)
        self.assertEqual(result.default_widget, EX.ComplexWidget)

        # Constraint Shape with WRONG datatype
        constraint_shape_bad = EX.BadShape
        self.shapes_graph.add((constraint_shape_bad, RDF.type, SH.PropertyShape))
        self.shapes_graph.add(
            (constraint_shape_bad, SH.datatype, XSD.string)
        )  # string != date

        result_bad = score_widgets(
            value_node=Literal("foo"),
            widget_scoring_graph=self.scoring_graph,
            constraint_shape=constraint_shape_bad,
            shapes_graph=self.shapes_graph,
        )
        self.assertEqual(len(result_bad.widget_scores), 0)

    def test_literal_complex_shape(self):
        """Test complex validation for Literal value node (pyshacl fallback)"""
        # Define a shape that requires string length >= 3
        # shui:minLengthShape
        self.scoring_graph.add((EX.MinLengthShape, RDF.type, SH.NodeShape))
        self.scoring_graph.add((EX.MinLengthShape, SH.datatype, XSD.string))
        self.scoring_graph.add((EX.MinLengthShape, SH.minLength, Literal(3)))

        # Score relies on this data graph shape
        self.scoring_graph.add((EX.LengthScore, RDF.type, SHUI.Score))
        self.scoring_graph.add((EX.LengthScore, SHUI.dataGraphShape, EX.MinLengthShape))
        self.scoring_graph.add((EX.LengthScore, SHUI.widget, EX.LengthWidget))
        self.scoring_graph.add((EX.LengthScore, SHUI.score, Literal(Decimal("5"))))

        # "foo" has length 3 -> Match
        result_match = score_widgets(
            value_node=Literal("foo"), widget_scoring_graph=self.scoring_graph
        )
        self.assertEqual(len(result_match.widget_scores), 1)
        self.assertEqual(result_match.default_widget, EX.LengthWidget)

        # "fo" has length 2 -> No Match
        result_no_match = score_widgets(
            value_node=Literal("fo"), widget_scoring_graph=self.scoring_graph
        )
        self.assertEqual(len(result_no_match.widget_scores), 0)


if __name__ == "__main__":
    unittest.main()

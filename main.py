"""Demo/CLI for SHACL UI Widget Scoring library."""

from decimal import Decimal

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

from shui_widget_scoring import score_widgets, SHUI, SH


# Define example namespace
EX = Namespace("http://example.org/")


def create_example_shapes_and_scores():
    """Create example widget scoring graph with shapes and scores."""
    scoring_graph = Graph()

    # Define shapes for data graph validation
    # Boolean shape
    scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
    scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

    # Date shape
    scoring_graph.add((EX.DateShape, RDF.type, SH.NodeShape))
    scoring_graph.add((EX.DateShape, SH.datatype, XSD.date))

    # String shape
    scoring_graph.add((EX.StringShape, RDF.type, SH.NodeShape))
    scoring_graph.add((EX.StringShape, SH.datatype, XSD.string))

    # Define Score instances
    # High score for boolean values → BooleanSelectEditor
    scoring_graph.add((EX.BooleanScore, RDF.type, SHUI.Score))
    scoring_graph.add((EX.BooleanScore, SHUI.widget, EX.BooleanSelectEditor))
    scoring_graph.add((EX.BooleanScore, SHUI.score, Literal(Decimal("10"))))
    scoring_graph.add((EX.BooleanScore, SHUI.dataGraphShape, EX.BooleanShape))

    # Medium score for date values → DatePickerEditor
    scoring_graph.add((EX.DateScore, RDF.type, SHUI.Score))
    scoring_graph.add((EX.DateScore, SHUI.widget, EX.DatePickerEditor))
    scoring_graph.add((EX.DateScore, SHUI.score, Literal(Decimal("8"))))
    scoring_graph.add((EX.DateScore, SHUI.dataGraphShape, EX.DateShape))

    # Low score for string values → TextEditor
    scoring_graph.add((EX.StringScore, RDF.type, SHUI.Score))
    scoring_graph.add((EX.StringScore, SHUI.widget, EX.TextEditor))
    scoring_graph.add((EX.StringScore, SHUI.score, Literal(Decimal("5"))))
    scoring_graph.add((EX.StringScore, SHUI.dataGraphShape, EX.StringShape))

    # Fallback score for any value → GenericEditor
    scoring_graph.add((EX.FallbackScore, RDF.type, SHUI.Score))
    scoring_graph.add((EX.FallbackScore, SHUI.widget, EX.GenericEditor))
    scoring_graph.add((EX.FallbackScore, SHUI.score, Literal(Decimal("1"))))

    return scoring_graph


def demo_boolean_value():
    """Demo scoring for a boolean value."""
    print("\n" + "="*60)
    print("Demo 1: Scoring widgets for a boolean value")
    print("="*60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal(True)

    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph
    )

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype}")
    print(f"\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}")


def demo_date_value():
    """Demo scoring for a date value."""
    print("\n" + "="*60)
    print("Demo 2: Scoring widgets for a date value")
    print("="*60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal("2025-01-15", datatype=XSD.date)

    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph
    )

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype}")
    print(f"\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}")


def demo_string_value():
    """Demo scoring for a string value."""
    print("\n" + "="*60)
    print("Demo 3: Scoring widgets for a string value")
    print("="*60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal("Hello, World!")

    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph
    )

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype or 'xsd:string (implicit)'}")
    print(f"\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}")


def demo_filtering_by_score():
    """Demo filtering widgets by minimum score."""
    print("\n" + "="*60)
    print("Demo 4: Filtering widgets by minimum score")
    print("="*60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal(True)

    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph
    )

    print(f"\nValue: {value_node}")
    print(f"\nAll widgets (including low scores):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(f"\nWidgets with score >= 5:")
    high_scoring = result.get_widgets_with_min_score(Decimal("5"))
    for ws in high_scoring:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("SHACL UI Widget Scoring - Demo")
    print("="*60)

    demo_boolean_value()
    demo_date_value()
    demo_string_value()
    demo_filtering_by_score()

    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

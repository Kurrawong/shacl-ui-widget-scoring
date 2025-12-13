"""Demo/CLI for SHACL UI Widget Scoring library."""

from decimal import Decimal

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import XSD

from shui_widget_scoring import score_widgets


# Define example namespace
EX = Namespace("http://example.org/")


def create_example_shapes_and_scores():
    """Create example widget scoring graph with shapes and scores."""
    scoring_graph = Graph()

    # Define shapes for data graph validation and Score instances using Turtle
    turtle_data = """
        PREFIX shui: <http://www.w3.org/ns/shacl-ui#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.org/>

        # Define shapes for data graph validation

        # Boolean shape
        ex:BooleanShape
            a sh:NodeShape ;
            sh:datatype xsd:boolean .

        # Date shape
        ex:DateShape
            a sh:NodeShape ;
            sh:datatype xsd:date .

        # String shape
        ex:StringShape
            a sh:NodeShape ;
            sh:datatype xsd:string .

        # Define Score instances

        # High score for boolean values → BooleanSelectEditor
        ex:BooleanScore
            a shui:Score ;
            shui:dataGraphShape ex:BooleanShape ;
            shui:score 10.0 ;
            shui:widget ex:BooleanSelectEditor .

        # Medium score for date values → DatePickerEditor
        ex:DateScore
            a shui:Score ;
            shui:dataGraphShape ex:DateShape ;
            shui:score 8.0 ;
            shui:widget ex:DatePickerEditor .

        # Low score for string values → TextEditor
        ex:StringScore
            a shui:Score ;
            shui:dataGraphShape ex:StringShape ;
            shui:score 5.0 ;
            shui:widget ex:TextEditor .

        # Fallback score for any value → GenericEditor
        ex:FallbackScore
            a shui:Score ;
            shui:score 1.0 ;
            shui:widget ex:GenericEditor .
    """

    scoring_graph.parse(data=turtle_data, format="turtle")
    return scoring_graph


def demo_boolean_value():
    """Demo scoring for a boolean value."""
    print("\n" + "=" * 60)
    print("Demo 1: Scoring widgets for a boolean value")
    print("=" * 60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal(True)

    result = score_widgets(value_node=value_node, widget_scoring_graph=scoring_graph)

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype}")
    print("\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(
        f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}"
    )


def demo_date_value():
    """Demo scoring for a date value."""
    print("\n" + "=" * 60)
    print("Demo 2: Scoring widgets for a date value")
    print("=" * 60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal("2025-01-15", datatype=XSD.date)

    result = score_widgets(value_node=value_node, widget_scoring_graph=scoring_graph)

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype}")
    print("\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(
        f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}"
    )


def demo_string_value():
    """Demo scoring for a string value."""
    print("\n" + "=" * 60)
    print("Demo 3: Scoring widgets for a string value")
    print("=" * 60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal("Hello, World!")

    result = score_widgets(value_node=value_node, widget_scoring_graph=scoring_graph)

    print(f"\nValue: {value_node}")
    print(f"Type: {value_node.datatype or 'xsd:string (implicit)'}")
    print("\nWidget Recommendations (sorted by score):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print(
        f"\nDefault (highest-scoring) widget: {str(result.default_widget).split('/')[-1]}"
    )


def demo_filtering_by_score():
    """Demo filtering widgets by minimum score."""
    print("\n" + "=" * 60)
    print("Demo 4: Filtering widgets by minimum score")
    print("=" * 60)

    scoring_graph = create_example_shapes_and_scores()
    value_node = Literal(True)

    result = score_widgets(value_node=value_node, widget_scoring_graph=scoring_graph)

    print(f"\nValue: {value_node}")
    print("\nAll widgets (including low scores):")
    for ws in result.widget_scores:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")

    print("\nWidgets with score >= 5:")
    high_scoring = result.get_widgets_with_min_score(Decimal("5"))
    for ws in high_scoring:
        widget_name = str(ws.widget).split("/")[-1]
        print(f"  - {widget_name}: {ws.score}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("SHACL UI Widget Scoring - Demo")
    print("=" * 60)

    demo_boolean_value()
    demo_date_value()
    demo_string_value()
    demo_filtering_by_score()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

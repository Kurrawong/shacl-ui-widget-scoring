"""
Demonstration of SHACL UI Widget Scoring Algorithm.

This script demonstrates the three examples from example.md, showing how the
widget scoring algorithm selects appropriate widgets based on data graphs,
shapes graphs, and their constraints.
"""

import json
from decimal import Decimal
from typing import List

from rdflib import Graph, Literal, Namespace, URIRef, RDF

from shui_widget_scoring import score_widgets, SHUI, ScoringResult

# Define namespaces
EX = Namespace("https://example.com/")
SCHEMA = Namespace("https://schema.org/")


def create_data_graph_shapes() -> Graph:
    """Create data graph shapes (for validating value nodes)."""
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


def create_shapes_graph_shapes() -> Graph:
    """Create shapes graph shapes (for validating constraint shapes)."""
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


def create_widget_scoring_graph() -> Graph:
    """Create widget scoring graph (Score instances only)."""
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


def create_data_graph() -> Graph:
    """Create the example data graph."""
    data_graph = Graph()

    turtle_data = """
PREFIX ex: <https://example.com/>
PREFIX schema: <https://schema.org/>

ex:user-a a schema:Person ;
    ex:isAdmin true .
"""

    data_graph.parse(data=turtle_data, format="turtle")
    return data_graph


def create_shapes_graph_example2() -> Graph:
    """
    Create shapes graph for Example 2.

    This graph constrains ex:isAdmin to non-literal values.
    """
    shapes_graph = Graph()

    turtle_data = """
PREFIX ex: <https://example.com/>
PREFIX schema: <https://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>

ex:PersonIsAdminShape a sh:PropertyShape ;
    sh:path ex:isAdmin ;
    sh:nodeKind sh:BlankNodeOrIRI .
"""

    shapes_graph.parse(data=turtle_data, format="turtle")
    return shapes_graph


def create_shapes_graph_example3() -> Graph:
    """
    Create shapes graph for Example 3.

    This graph constrains ex:isAdmin to date values.
    """
    shapes_graph = Graph()

    turtle_data = """
PREFIX ex: <https://example.com/>
PREFIX schema: <https://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

ex:PersonIsAdminShape a sh:PropertyShape ;
    sh:path ex:isAdmin ;
    sh:datatype xsd:date .
"""

    shapes_graph.parse(data=turtle_data, format="turtle")
    return shapes_graph


def serialize_graph_section(
    graph: Graph,
    title: str,
) -> str:
    """
    Serialize a graph to Turtle format.
    """
    turtle = graph.serialize(format="turtle")

    output = f"{title}:\n"
    output += "-" * len(title) + "\n"
    output += turtle
    return output


def find_matching_score_instances(
    scoring_graph: Graph,
    widget: URIRef,
    score: Decimal,
) -> List[URIRef]:
    """Find Score instance URIs that match widget and score."""
    results = []
    for score_uri in scoring_graph.subjects(RDF.type, SHUI.Score):
        widget_match = scoring_graph.value(score_uri, SHUI.widget) == widget
        score_match = Decimal(str(scoring_graph.value(score_uri, SHUI.score))) == score
        if widget_match and score_match:
            results.append(score_uri)
    return results


def format_results_as_json(
    result: ScoringResult,
    scoring_graph: Graph,
) -> str:
    """Format scoring results as JSON matching example.md format."""
    output_dict = {}

    for widget_score in result.widget_scores:
        # Find matching score instances
        score_instances = find_matching_score_instances(
            scoring_graph, widget_score.widget, widget_score.score
        )

        for score_instance in score_instances:
            # Get the last part of the URI for a cleaner key
            score_key = str(score_instance).split("/")[-1]

            output_dict[score_key] = {
                "shui:widget": str(widget_score.widget).split("/")[-1],
                "shui:score": int(widget_score.score),
            }

    return json.dumps(output_dict, indent=2)


def format_value_node(value_node) -> str:
    """Format a value node for display."""
    if isinstance(value_node, Literal):
        datatype = value_node.datatype
        if datatype:
            datatype_str = str(datatype).split("/")[-1]
            return f"{value_node} ({datatype_str})"
        else:
            return str(value_node)
    return str(value_node)


def run_example_1(
    scoring_graph: Graph, data_graph_shapes: Graph, shapes_graph_shapes: Graph
) -> None:
    """Run Example 1: Data graph only."""
    print("\n" + "=" * 80)
    print("Example 1: Data graph only")
    print("=" * 80)

    # Create data graph
    data_graph = create_data_graph()

    # Value node to score
    value_node = Literal(True)

    print("\nData Graph:")
    print("-" * 80)
    print(data_graph.serialize(format="turtle"))

    print("\nData Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(data_graph_shapes, ""))

    print("\nShapes Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(shapes_graph_shapes, ""))

    print("\nWidget Scoring Graph - Widget Scores:")
    print("-" * 80)
    print(serialize_graph_section(scoring_graph, ""))

    # Score the widgets
    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph,
        data_graph_shapes_graph=data_graph_shapes,
        shapes_graph_shapes_graph=shapes_graph_shapes,
    )

    print("\nScoring Results:")
    print("-" * 80)
    print(f"Value Node: {format_value_node(value_node)}\n")
    print("Matched Scores (JSON):")
    print(format_results_as_json(result, scoring_graph))

    if result.default_widget:
        widget_name = str(result.default_widget).split("/")[-1]
        print(f"\nDefault Widget: {widget_name} (score: {result.default_score})")


def run_example_2(
    scoring_graph: Graph, data_graph_shapes: Graph, shapes_graph_shapes: Graph
) -> None:
    """Run Example 2: Data graph + shapes graph with non-literal constraint."""
    print("\n" + "=" * 80)
    print("Example 2: Data graph + shapes graph (non-literal constraint)")
    print("=" * 80)

    # Create graphs
    data_graph = create_data_graph()
    shapes_graph = create_shapes_graph_example2()

    # Value node to score
    value_node = Literal(True)

    # Get constraint shape
    constraint_shape = EX.PersonIsAdminShape

    print("\nData Graph:")
    print("-" * 80)
    print(data_graph.serialize(format="turtle"))

    print("\nShapes Graph:")
    print("-" * 80)
    print(shapes_graph.serialize(format="turtle"))

    print("\nData Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(data_graph_shapes, ""))

    print("\nShapes Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(shapes_graph_shapes, ""))

    print("\nWidget Scoring Graph - Widget Scores:")
    print("-" * 80)
    print(serialize_graph_section(scoring_graph, ""))

    # Score the widgets
    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph,
        constraint_shape=constraint_shape,
        shapes_graph=shapes_graph,
        data_graph_shapes_graph=data_graph_shapes,
        shapes_graph_shapes_graph=shapes_graph_shapes,
    )

    print("\nScoring Results:")
    print("-" * 80)
    print(f"Value Node: {format_value_node(value_node)}")
    print(f"Constraint Shape: {constraint_shape}\n")
    print("Matched Scores (JSON):")
    print(format_results_as_json(result, scoring_graph))

    if result.default_widget:
        widget_name = str(result.default_widget).split("/")[-1]
        print(f"\nDefault Widget: {widget_name} (score: {result.default_score})")


def run_example_3(
    scoring_graph: Graph, data_graph_shapes: Graph, shapes_graph_shapes: Graph
) -> None:
    """Run Example 3: Data graph + shapes graph with date constraint."""
    print("\n" + "=" * 80)
    print("Example 3: Data graph + shapes graph (date datatype constraint)")
    print("=" * 80)

    # Create graphs
    data_graph = create_data_graph()
    shapes_graph = create_shapes_graph_example3()

    # Value node to score
    value_node = Literal(True)

    # Get constraint shape
    constraint_shape = EX.PersonIsAdminShape

    print("\nData Graph:")
    print("-" * 80)
    print(data_graph.serialize(format="turtle"))

    print("\nShapes Graph:")
    print("-" * 80)
    print(shapes_graph.serialize(format="turtle"))

    print("\nData Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(data_graph_shapes, ""))

    print("\nShapes Graph Shapes:")
    print("-" * 80)
    print(serialize_graph_section(shapes_graph_shapes, ""))

    print("\nWidget Scoring Graph - Widget Scores:")
    print("-" * 80)
    print(serialize_graph_section(scoring_graph, ""))

    # Score the widgets
    result = score_widgets(
        value_node=value_node,
        widget_scoring_graph=scoring_graph,
        constraint_shape=constraint_shape,
        shapes_graph=shapes_graph,
        data_graph_shapes_graph=data_graph_shapes,
        shapes_graph_shapes_graph=shapes_graph_shapes,
    )

    print("\nScoring Results:")
    print("-" * 80)
    print(f"Value Node: {format_value_node(value_node)}")
    print(f"Constraint Shape: {constraint_shape}\n")
    print("Matched Scores (JSON):")
    print(format_results_as_json(result, scoring_graph))

    if result.default_widget:
        widget_name = str(result.default_widget).split("/")[-1]
        print(f"\nDefault Widget: {widget_name} (score: {result.default_score})")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("SHACL UI Widget Scoring - Examples from example.md")
    print("=" * 80)

    # Create the three separate graphs (shared across all examples)
    scoring_graph = create_widget_scoring_graph()
    data_graph_shapes = create_data_graph_shapes()
    shapes_graph_shapes = create_shapes_graph_shapes()

    # Run all examples
    run_example_1(scoring_graph, data_graph_shapes, shapes_graph_shapes)
    run_example_2(scoring_graph, data_graph_shapes, shapes_graph_shapes)
    run_example_3(scoring_graph, data_graph_shapes, shapes_graph_shapes)

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Extract examples from the shui-widget-scoring package and generate examples.json
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import example.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shui-widget-scoring"))

from rdflib import Namespace
from example import (
    create_widget_scoring_graph,
    create_data_graph_shapes,
    create_shapes_graph_shapes,
    create_data_graph,
    create_shapes_graph_example2,
    create_shapes_graph_example3,
)

EX = Namespace("https://example.com/")


def serialize_graph(graph):
    """Serialize a graph to Turtle format."""
    return graph.serialize(format="turtle")


def extract_examples():
    """Extract examples and return as a dictionary."""
    # Create shared graphs
    scoring_graph = create_widget_scoring_graph()
    data_graph_shapes = create_data_graph_shapes()
    shapes_graph_shapes = create_shapes_graph_shapes()

    examples = {
        "version": "1.0.0",
        "sharedGraphs": {
            "widgetScoringGraph": serialize_graph(scoring_graph),
            "dataGraphShapes": serialize_graph(data_graph_shapes),
            "shapesGraphShapes": serialize_graph(shapes_graph_shapes),
        },
        "examples": [
            {
                "id": "example1",
                "name": "Data Graph Only",
                "description": "Widget scoring based only on data graph value node",
                "dataGraph": serialize_graph(create_data_graph()),
                "focusNode": "true",  # Literal(True)
                "focusNodeDatatype": "http://www.w3.org/2001/XMLSchema#boolean",
                "shapesGraph": None,
                "constraintShape": None,
            },
            {
                "id": "example2",
                "name": "Data Graph + Shapes Graph (Non-literal Constraint)",
                "description": "Widget scoring with shapes graph constraint requiring non-literal values",
                "dataGraph": serialize_graph(create_data_graph()),
                "focusNode": "true",  # Literal(True)
                "focusNodeDatatype": "http://www.w3.org/2001/XMLSchema#boolean",
                "shapesGraph": serialize_graph(create_shapes_graph_example2()),
                "constraintShape": "https://example.com/PersonIsAdminShape",
            },
            {
                "id": "example3",
                "name": "Data Graph + Shapes Graph (Date Constraint)",
                "description": "Widget scoring with shapes graph constraint requiring date datatype",
                "dataGraph": serialize_graph(create_data_graph()),
                "focusNode": "true",  # Literal(True)
                "focusNodeDatatype": "http://www.w3.org/2001/XMLSchema#boolean",
                "shapesGraph": serialize_graph(create_shapes_graph_example3()),
                "constraintShape": "https://example.com/PersonIsAdminShape",
            },
        ],
    }

    return examples


def main():
    """Main function to generate examples.json"""
    output_dir = Path(__file__).parent.parent / "public"
    output_dir.mkdir(parents=True, exist_ok=True)

    examples = extract_examples()

    output_file = output_dir / "examples.json"
    with open(output_file, "w") as f:
        json.dump(examples, f, indent=2)

    print(f"Examples extracted to {output_file}")
    print(f"Generated {len(examples['examples'])} examples")


if __name__ == "__main__":
    main()

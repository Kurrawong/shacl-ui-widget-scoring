# SHACL UI Widget Scoring

A Python library implementing the SHACL UI Widget Scoring algorithm for automatically selecting the most appropriate UI widgets based on data types and SHACL constraints.

## Overview

This library provides a mechanism to score and rank UI widgets based on:
- The datatype and value of data being edited
- SHACL shape constraints that apply to the data
- Configurable scoring rules defined in RDF

See [spec.md](spec.md) for the complete specification.

## Installation

This package uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Install with development dependencies (for testing)
uv sync --extra dev
```

## Quick Start

```python
from decimal import Decimal
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD
from shui_widget_scoring import score_widgets, SHUI, SH

# Define namespace
EX = Namespace("http://example.org/")

# Create widget scoring graph
scoring_graph = Graph()

# Define a shape for boolean values
scoring_graph.add((EX.BooleanShape, RDF.type, SH.NodeShape))
scoring_graph.add((EX.BooleanShape, SH.datatype, XSD.boolean))

# Define a score: use BooleanSelectEditor for boolean values
scoring_graph.add((EX.BooleanScore, RDF.type, SHUI.Score))
scoring_graph.add((EX.BooleanScore, SHUI.widget, EX.BooleanSelectEditor))
scoring_graph.add((EX.BooleanScore, SHUI.score, Literal(Decimal("10"))))
scoring_graph.add((EX.BooleanScore, SHUI.dataGraphShape, EX.BooleanShape))

# Score widgets for a boolean value
result = score_widgets(
    value_node=Literal(True),
    widget_scoring_graph=scoring_graph
)

# Get the recommended widget
print(f"Recommended widget: {result.default_widget}")
print(f"Score: {result.default_score}")

# Get all widget recommendations
for widget_score in result.widget_scores:
    print(f"{widget_score.widget}: {widget_score.score}")
```

## Usage

### Main API: `score_widgets()`

```python
score_widgets(
    value_node,              # The node to score widgets for (URIRef, BNode, or Literal)
    widget_scoring_graph,    # Graph containing shui:Score instances
    data_graph=None,         # Optional: data graph (required for URIRef/BNode values)
    constraint_shape=None,   # Optional: SHACL shape constraining the value
    shapes_graph=None,       # Optional: shapes graph (required if constraint_shape provided)
    logger=None             # Optional: Python logger for warnings
) -> ScoringResult
```

### Working with Results

The `ScoringResult` object provides several ways to access scoring results:

```python
result = score_widgets(value_node, widget_scoring_graph)

# Get the highest-scoring widget
default_widget = result.default_widget
default_score = result.default_score

# Iterate over all recommendations
for ws in result.widget_scores:
    print(f"Widget: {ws.widget}, Score: {ws.score}")

# Filter widgets by minimum score
high_scoring = result.get_widgets_with_min_score(Decimal("5"))
```

### Defining Score Instances

Score instances are defined in RDF using the `shui:Score` class:

```turtle
@prefix shui: <http://www.w3.org/ns/shacl-ui#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/> .

# Define a shape
ex:DateShape a sh:NodeShape ;
    sh:datatype xsd:date .

# Define a score
ex:DatePickerScore a shui:Score ;
    shui:widget ex:DatePickerEditor ;
    shui:score 10 ;
    shui:dataGraphShape ex:DateShape .
```

### Score Properties

- `shui:widget` (required, exactly one): The widget to be scored
- `shui:score` (required, exactly one): Numeric score (decimal or integer)
  - Positive scores indicate selectable widgets
  - Zero indicates not selectable
  - Negative scores are valid but rarely selected
- `shui:dataGraphShape` (optional, zero or more): Shapes to validate the value node against
- `shui:shapesGraphShape` (optional, zero or more): Shapes to validate the constraint shape against

### Edge Cases

#### Unconditional Scores
Scores with no shape constraints always apply:

```python
# Always suggest a generic text editor with low priority
scoring_graph.add((EX.FallbackScore, SHUI.Score))
scoring_graph.add((EX.FallbackScore, SHUI.widget, EX.TextEditor))
scoring_graph.add((EX.FallbackScore, SHUI.score, Literal(Decimal("1"))))
# No dataGraphShape or shapesGraphShape - always applicable
```

#### Multiple Scores per Widget
When multiple scores match for the same widget, the maximum score is used:

```python
# Score 10 if boolean value
# Score 5 if shape has boolean constraint
# If both conditions met → widget gets score 10 (maximum)
```

#### Negative and Zero Scores
```python
# Zero score = not selectable
scoring_graph.add((EX.ZeroScore, SHUI.score, Literal(Decimal("0"))))

# Negative score = valid but deprioritized
scoring_graph.add((EX.DeprioritizedScore, SHUI.score, Literal(Decimal("-5"))))
```

## Running the Demo

```bash
uv run python main.py
```

This runs demonstrations of:
1. Scoring widgets for boolean values
2. Scoring widgets for date values
3. Scoring widgets for string values
4. Filtering widgets by minimum score

## Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_core.py

# Run with verbose output
uv run pytest -v
```

## Development

### Project Structure

```
shui-widget-scoring/
├── shui_widget_scoring/     # Main package
│   ├── __init__.py          # Public API
│   ├── core.py              # Main scoring algorithm
│   ├── models.py            # Data structures
│   ├── validation.py        # SHACL validation
│   ├── exceptions.py        # Error types
│   └── namespaces.py        # RDF namespaces
├── tests/                   # Test suite
├── main.py                  # Demo/CLI
├── spec.md                  # Algorithm specification
└── pyproject.toml           # Project configuration
```

### Adding Dependencies

```bash
uv add package_name          # Add runtime dependency
uv add --dev package_name    # Add development dependency
```

## Error Handling

The library raises specific exceptions for different error conditions:

```python
from shui_widget_scoring import (
    MalformedScoreError,      # Score instance violates constraints
    InvalidValueNodeError,    # Invalid value_node parameter
    MissingGraphError,        # Required graph not provided
)

try:
    result = score_widgets(value_node, scoring_graph)
except MalformedScoreError as e:
    print(f"Invalid Score instance: {e}")
except InvalidValueNodeError as e:
    print(f"Invalid value node: {e}")
```

## Specification

For the complete algorithm specification, including:
- Detailed scoring rules
- SHACL feature support
- Edge cases and error handling
- Formal algorithm steps

See [spec.md](spec.md).

## License

See LICENSE file for details.

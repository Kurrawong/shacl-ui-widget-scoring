# SHACL UI Widget Scoring

A Python library implementing the [SHACL UI Widget Scoring algorithm](spec.md) for automatically selecting appropriate UI widgets based on data types and SHACL constraints.

## Overview

This library provides a mechanism to score and rank candidate UI widgets based on:

- The datatype and value of data being edited
- SHACL shape constraints that apply to the data
- Configurable scoring rules defined in RDF

The scoring algorithm matches value nodes and constraint shapes against configurable scoring rules, returning a ranked list of suitable widgets with their scores.

## Installation

```bash
# Install the package
pip install shui-widget-scoring

# With development tools (testing, linting)
pip install shui-widget-scoring[dev]
```

Or using `uv`:

```bash
uv add shui-widget-scoring
```

## Quick Start

```python
from rdflib import Graph, Literal
from shui_widget_scoring import score_widgets

# Define scoring rules in Turtle format
turtle_data = """
@prefix shui: <http://www.w3.org/ns/shacl-ui#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/> .

ex:BoolShape a sh:NodeShape ;
    sh:datatype xsd:boolean .

ex:BoolScore a shui:Score ;
    shui:widget ex:BooleanSelectEditor ;
    shui:score 10 ;
    shui:dataGraphShape ex:BoolShape .
"""

# Parse the Turtle data into a graph
scoring_graph = Graph()
scoring_graph.parse(data=turtle_data, format="turtle")

# Score widgets for a boolean value
result = score_widgets(
    value_node=Literal(True),
    widget_scoring_graph=scoring_graph
)

print(f"Recommended: {result.default_widget} ({result.default_score})")
# Output: Recommended: http://example.org/BooleanSelectEditor (10)
```

## API Reference

### `score_widgets()`

```python
score_widgets(
    value_node: URIRef | BNode | Literal,
    widget_scoring_graph: Graph,
    data_graph: Graph | None = None,
    constraint_shape: URIRef | None = None,
    shapes_graph: Graph | None = None,
    logger: logging.Logger | None = None
) -> ScoringResult
```

**Parameters:**

- `value_node`: The node to score widgets for
- `widget_scoring_graph`: Graph containing `shui:Score` instances
- `data_graph`: Optional; required when `value_node` is a URIRef or BNode
- `constraint_shape`: Optional; SHACL shape constraining the value
- `shapes_graph`: Optional; required if `constraint_shape` is provided
- `logger`: Optional; Python logger for validation warnings

**Returns:** `ScoringResult` object with widget scores and recommendations

### `ScoringResult`

```python
result = score_widgets(value_node, widget_scoring_graph)

# Get top recommendation
widget = result.default_widget        # URIRef of highest-scoring widget
score = result.default_score          # Decimal score

# Get all recommendations
for widget_score in result.widget_scores:
    print(f"{widget_score.widget}: {widget_score.score}")

# Filter by minimum score
high_scoring = result.get_widgets_with_min_score(Decimal("5"))
```

## Defining Scoring Rules

Score rules are defined as `shui:Score` instances in RDF:

```turtle
@prefix shui: <http://www.w3.org/ns/shacl-ui#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/> .

# Optional: Define shapes to match against
ex:DateShape a sh:NodeShape ;
    sh:datatype xsd:date .

# Define a score rule
ex:DatePickerScore a shui:Score ;
    shui:widget ex:DatePickerEditor ;
    shui:score 10 ;
    shui:dataGraphShape ex:DateShape .
```

**Score Properties:**

- `shui:widget` (required): The widget URI
- `shui:score` (required): Numeric score (positive, zero, or negative)
- `shui:dataGraphShape` (optional): Shapes to validate the value node against
- `shui:shapesGraphShape` (optional): Shapes to validate the constraint shape against

**Scoring Rules:**

- Positive scores indicate selectable widgets
- Zero or negative scores indicate non-selectable or deprioritized widgets
- When multiple scores match for the same widget, the maximum is used
- Scores with no shape constraints always apply

## Examples

For comprehensive examples demonstrating the full algorithm capabilities, see [example.py](example.py). This file contains three detailed examples showing:

1. Data graph only scoring (no shape constraints)
2. Shape constraint scoring with non-literal requirements
3. Shape constraint scoring with datatype requirements

Run examples with:

```bash
uv run python example.py
```

## Specification

The complete algorithm specification is in [spec.md](spec.md), including:

- Formal scoring algorithm steps
- SHACL feature support
- Edge cases and error handling
- Detailed examples with expected outputs

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_core.py
```

The library has 90% test coverage across 67 tests covering the core algorithm, validation, models, and specification compliance.

## Error Handling

The library raises specific exceptions for error conditions:

```python
from shui_widget_scoring import (
    MalformedScoreError,    # Invalid Score instance
    InvalidValueNodeError,  # Invalid value_node type
    MissingGraphError,      # Required graph not provided
)

try:
    result = score_widgets(value_node, scoring_graph)
except MalformedScoreError as e:
    print(f"Invalid Score: {e}")
except InvalidValueNodeError as e:
    print(f"Invalid value node: {e}")
except MissingGraphError as e:
    print(f"Missing required graph: {e}")
```

## Development

### Setup

```bash
# Install with development dependencies
uv sync --extra dev

# Format and lint code
uv run ruff format .
uv run ruff check --fix .
```

### Project Structure

```
shui_widget_scoring/
├── __init__.py          # Public API
├── core.py              # Scoring algorithm
├── models.py            # Data structures
├── validation.py        # SHACL validation
├── exceptions.py        # Exception types
└── namespaces.py        # RDF namespaces

tests/                   # Test suite
example.py              # Algorithm examples
spec.md                 # Full specification
```

## References

- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [SHACL UI Community Group](https://www.w3.org/community/shacl-ui/)
- [RDFlib Documentation](https://rdflib.readthedocs.io/)
- [pyshacl Documentation](https://pyshacl.readthedocs.io/)

## License

See LICENSE file for details.

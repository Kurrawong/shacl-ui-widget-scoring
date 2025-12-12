# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package that implements the SHACL UI widget scoring algorithm, which determines the best suitable widget to use for a data graph's value node. The project has a working implementation with comprehensive test coverage and follows modern Python packaging standards.

## Development Setup

- **Python Version**: 3.14 (specified in `.python-version`)
- **Package Manager**: `uv` (https://astral.sh/uv/) - handles both dependency management and Python version control
- **Main Dependencies**:
  - `pyshacl>=0.30.1` - SHACL validation and processing
  - `rdflib` - RDF graph operations (via pyshacl)
- **Development Dependencies**:
  - `pytest>=8.0.0` - testing framework
  - `pytest-cov>=4.1.0` - test coverage reporting
  - `ruff>=0.14.9` - code formatting and linting

## Common Commands

### Dependency Management
- **Install/Update dependencies**: `uv sync` (installs all dependencies from `pyproject.toml` and `uv.lock`)
- **Install with dev dependencies**: `uv sync --extra dev` (includes pytest and other dev tools)
- **Add a new dependency**: `uv add package_name` (updates both `pyproject.toml` and `uv.lock`)
- **Add dev dependency**: `uv add --dev package_name`
- **Remove a dependency**: `uv remove package_name`
- **Check for dependency updates**: `uv lock --upgrade`

### Running the Application
- **Run the demo application**: `uv run python main.py`
- **Run a specific Python script**: `uv run python script_name.py`

### Testing
- **Run all tests**: `uv run pytest`
- **Run tests with coverage**: `uv run pytest` (coverage enabled by default in `pyproject.toml`)
- **Run specific test file**: `uv run pytest tests/test_core.py`
- **Run tests with verbose output**: `uv run pytest -v`
- **Run specific test**: `uv run pytest tests/test_core.py::test_function_name`

### Code Quality
- **Format and lint code**: `task code` (runs ruff format + ruff check --fix)
- **Format code only**: `uv run ruff format .`
- **Lint code only**: `uv run ruff check --fix .`

## Architecture

### Package Structure

```
shui_widget_scoring/
├── __init__.py          # Public API exports (score_widgets, SHUI, SH, etc.)
├── core.py              # Main scoring algorithm implementation
├── models.py            # Data structures (WidgetScore, ScoringResult, ScoreInstance)
├── validation.py        # SHACL validation logic
├── exceptions.py        # Custom exception types
└── namespaces.py        # RDF namespace definitions (SHUI, SH, XSD)
```

### Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and shared test setup
├── test_core.py         # Tests for core.py (main scoring algorithm)
├── test_models.py       # Tests for models.py (data structures)
├── test_validation.py   # Tests for validation.py (SHACL validation)
├── test_spec.py         # Tests for spec.md examples and compliance
└── test_edge_cases.py   # Tests for edge cases and error handling
```

### Key Modules

- **`core.py`**: Contains `score_widgets()` function - the main entry point for the scoring algorithm
- **`models.py`**: Defines dataclasses:
  - `WidgetScore`: Widget URI and its score
  - `ScoringResult`: Complete result with all widget scores and default recommendation
  - `ScoreInstance`: Internal representation of a `shui:Score` instance
- **`validation.py`**: SHACL validation using `pyshacl` to check if shapes match value nodes
- **`exceptions.py`**: Custom exceptions:
  - `MalformedScoreError`: Score instance violates constraints
  - `InvalidValueNodeError`: Invalid value_node parameter
  - `MissingGraphError`: Required graph not provided
- **`namespaces.py`**: RDF namespace constants (SHUI, SH, XSD)

### Entry Points

- **`main.py`**: Demo application showing various scoring scenarios
- **Public API**: Import from package root: `from shui_widget_scoring import score_widgets, SHUI, SH`

## Specification

The complete algorithm specification is defined in `spec.md`, which includes:
- SHACL UI scoring rules and semantics
- Shape validation requirements
- Edge cases and error handling
- Formal algorithm steps

The implementation in `shui_widget_scoring/` follows this specification, and `tests/test_spec.py` validates compliance with the examples in the specification.

## Testing Strategy

- **Unit tests**: Each module has dedicated tests
- **Spec compliance**: `test_spec.py` ensures implementation matches specification examples
- **Edge cases**: `test_edge_cases.py` covers error conditions, boundary cases, and unusual inputs
- **Coverage**: Pytest-cov configured to report test coverage automatically

## Development Workflow

1. Make changes to code in `shui_widget_scoring/`
2. Run tests: `uv run pytest`
3. Format and lint: `task code`
4. Verify test coverage in output
5. Update tests if adding new features

## Code Style

- Python 3.14+ features are allowed
- Type hints are encouraged but not required
- Code is formatted and linted with `ruff`
- Follow existing patterns in the codebase

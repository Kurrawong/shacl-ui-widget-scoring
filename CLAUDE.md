# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SHACL UI Widget Scoring** is a Python library that implements the SHACL UI widget scoring algorithm, which determines the best suitable widget to use for a data graph's value node based on data types and SHACL constraints.

- **Package Name**: `shui-widget-score`
- **Version**: 0.1.0
- **Python**: 3.14+
- **Status**: Fully functional with comprehensive test coverage
- **Test Coverage**: 90% (67 tests passing)
- **Architecture**: Modular, production-ready Python package following modern packaging standards

## Development Setup

- **Python Version**: 3.14 (specified in `.python-version`)
- **Package Manager**: `uv` (https://astral.sh/uv/) - handles both dependency management and Python version control
- **Main Dependencies**:
  - `pyshacl>=0.30.1` - SHACL validation and processing
  - `rdflib` - RDF graph operations (via pyshacl as transitive dependency)
- **Development Dependencies** (defined in `pyproject.toml` under `[project.optional-dependencies.dev]`):
  - `pytest>=8.0.0` - testing framework
  - `pytest-cov>=4.1.0` - test coverage reporting
- **Code Quality** (defined in `pyproject.toml` under `[dependency-groups.dev]`):
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

- **Run the examples**: `uv run python example.py`
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
- **`exceptions.py`**: Custom exception hierarchy:
  - `ShuiWidgetScoringError`: Base exception class (parent of all custom exceptions)
  - `MalformedScoreError`: Score instance violates SHACL constraints
  - `InvalidValueNodeError`: Invalid value_node parameter type
  - `MissingGraphError`: Required graph not provided for validation
- **`namespaces.py`**: RDF namespace constants (SHUI, SH, XSD)

### Entry Points

- **`example.py`**: Examples demonstrating the widget scoring algorithm with comprehensive Turtle-based RDF definitions
- **Public API** (defined in `__init__.py`, import from package root):
  - `score_widgets()` - Main function for scoring widgets
  - `WidgetScore` - Data structure for individual widget scores
  - `ScoringResult` - Data structure containing all results
  - `ShuiWidgetScoringError` - Base exception class
  - `MalformedScoreError` - Exception for invalid Score instances
  - `InvalidValueNodeError` - Exception for invalid inputs
  - `MissingGraphError` - Exception for missing required graphs
  - `SHUI` - SHACL UI namespace constant
  - `SH` - SHACL namespace constant

## Specification

The complete algorithm specification is defined in `spec.md`, which includes:

- SHACL UI scoring rules and semantics
- Shape validation requirements
- Edge cases and error handling
- Formal algorithm steps

The implementation in `shui_widget_scoring/` follows this specification, and `tests/test_spec.py` validates compliance with the examples in the specification.

## Testing Strategy

- **Unit tests**: Each module has dedicated tests organized by functionality
  - `test_core.py`: Tests for the main `score_widgets()` algorithm (13+ tests)
  - `test_models.py`: Tests for data structures (14+ tests)
  - `test_validation.py`: Tests for SHACL validation (16+ tests)
  - `test_edge_cases.py`: Error conditions and boundary cases (13+ tests)
- **Spec compliance**: `test_spec.py` (9 tests) ensures implementation matches specification examples
- **Documentation examples**: `test_example_md.py` (3 tests) validates all examples in `example.md`
- **Total Coverage**: 90% coverage across 67 passing tests
  - `__init__.py`: 100%
  - `exceptions.py`: 100%
  - `namespaces.py`: 100%
  - `core.py`: 95%
  - `models.py`: 95%
  - `validation.py`: 83%
- **Pytest Configuration**: Automatic coverage reporting via `pytest-cov` (configured in `pyproject.toml`)

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
- Keep solutions focused and avoid over-engineering
- Only add comments where logic isn't self-evident
- Trust framework guarantees (only validate at system boundaries)

## Verifying Your Setup

To verify everything is working correctly:

```bash
# 1. Install dependencies
uv sync --extra dev

# 2. Run the examples
uv run python example.py

# 3. Run the test suite
uv run pytest

# 4. Check code quality
task code
```

If all of these succeed, your setup is ready for development.

## Build System

The project uses modern Python packaging standards:

- **Build backend**: `hatchling` (specified in `pyproject.toml`)
- **Wheel packages**: Configured with `[tool.hatch.build.targets.wheel]`
- **Package discovery**: Automatic (targets `shui_widget_scoring/` directory)

To build a distribution:

```bash
uv build
```

## Claude Code Planning Rules

When working on implementation tasks, follow these planning guidelines:

### Planning Rules

- Plans must be concise and execution-focused
- Plans describe actions, not implementations
- Do not include thinking, reasoning, explanations, or alternatives
- Do not restate the problem
- List only the tasks to perform and the order to perform them
- Use bullets only; one sentence per step
- Do not include code blocks, diffs, or before/after examples in plans

### Clarifying Questions

- If any clarifying questions are required, ask them first
- Do not produce a plan until all clarifying questions have been answered

### Implementation Phase

- Implementation is a separate step from planning
- Implementation may list files and approximate locations to change
- Do not include current code or rewritten code by default
- Describe changes in one or two sentences per file
- Only include code snippets when strictly necessary to clarify the task
- Include brief context explaining the reasoning behind each implementation step, if needed to clarify the task.
- The goal is to minimize output while keeping plans unambiguous and actionable.

## Useful Resources

- [SHACL Specification](https://www.w3.org/TR/shacl/) - W3C SHACL standard
- [SHACL UI Community Group](https://www.w3.org/community/shacl-ui/) - Community group specification
- [RDFlib Documentation](https://rdflib.readthedocs.io/) - Python RDF toolkit
- [pyshacl Documentation](https://pyshacl.readthedocs.io/) - Python SHACL validation library
- [Turtle RDF Format](https://www.w3.org/TR/turtle/) - RDF serialization format used in this project

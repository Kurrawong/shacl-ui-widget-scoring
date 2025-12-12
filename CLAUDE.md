# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package that implements the SHACL UI widget scoring algorithm, which determines the best suitable widget to use for a data graph's value node. The project is early-stage and uses `uv` for package management and dependency handling.

## Development Setup

- **Python Version**: 3.14 (specified in `.python-version`)
- **Package Manager**: `uv` (https://astral.sh/uv/) - handles both dependency management and Python version control
- **Main Dependency**: `pyshacl>=0.30.1`

## Common Commands

- **Install/Update dependencies**: `uv sync` (installs all dependencies from `pyproject.toml` and `uv.lock`)
- **Run the main application**: `uv run python main.py`
- **Run a specific Python script**: `uv run python script_name.py`
- **Add a new dependency**: `uv add package_name` (updates both `pyproject.toml` and `uv.lock`)
- **Remove a dependency**: `uv remove package_name`
- **Check for dependency updates**: `uv lock --upgrade`

## Architecture Notes

- **Entry point**: `main.py` contains the main entry point
- **Specification**: `spec.md` defines the widget scoring algorithm
- The actual implementation of the SHACL UI widget scoring algorithm should be built out in separate modules as the project develops
- The project depends on `pyshacl` for SHACL validation and processing

## Project Structure

The repository is currently minimal with:
- `main.py` - application entry point
- `pyproject.toml` - project metadata and dependencies
- `spec.md` - specification for the widget scoring algorithm
- `README.md` - project overview
- `uv.lock` - locked dependency versions (auto-managed by uv)

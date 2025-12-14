"""Core widget scoring algorithm implementation."""

import logging
from typing import Optional, Union

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF

from .models import WidgetScore, ScoringResult
from .namespaces import SH
from .validation import (
    validate_widget_scoring_graph,
    extract_score_instances,
    validate_against_shapes,
    validate_graph_against_shape,
)
from .exceptions import InvalidFocusNodeError, MissingGraphError


def score_widgets(
    focus_node: Union[URIRef, BNode, Literal],
    widget_scoring_graph: Graph,
    data_graph: Optional[Graph] = None,
    constraint_shape: Optional[Union[URIRef, BNode]] = None,
    shapes_graph: Optional[Graph] = None,
    data_graph_shapes_graph: Optional[Graph] = None,
    shapes_graph_shapes_graph: Optional[Graph] = None,
    logger: Optional[logging.Logger] = None,
) -> ScoringResult:
    """
    Score widgets based on SHACL UI Widget Scoring algorithm.

    This function implements the widget scoring algorithm as specified in the
    SHACL UI Widget Scoring specification. It validates a focus node against
    Score instances defined in the widget scoring graph and returns a sorted
    list of widget recommendations.

    Args:
        focus_node: The node in the data graph to score widgets for (URIRef, BNode, or Literal)
        widget_scoring_graph: Graph containing shui:Score instances
        data_graph: The data graph containing the focus node (optional for Literals)
        constraint_shape: The SHACL shape constraining the focus node (optional)
        shapes_graph: The shapes graph containing constraint_shape (required if constraint_shape provided)
        data_graph_shapes_graph: Graph containing shapes for dataGraphShape validation (defaults to widget_scoring_graph)
        shapes_graph_shapes_graph: Graph containing shapes for shapesGraphShape validation (defaults to widget_scoring_graph)
        logger: Optional logger for warnings and debug messages

    Returns:
        ScoringResult containing sorted list of (widget, score) pairs,
        sorted by score descending, then by widget IRI ascending

    Raises:
        MalformedScoreError: If a Score instance violates multiplicity constraints
        InvalidFocusNodeError: If focus_node is invalid or not provided
        MissingGraphError: If required graphs are missing

    Example:
        >>> from rdflib import Graph, Literal
        >>> from shui_widget_scoring import score_widgets
        >>>
        >>> # Create graphs
        >>> data_graph = Graph()
        >>> widget_scoring_graph = Graph()
        >>> # ... populate graphs ...
        >>>
        >>> # Score widgets for a boolean value
        >>> result = score_widgets(
        ...     focus_node=Literal(True),
        ...     widget_scoring_graph=widget_scoring_graph
        ... )
        >>> print(result.default_widget)  # Highest-scoring widget
    """
    # Backward compatibility: if separate shape graphs not provided,
    # use widget_scoring_graph (old behavior)
    if data_graph_shapes_graph is None:
        data_graph_shapes_graph = widget_scoring_graph
    if shapes_graph_shapes_graph is None:
        shapes_graph_shapes_graph = widget_scoring_graph

    # Step a: Validate Widget Scoring Graph
    # This ensures all Score instances are well-formed before processing
    validate_widget_scoring_graph(widget_scoring_graph, logger=logger)

    # Step b: Input Validation
    # focus_node is required
    if focus_node is None:
        raise InvalidFocusNodeError("focus_node is required")

    if not isinstance(focus_node, (URIRef, BNode, Literal)):
        raise InvalidFocusNodeError(
            f"focus_node must be URIRef, BNode, or Literal, got {type(focus_node)}"
        )

    # For URIRef/BNode focus nodes, require data_graph
    if isinstance(focus_node, (URIRef, BNode)) and data_graph is None:
        raise MissingGraphError("data_graph is required for URIRef/BNode focus nodes")

    # If constraint_shape provided, require shapes_graph
    if constraint_shape is not None and shapes_graph is None:
        raise MissingGraphError(
            "shapes_graph is required when constraint_shape is provided"
        )

    # Step c: Extract Score Instances
    score_instances = extract_score_instances(widget_scoring_graph)

    # Step d: Evaluate Each Score
    results = []

    for score_inst in score_instances:
        # Validate against dataGraphShapes
        # Use empty graph for Literals without data_graph
        dg_to_use = data_graph if data_graph is not None else Graph()
        data_valid = validate_against_shapes(
            focus_node,
            dg_to_use,
            score_inst["dataGraphShapes"],
            data_graph_shapes_graph,
            logger,
        )

        # Validate against shapesGraphShapes
        if constraint_shape is not None:
            # Validate constraint_shape as a focus node against each shapesGraphShape
            sg_to_use = shapes_graph if shapes_graph is not None else Graph()
            shapes_valid = validate_against_shapes(
                constraint_shape,
                sg_to_use,
                score_inst["shapesGraphShapes"],
                shapes_graph_shapes_graph,
                logger,
            )
        else:
            # No constraint_shape provided: validate using shape's own targets
            # Shapes without explicit targets validate trivially (no violations)
            sg_to_use = shapes_graph if shapes_graph is not None else Graph()
            shapes_valid = True
            for sg_shape in score_inst["shapesGraphShapes"]:
                if not validate_graph_against_shape(
                    sg_to_use, sg_shape, shapes_graph_shapes_graph, logger
                ):
                    shapes_valid = False
                    break

        # If all validations passed, record the result
        if data_valid and shapes_valid:
            results.append((score_inst["widget"], score_inst["score"]))

    # Step e: Create WidgetScore objects (NO deduplication)
    # All matching score instances should be returned, even if same widget
    widget_scores = [WidgetScore(widget=w, score=s) for w, s in results]
    widget_scores.sort()  # Uses WidgetScore.__lt__

    return ScoringResult(widget_scores=widget_scores)

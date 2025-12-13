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
    validate_node_against_shape,
    validate_graph_against_shape,
)
from .exceptions import InvalidValueNodeError, MissingGraphError


def score_widgets(
    value_node: Union[URIRef, BNode, Literal],
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
    SHACL UI Widget Scoring specification. It validates a value node against
    Score instances defined in the widget scoring graph and returns a sorted
    list of widget recommendations.

    Args:
        value_node: The node in the data graph to score widgets for (URIRef, BNode, or Literal)
        widget_scoring_graph: Graph containing shui:Score instances
        data_graph: The data graph containing the value node (optional for Literals)
        constraint_shape: The SHACL shape constraining the value node (optional)
        shapes_graph: The shapes graph containing constraint_shape (required if constraint_shape provided)
        data_graph_shapes_graph: Graph containing shapes for dataGraphShape validation (defaults to widget_scoring_graph)
        shapes_graph_shapes_graph: Graph containing shapes for shapesGraphShape validation (defaults to widget_scoring_graph)
        logger: Optional logger for warnings and debug messages

    Returns:
        ScoringResult containing sorted list of (widget, score) pairs,
        sorted by score descending, then by widget IRI ascending

    Raises:
        MalformedScoreError: If a Score instance violates multiplicity constraints
        InvalidValueNodeError: If value_node is invalid
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
        ...     value_node=Literal(True),
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
    if not isinstance(value_node, (URIRef, BNode, Literal)):
        raise InvalidValueNodeError(
            f"value_node must be URIRef, BNode, or Literal, got {type(value_node)}"
        )

    # For URIRef/BNode value nodes, require data_graph
    if isinstance(value_node, (URIRef, BNode)) and data_graph is None:
        raise MissingGraphError("data_graph is required for URIRef/BNode value nodes")

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
        valid = True

        # Validate against dataGraphShapes
        for dg_shape in score_inst["dataGraphShapes"]:
            # For Literal value nodes, use a simple datatype check or fallback to pyshacl
            if isinstance(value_node, Literal):
                # Check if shape is defined in the data graph shapes graph
                shape_triples = list(data_graph_shapes_graph.predicate_objects(dg_shape))
                if not shape_triples:
                    # Shape is not defined, validation fails
                    valid = False
                    if logger:
                        logger.warning(
                            f"Data graph shape {dg_shape} is not defined in data graph shapes graph"
                        )
                    break

                # For simple sh:datatype constraints, do direct comparison

                shape_datatype = data_graph_shapes_graph.value(dg_shape, SH.datatype)

                # Check if we can use the simple datatype limit optimization
                # Pass if the only constraint is sh:datatype
                is_simple_datatype_only = False
                if shape_datatype:
                    constraints = [p for p, o in shape_triples if p != RDF.type]
                    if len(constraints) == 1 and constraints[0] == SH.datatype:
                        is_simple_datatype_only = True

                if is_simple_datatype_only:
                    # Simple datatype check
                    if value_node.datatype != shape_datatype:
                        valid = False
                        break
                else:
                    # For complex shapes, use pyshacl validation with a property shape wrapper
                    temp_data_graph = Graph()
                    temp_shapes_graph = Graph()
                    temp_subject = URIRef("http://temp.example.org/subject")
                    temp_property = URIRef("http://temp.example.org/property")
                    temp_property_shape = BNode()

                    # Add the literal as the object of a property
                    temp_data_graph.add((temp_subject, temp_property, value_node))

                    # Create a property shape that copies constraints from node shape
                    temp_shapes_graph.add(
                        (temp_property_shape, RDF.type, SH.PropertyShape)
                    )
                    temp_shapes_graph.add((temp_property_shape, SH.path, temp_property))
                    temp_shapes_graph.add(
                        (temp_property_shape, SH.targetNode, temp_subject)
                    )

                    # Copy constraints from the node shape to the property shape
                    for p, o in shape_triples:
                        if p not in (RDF.type,):  # Skip rdf:type
                            temp_shapes_graph.add((temp_property_shape, p, o))

                    # Validate
                    if not validate_node_against_shape(
                        temp_subject,
                        temp_property_shape,
                        temp_data_graph,
                        temp_shapes_graph,
                        logger,
                    ):
                        valid = False
                        break
            else:
                # For URIRef/BNode, validate directly
                if not validate_node_against_shape(
                    value_node, dg_shape, data_graph, data_graph_shapes_graph, logger
                ):
                    valid = False
                    break

        # Validate against shapesGraphShapes
        if valid:
            for sg_shape in score_inst["shapesGraphShapes"]:
                # If constraint_shape is provided, use it as the focus node (target)
                # If not provided, validate using the shape's own declared targets
                if constraint_shape is not None:
                    # Validate the constraint shape as a focus node
                    if not validate_node_against_shape(
                        constraint_shape,
                        sg_shape,
                        shapes_graph,
                        shapes_graph_shapes_graph,
                        logger,
                    ):
                        valid = False
                        break
                else:
                    # No constraint_shape provided, validate using shape's own targets
                    # If shapes_graph is None, create an empty graph for validation
                    graph_to_validate = shapes_graph if shapes_graph is not None else Graph()
                    if not validate_graph_against_shape(
                        graph_to_validate,
                        sg_shape,
                        shapes_graph_shapes_graph,
                        logger,
                    ):
                        valid = False
                        break

        # If all validations passed (or no shapes to validate), record the result
        if valid:
            results.append((score_inst["widget"], score_inst["score"]))

    # Step e: Create WidgetScore objects (NO deduplication)
    # All matching score instances should be returned, even if same widget
    widget_scores = [
        WidgetScore(widget=w, score=s) for w, s in results
    ]
    widget_scores.sort()  # Uses WidgetScore.__lt__

    return ScoringResult(widget_scores=widget_scores)

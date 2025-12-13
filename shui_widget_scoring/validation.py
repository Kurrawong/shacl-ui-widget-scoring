"""SHACL validation helpers for Widget Scoring."""

import logging
import decimal
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

import pyshacl
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF

from .namespaces import SHUI, SH
from .exceptions import MalformedScoreError


# Meta-shapes for validating shui:Score instances
META_SHAPES_TTL = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix shui: <http://www.w3.org/ns/shacl-ui#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

shui:ScoreShape a sh:NodeShape ;
    sh:targetClass shui:Score ;
    sh:property [
        sh:path shui:widget ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:nodeKind sh:BlankNodeOrIRI ;
        sh:message "Score must have exactly one shui:widget" ;
    ] ;
    sh:property [
        sh:path shui:score ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:or (
            [ sh:datatype xsd:decimal ]
            [ sh:datatype xsd:integer ]
        ) ;
        sh:message "Score must have exactly one shui:score with datatype xsd:decimal or xsd:integer" ;
    ] ;
    sh:property [
        sh:path shui:dataGraphShape ;
        sh:nodeKind sh:BlankNodeOrIRI ;
        sh:message "dataGraphShape must reference a valid node" ;
    ] ;
    sh:property [
        sh:path shui:shapesGraphShape ;
        sh:nodeKind sh:BlankNodeOrIRI ;
        sh:message "shapesGraphShape must reference a valid node" ;
    ] .
"""


def _get_meta_shapes_graph() -> Graph:
    """Get the meta-shapes graph for validating Score instances."""
    g = Graph()
    g.parse(data=META_SHAPES_TTL, format="turtle")
    return g


def validate_widget_scoring_graph(
    widget_scoring_graph: Graph, logger: Optional[logging.Logger] = None
) -> None:
    """
    Validate the widget scoring graph against meta-shapes.

    This ensures all shui:Score instances are well-formed before processing.

    Args:
        widget_scoring_graph: Graph containing shui:Score instances
        logger: Optional logger for warnings

    Raises:
        MalformedScoreError: If any Score instance is malformed
    """
    meta_shapes_graph = _get_meta_shapes_graph()

    try:
        conforms, results_graph, results_text = pyshacl.validate(
            data_graph=widget_scoring_graph,
            shacl_graph=meta_shapes_graph,
            inference="none",
            abort_on_first=False,
        )

        if not conforms:
            # Extract details about which Score instances are malformed
            if logger:
                logger.error(f"Widget scoring graph validation failed:\n{results_text}")

            # Try to find the first violation to provide a helpful error message
            from rdflib.namespace import SH as SHACL_NS

            violations = list(
                results_graph.subjects(RDF.type, SHACL_NS.ValidationResult)
            )
            if violations:
                first_violation = violations[0]
                focus_node = results_graph.value(first_violation, SHACL_NS.focusNode)
                message = results_graph.value(first_violation, SHACL_NS.resultMessage)

                if focus_node and message:
                    raise MalformedScoreError(str(focus_node), str(message))

            # Fallback error message
            raise MalformedScoreError(
                "unknown",
                "Widget scoring graph contains malformed Score instances. Check logs for details.",
            )

    except MalformedScoreError:
        raise
    except Exception as e:
        if logger:
            logger.warning(f"Error during widget scoring graph validation: {e}")
        raise MalformedScoreError("unknown", f"Validation error: {e}")


def validate_node_against_shape(
    focus_node: Union[URIRef, BNode, Literal],
    shape: Union[URIRef, BNode],
    data_graph: Graph,
    shape_definitions_graph: Graph,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """
    Validate a focus node against a SHACL shape.

    Args:
        focus_node: The node to validate
        shape: The SHACL shape to validate against
        data_graph: The data graph containing the focus node
        shape_definitions_graph: The graph containing the shape definition
        logger: Optional logger for warnings

    Returns:
        True if validation passes (conforms), False if violations occur
    """
    try:
        # Create a temporary SHACL graph that specifically targets the focus node with the shape
        # This is necessary because the shapes in the scoring graph (shui:Score) do not have
        # implicit targets (sh:targetClass, etc.) that match the focus node.
        # We must explicitly link them for this validation session.
        validation_shacl_graph = Graph()
        validation_shacl_graph += shape_definitions_graph
        validation_shacl_graph.add((shape, SH.targetNode, focus_node))

        conforms, results_graph, results_text = pyshacl.validate(
            data_graph=data_graph,
            shacl_graph=validation_shacl_graph,
            advanced=True,
            inference="none",
            abort_on_first=True,
        )
        return conforms
    except Exception as e:
        # Malformed shape or validation error
        if logger:
            logger.warning(f"Shape validation failed for shape {shape}: {e}")
        return False


def validate_graph_against_shape(
    data_graph: Graph,
    shape: Union[URIRef, BNode],
    shape_definitions_graph: Graph,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """
    Validate a data graph against a SHACL shape using the shape's own targets.

    Unlike validate_node_against_shape which validates a specific focus node,
    this function relies on the shape's declared targets (sh:targetClass,
    sh:targetNode, sh:targetSubjectsOf, etc.) to determine what to validate.

    If the shape has no declared targets, validation will pass trivially
    (no violations because there's nothing to check).

    Args:
        data_graph: The data graph to validate
        shape: The SHACL shape to validate against
        shape_definitions_graph: The graph containing the shape definition
        logger: Optional logger for warnings

    Returns:
        True if validation passes (conforms), False if violations occur
    """
    try:
        conforms, results_graph, results_text = pyshacl.validate(
            data_graph=data_graph,
            shacl_graph=shape_definitions_graph,
            advanced=True,
            inference="none",
            abort_on_first=True,
        )
        return conforms
    except Exception as e:
        # Malformed shape or validation error
        if logger:
            logger.warning(f"Graph validation failed for shape {shape}: {e}")
        return False


def validate_score_instance(
    score_uri: Union[URIRef, BNode], widget_scoring_graph: Graph
) -> Dict[str, Any]:
    """
    Validate a single Score instance and extract its properties.

    Args:
        score_uri: The URI or BNode of the Score instance
        widget_scoring_graph: Graph containing the Score instance

    Returns:
        Dict with keys: 'uri', 'widget', 'score', 'dataGraphShapes', 'shapesGraphShapes'

    Raises:
        MalformedScoreError: If multiplicity constraints are violated
    """
    # Extract shui:widget (exactly one)
    widgets = list(widget_scoring_graph.objects(score_uri, SHUI.widget))
    if len(widgets) == 0:
        raise MalformedScoreError(
            str(score_uri), "Score must have exactly one shui:widget"
        )
    if len(widgets) > 1:
        raise MalformedScoreError(
            str(score_uri), "Score must have exactly one shui:widget (found multiple)"
        )

    widget = widgets[0]

    # Extract shui:score (exactly one)
    scores = list(widget_scoring_graph.objects(score_uri, SHUI.score))
    if len(scores) == 0:
        raise MalformedScoreError(
            str(score_uri), "Score must have exactly one shui:score"
        )
    if len(scores) > 1:
        raise MalformedScoreError(
            str(score_uri), "Score must have exactly one shui:score (found multiple)"
        )

    score_literal = scores[0]

    # Convert score to Decimal for precise comparison
    try:
        score_value = Decimal(str(score_literal))
    except (ValueError, TypeError, decimal.InvalidOperation) as e:
        raise MalformedScoreError(
            str(score_uri), f"shui:score must be a valid decimal or integer: {e}"
        )

    # Extract shui:dataGraphShape (zero or more)
    data_graph_shapes = list(
        widget_scoring_graph.objects(score_uri, SHUI.dataGraphShape)
    )

    # Extract shui:shapesGraphShape (zero or more)
    shapes_graph_shapes = list(
        widget_scoring_graph.objects(score_uri, SHUI.shapesGraphShape)
    )

    return {
        "uri": score_uri,
        "widget": widget,
        "score": score_value,
        "dataGraphShapes": data_graph_shapes,
        "shapesGraphShapes": shapes_graph_shapes,
    }


def extract_score_instances(widget_scoring_graph: Graph) -> List[Dict[str, Any]]:
    """
    Extract and validate all shui:Score instances from the widget scoring graph.

    Args:
        widget_scoring_graph: Graph containing shui:Score instances

    Returns:
        List of dicts with keys: 'uri', 'widget', 'score', 'dataGraphShapes', 'shapesGraphShapes'

    Raises:
        MalformedScoreError: If any Score instance violates multiplicity constraints
    """
    score_instances = []

    # Query for all instances of shui:Score
    for score_uri in widget_scoring_graph.subjects(RDF.type, SHUI.Score):
        score_data = validate_score_instance(score_uri, widget_scoring_graph)
        score_instances.append(score_data)

    return score_instances

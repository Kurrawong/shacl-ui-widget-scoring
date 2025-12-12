"""RDF namespace definitions for SHACL UI Widget Scoring."""

from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, SH, XSD

# SHACL UI namespace
SHUI = Namespace("http://www.w3.org/ns/shacl-ui#")

__all__ = ["SHUI", "RDF", "RDFS", "SH", "XSD"]

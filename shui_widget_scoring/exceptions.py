"""Custom exception classes for SHACL UI Widget Scoring."""


class ShuiWidgetScoringError(Exception):
    """Base exception for SHUI widget scoring errors."""
    pass


class MalformedScoreError(ShuiWidgetScoringError):
    """Raised when a shui:Score instance violates multiplicity constraints or is otherwise malformed."""

    def __init__(self, score_uri: str, message: str):
        self.score_uri = score_uri
        super().__init__(f"Malformed Score instance {score_uri}: {message}")


class InvalidValueNodeError(ShuiWidgetScoringError):
    """Raised when the value node is invalid or missing from data graph."""
    pass


class MissingGraphError(ShuiWidgetScoringError):
    """Raised when required graphs are not provided."""
    pass

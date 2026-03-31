class Bambu2IfcError(Exception):
    """Base error for conversion failures."""


class InputFormatError(Bambu2IfcError):
    """Raised when input file structure is not supported."""


class ParseError(Bambu2IfcError):
    """Raised when parsing a Bambu file fails."""


class ValidationError(Bambu2IfcError):
    """Raised when normalized model validation fails."""

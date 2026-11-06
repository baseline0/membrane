"""Malta domain exceptions for regulatory audit trail and debugging clarity."""


class MaltaError(Exception):
    """Base exception for all Malta errors."""

    pass


class SimulationError(MaltaError):
    """Raised when simulation execution fails."""

    pass


class EnvironmentError(MaltaError):
    """Raised when environment state is invalid."""

    pass


class RuleApplicationError(MaltaError):
    """Raised when rule application fails (catalyst missing, type mismatch, etc)."""

    pass


class MembraneError(MaltaError):
    """Raised when membrane structure is invalid."""

    pass


class ConfigurationError(MaltaError):
    """Raised when simulation configuration is incomplete or invalid."""

    pass

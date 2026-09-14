"""Malta P-System simulator — membrane computing framework.

Public API for external code (benchmarks, user scripts, research applications).
Internal modules should not be imported directly; use the services layer instead.
"""

from malta.core.simulation import Simulation
from malta.services.factory import Factory

__all__ = [
    "Simulation",
    "Factory",
]

__version__ = "0.1.0"

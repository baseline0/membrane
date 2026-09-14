"""Malta P-System simulator — membrane computing framework.

Public API for external code (benchmarks, user scripts, research applications).
Internal modules should not be imported directly; use the services layer instead.
"""

from typing import TYPE_CHECKING

from malta.core.simulation import Simulation
from malta.services.factory import Factory

if TYPE_CHECKING:
    from malta.exceptions import MaltaError

__all__ = [
    "Simulation",
    "Factory",
    "MaltaError",
]

__version__ = "0.1.0"

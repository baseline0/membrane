"""P systems, v1: symbol objects, maximal parallelism per region, target indications. See docs/psystems/SPEC-v1.md."""

from malta.psystem.engine import Result, Status, run
from malta.psystem.model import Region, Rule, System, SystemError

__all__ = ["Region", "Result", "Rule", "Status", "System", "SystemError", "run"]

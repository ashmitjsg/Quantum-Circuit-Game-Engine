"""Abstract execution backend.

Every backend is a *strategy* for turning a :class:`~qcge.ir.CircuitIR` into a
:class:`~qcge.result.SimulationResult`. The grid UI depends only on this
interface, never on a concrete simulator, so new backends can be added without
touching any game or UI code (open/closed principle).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from qcge.ir import CircuitIR
from qcge.result import SimulationResult


class QuantumBackend(ABC):
    #: short, stable identifier used by the registry (e.g. "numpy", "qiskit").
    name: str = "abstract"

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Whether this backend can run in the current environment.

        Lets the registry transparently skip backends whose optional dependencies
        (or platform support) are missing - e.g. Qiskit inside a WebAssembly build.
        """

    @abstractmethod
    def run(self, circuit: CircuitIR) -> SimulationResult:
        """Execute ``circuit`` and return its result."""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{type(self).__name__} name={self.name!r}>"

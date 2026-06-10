"""qcge - Quantum Circuit Game Engine.

A pygame-based engine for building quantum-circuit games, with a pluggable
execution backend: real Qiskit on the desktop, or a dependency-free numpy
statevector simulator that also runs in the browser (pygbag/WebAssembly).
"""

from qcge.configs import *
from qcge.ir import CircuitIR, GateOp, SUPPORTED_GATES
from qcge.result import SimulationResult
from qcge.backends import (
    QuantumBackend,
    NumpyBackend,
    QiskitBackend,
    get_backend,
    available_backends,
)
from qcge.quantum_circuit import QuantumCircuitGrid

__version__ = "2.0.0"

__all__ = [
    "QuantumCircuitGrid",
    "CircuitIR",
    "GateOp",
    "SUPPORTED_GATES",
    "SimulationResult",
    "QuantumBackend",
    "NumpyBackend",
    "QiskitBackend",
    "get_backend",
    "available_backends",
    "__version__",
]

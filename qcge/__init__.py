"""qcge - Quantum Circuit Game Engine.

A pygame-based engine for building quantum-circuit games, with a pluggable
execution backend: real Qiskit on the desktop, or a dependency-free pure-Python
statevector simulator that also runs in the browser (pygbag/WebAssembly).

Importing qcge stays numpy-free: the core (grid UI, IR, result) and the registry
have no numpy dependency, and the numpy/qiskit backends are exposed lazily via
module ``__getattr__``. This is required for the browser build - importing numpy
inside pygbag breaks the SDL display - so the default ``backend="auto"`` resolves
to the pure-Python simulator there without ever importing numpy.
"""

from importlib.metadata import version as _pkg_version, PackageNotFoundError

from qcge.configs import *
from qcge.ir import CircuitIR, GateOp, SUPPORTED_GATES
from qcge.result import SimulationResult
from qcge.backends import QuantumBackend, get_backend, available_backends
from qcge.quantum_circuit import QuantumCircuitGrid

# Single source of truth for the version is pyproject.toml; read it from the
# installed package metadata so __version__ can never drift out of sync.
try:
    __version__ = _pkg_version("qcge")
except PackageNotFoundError:  # running from a source checkout that isn't installed
    __version__ = "0.0.0+local"

__all__ = [
    "QuantumCircuitGrid",
    "CircuitIR",
    "GateOp",
    "SUPPORTED_GATES",
    "SimulationResult",
    "QuantumBackend",
    "NumpyBackend",
    "QiskitBackend",
    "PySimBackend",
    "get_backend",
    "available_backends",
    "__version__",
]

# Concrete backends are lazy so `import qcge` never imports numpy/qiskit.
_LAZY = {"NumpyBackend", "QiskitBackend", "PySimBackend"}


def __getattr__(name):  # PEP 562
    if name in _LAZY:
        from qcge import backends
        return getattr(backends, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

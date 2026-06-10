"""Pluggable quantum execution backends for qcge.

Only the dependency-free pieces (the abstract base and the registry) are imported
eagerly. Concrete backends are exposed lazily via module ``__getattr__`` so that
``import qcge`` - and the browser build's auto path - never imports numpy or qiskit
unless those backends are actually requested. (Importing numpy inside pygbag breaks
the SDL display, so this laziness is load-bearing, not just tidy.)
"""

from qcge.backends.base import QuantumBackend
from qcge.backends.registry import available_backends, get_backend

__all__ = [
    "QuantumBackend",
    "NumpyBackend",
    "QiskitBackend",
    "PySimBackend",
    "get_backend",
    "available_backends",
]

_LAZY = {
    "NumpyBackend": ("qcge.backends.numpy_backend", "NumpyBackend"),
    "QiskitBackend": ("qcge.backends.qiskit_backend", "QiskitBackend"),
    "PySimBackend": ("qcge.backends.python_backend", "PySimBackend"),
}


def __getattr__(name):  # PEP 562
    if name in _LAZY:
        import importlib
        module_path, class_name = _LAZY[name]
        return getattr(importlib.import_module(module_path), class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

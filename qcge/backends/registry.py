"""Backend factory and selection.

Resolves a backend by name, or - with ``"auto"`` - picks the best one available
in the current environment: real Qiskit when installed, otherwise the always-present
numpy simulator. This is what lets the *same* game run with accurate Qiskit on a
desktop and fall back to the dependency-free simulator in a browser build, with no
code change at the call site.
"""

from __future__ import annotations

from qcge.backends.base import QuantumBackend
from qcge.backends.numpy_backend import NumpyBackend
from qcge.backends.qiskit_backend import QiskitBackend

# Registry of known backend classes, in auto-selection preference order.
_BACKENDS: dict[str, type[QuantumBackend]] = {
    QiskitBackend.name: QiskitBackend,
    NumpyBackend.name: NumpyBackend,
}
_AUTO_ORDER = (QiskitBackend, NumpyBackend)

# Aliases for friendlier call sites.
_ALIASES = {"sim": "numpy", "statevector": "numpy", "real": "qiskit"}

_instances: dict[str, QuantumBackend] = {}


def available_backends() -> list[str]:
    """Names of backends usable in this environment."""
    return [name for name, cls in _BACKENDS.items() if cls.is_available()]


def get_backend(name: str = "auto") -> QuantumBackend:
    """Return a (cached) backend instance.

    Args:
        name: ``"auto"`` (default), a backend name (``"numpy"``/``"qiskit"``), or an
            alias (``"sim"``/``"real"``).

    Raises:
        ValueError: unknown name.
        RuntimeError: the requested backend is unavailable (e.g. ``"qiskit"`` when
            Qiskit is not installed), or no backend is available at all.
    """
    name = _ALIASES.get(name, name)

    if name == "auto":
        for cls in _AUTO_ORDER:
            if cls.is_available():
                return _instances.setdefault(cls.name, cls())
        raise RuntimeError("No quantum backend is available")  # pragma: no cover

    if name not in _BACKENDS:
        raise ValueError(f"Unknown backend {name!r}; choose from {sorted(_BACKENDS)} or 'auto'")

    cls = _BACKENDS[name]
    if not cls.is_available():
        hint = " (install with: pip install qcge[qiskit])" if name == "qiskit" else ""
        raise RuntimeError(f"Backend {name!r} is not available in this environment{hint}")
    return _instances.setdefault(name, cls())

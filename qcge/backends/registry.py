"""Backend factory and selection.

Resolves a backend by name, or - with ``"auto"`` - picks the best one available
in the current environment: real Qiskit when installed, otherwise the always-present
pure-Python statevector simulator. This is what lets the *same* game run with
accurate Qiskit on a desktop and fall back to the dependency-free simulator in a
browser build, with no code change at the call site.

Backend classes are imported lazily, and availability is probed with
``importlib.util.find_spec`` (which does not import the module). This matters for
the browser build: importing numpy inside pygbag breaks the SDL display, so the
auto path must be able to choose a backend *without* importing numpy. ``"auto"``
therefore never selects the numpy backend - the pure-Python backend gives identical
results with no dependency - though ``"numpy"`` remains available by explicit name
on the desktop.
"""

from __future__ import annotations

import importlib
import importlib.util

from qcge.backends.base import QuantumBackend

# name -> (module path, class name). Imported only when actually used.
_SPECS: dict[str, tuple[str, str]] = {
    "qiskit": ("qcge.backends.qiskit_backend", "QiskitBackend"),
    "python": ("qcge.backends.python_backend", "PySimBackend"),
    "numpy": ("qcge.backends.numpy_backend", "NumpyBackend"),
}

# Auto-selection preference order. Numpy is intentionally excluded (see module
# docstring): the pure-Python backend is the universal, numpy-free fallback.
_AUTO_ORDER = ("qiskit", "python")

# Aliases for friendlier call sites.
_ALIASES = {"sim": "python", "statevector": "python", "real": "qiskit"}

_instances: dict[str, QuantumBackend] = {}


def _is_available(name: str) -> bool:
    """Whether a backend can run here, without importing heavy modules."""
    if name == "python":
        return True  # pure standard library
    if name == "qiskit":
        return importlib.util.find_spec("qiskit") is not None
    if name == "numpy":
        return importlib.util.find_spec("numpy") is not None
    return False


def _load_class(name: str) -> type[QuantumBackend]:
    module_path, class_name = _SPECS[name]
    return getattr(importlib.import_module(module_path), class_name)


def available_backends() -> list[str]:
    """Names of backends usable in this environment."""
    return [name for name in _SPECS if _is_available(name)]


def get_backend(name: str = "auto") -> QuantumBackend:
    """Return a (cached) backend instance.

    Args:
        name: ``"auto"`` (default), a backend name (``"python"``/``"qiskit"``/
            ``"numpy"``), or an alias (``"sim"``/``"real"``).

    Raises:
        ValueError: unknown name.
        RuntimeError: the requested backend is unavailable (e.g. ``"qiskit"`` when
            Qiskit is not installed), or no backend is available at all.
    """
    name = _ALIASES.get(name, name)

    if name == "auto":
        for candidate in _AUTO_ORDER:
            if _is_available(candidate):
                return _instances.setdefault(candidate, _load_class(candidate)())
        raise RuntimeError("No quantum backend is available")  # pragma: no cover

    if name not in _SPECS:
        raise ValueError(f"Unknown backend {name!r}; choose from {sorted(_SPECS)} or 'auto'")

    if not _is_available(name):
        hint = " (install with: pip install qcge[qiskit])" if name == "qiskit" else ""
        raise RuntimeError(f"Backend {name!r} is not available in this environment{hint}")
    return _instances.setdefault(name, _load_class(name)())

"""Backend-agnostic quantum-circuit intermediate representation (IR).

The pygame circuit-grid UI knows nothing about how a circuit is executed; it only
knows how to emit this IR. Execution backends (numpy, qiskit, ...) consume the
same IR. This is the seam that lets qcge run identically on a desktop with real
Qiskit and inside a browser (pygbag/WebAssembly) with the dependency-free numpy
simulator.

The IR is deliberately tiny and validated at construction so that a malformed
grid fails fast with a clear error instead of deep inside a backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Single-qubit, non-parameterised gates every backend must support.
_SIMPLE_GATES = frozenset({"i", "x", "y", "z", "h", "s", "sdg", "t", "tdg"})
# Single-qubit, parameterised (one real angle) gates.
_ROTATION_GATES = frozenset({"rx", "ry", "rz"})
# Multi-qubit gates with their required target arity.
_SWAP_GATES = frozenset({"swap"})

SUPPORTED_GATES = _SIMPLE_GATES | _ROTATION_GATES | _SWAP_GATES


@dataclass(frozen=True)
class GateOp:
    """A single gate application in the circuit.

    Args:
        name: canonical lowercase gate name (see ``SUPPORTED_GATES``).
        targets: qubit indices the gate body acts on. Length 1 for the simple and
            rotation gates, length 2 for ``swap``.
        controls: control qubit indices (empty for uncontrolled gates). Any gate
            may be controlled; e.g. ``x`` with one control is a CNOT, with two a
            Toffoli, and ``swap`` with one control is a Fredkin.
        param: rotation angle in radians (only meaningful for rotation gates).
    """

    name: str
    targets: tuple[int, ...]
    controls: tuple[int, ...] = ()
    param: float = 0.0

    def __post_init__(self) -> None:
        if self.name not in SUPPORTED_GATES:
            raise ValueError(f"Unsupported gate {self.name!r}; expected one of {sorted(SUPPORTED_GATES)}")

        arity = 2 if self.name in _SWAP_GATES else 1
        if len(self.targets) != arity:
            raise ValueError(f"Gate {self.name!r} needs {arity} target(s), got {self.targets}")

        qubits = list(self.targets) + list(self.controls)
        if len(set(qubits)) != len(qubits):
            raise ValueError(f"Gate {self.name!r} has overlapping qubits: targets={self.targets} controls={self.controls}")

        if (self.param != 0.0) and (self.name not in _ROTATION_GATES):
            raise ValueError(f"Gate {self.name!r} does not take a rotation angle")

    @property
    def is_controlled(self) -> bool:
        return len(self.controls) > 0


@dataclass
class CircuitIR:
    """An ordered list of gate operations on a fixed-width qubit register."""

    num_qubits: int
    ops: list[GateOp] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.num_qubits <= 0:
            raise ValueError(f"num_qubits must be positive, got {self.num_qubits}")
        for op in self.ops:
            self._check_indices(op)

    def add(self, name: str, targets, controls=(), param: float = 0.0) -> "CircuitIR":
        """Append a gate; returns self for chaining."""
        op = GateOp(name, tuple(targets), tuple(controls), param)
        self._check_indices(op)
        self.ops.append(op)
        return self

    def _check_indices(self, op: GateOp) -> None:
        for q in (*op.targets, *op.controls):
            if not 0 <= q < self.num_qubits:
                raise ValueError(f"Qubit index {q} out of range for {self.num_qubits}-qubit circuit")

    @property
    def dim(self) -> int:
        """Hilbert-space dimension (2**num_qubits)."""
        return 1 << self.num_qubits

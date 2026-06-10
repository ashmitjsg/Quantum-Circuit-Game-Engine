"""Pure-Python statevector backend (zero third-party dependencies).

This is the backend used in the browser (pygbag/WebAssembly) build. It is a
deliberate, dependency-free twin of :class:`NumpyBackend`: importing numpy inside
a pygbag bundle breaks the SDL display (the numpy wheel poisons canvas/display
init), so the web path must never touch numpy. For the small registers
interactive games use (a handful of qubits => a few dozen amplitudes) a plain
Python statevector loop is more than fast enough.

Amplitudes are Python ``complex`` in a flat list. Convention matches Qiskit:
qubit 0 is the least-significant bit (little-endian), so results are interchangeable
with the numpy and qiskit backends.
"""

from __future__ import annotations

import cmath
import math

from qcge.backends.base import QuantumBackend
from qcge.ir import CircuitIR, GateOp
from qcge.result import SimulationResult

_SQRT1_2 = 1.0 / math.sqrt(2.0)

# 2x2 single-qubit gate matrices as ((a, b), (c, d)) tuples of complex numbers.
_STATIC_GATES = {
    "i": ((1 + 0j, 0j), (0j, 1 + 0j)),
    "x": ((0j, 1 + 0j), (1 + 0j, 0j)),
    "y": ((0j, -1j), (1j, 0j)),
    "z": ((1 + 0j, 0j), (0j, -1 + 0j)),
    "h": ((_SQRT1_2 + 0j, _SQRT1_2 + 0j), (_SQRT1_2 + 0j, -_SQRT1_2 + 0j)),
    "s": ((1 + 0j, 0j), (0j, 1j)),
    "sdg": ((1 + 0j, 0j), (0j, -1j)),
    "t": ((1 + 0j, 0j), (0j, complex(_SQRT1_2, _SQRT1_2))),
    "tdg": ((1 + 0j, 0j), (0j, complex(_SQRT1_2, -_SQRT1_2))),
}


def _rotation_matrix(name: str, theta: float):
    half = theta / 2.0
    cos, sin = math.cos(half), math.sin(half)
    if name == "rx":
        return ((cos + 0j, -1j * sin), (-1j * sin, cos + 0j))
    if name == "ry":
        return ((cos + 0j, -sin + 0j), (sin + 0j, cos + 0j))
    if name == "rz":
        return ((cmath.exp(-1j * half), 0j), (0j, cmath.exp(1j * half)))
    raise ValueError(f"Unknown rotation gate {name!r}")  # pragma: no cover


class PySimBackend(QuantumBackend):
    name = "python"

    @classmethod
    def is_available(cls) -> bool:
        return True  # pure standard library; always usable

    def run(self, circuit: CircuitIR) -> SimulationResult:
        n = circuit.num_qubits
        state = [0j] * circuit.dim
        state[0] = 1 + 0j  # |0...0>

        for op in circuit.ops:
            if op.name == "swap":
                state = self._apply_swap(state, op)
            else:
                matrix = _STATIC_GATES[op.name] if op.name in _STATIC_GATES else _rotation_matrix(op.name, op.param)
                state = self._apply_1q(state, matrix, op.targets[0], op.controls)

        return SimulationResult(statevector=state, num_qubits=n)

    @staticmethod
    def _controls_satisfied(index: int, controls: tuple[int, ...]) -> bool:
        return all((index >> c) & 1 for c in controls)

    def _apply_1q(self, state, matrix, target, controls):
        out = list(state)
        (m00, m01), (m10, m11) = matrix
        for index in range(len(state)):
            # iterate only the half where the target bit is 0; pair it with bit=1
            if (index >> target) & 1:
                continue
            if not self._controls_satisfied(index, controls):
                continue
            i0 = index
            i1 = index | (1 << target)
            a0, a1 = state[i0], state[i1]
            out[i0] = m00 * a0 + m01 * a1
            out[i1] = m10 * a0 + m11 * a1
        return out

    def _apply_swap(self, state, op: GateOp):
        a, b = op.targets
        out = list(state)
        for index in range(len(state)):
            bit_a = (index >> a) & 1
            bit_b = (index >> b) & 1
            if bit_a == bit_b:
                continue
            if not self._controls_satisfied(index, op.controls):
                continue
            swapped = index ^ (1 << a) ^ (1 << b)
            out[swapped] = state[index]
        return out

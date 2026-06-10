"""Pure-Python/numpy statevector backend.

Has no third-party dependency beyond numpy, so it runs everywhere qcge does -
crucially inside a pygbag/WebAssembly (Pyodide) build, where Qiskit's compiled
extensions are unavailable. Adequate for the small circuits (a handful of qubits)
that interactive games build.

Convention matches Qiskit: qubit 0 is the least-significant bit (little-endian),
so results are interchangeable with the Qiskit backend.
"""

from __future__ import annotations

import cmath
import math

import numpy as np

from qcge.backends.base import QuantumBackend
from qcge.ir import CircuitIR, GateOp
from qcge.result import SimulationResult

_SQRT1_2 = 1.0 / math.sqrt(2.0)


def _static_gates() -> dict[str, np.ndarray]:
    c = complex
    return {
        "i": np.array([[1, 0], [0, 1]], dtype=complex),
        "x": np.array([[0, 1], [1, 0]], dtype=complex),
        "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "z": np.array([[1, 0], [0, -1]], dtype=complex),
        "h": np.array([[_SQRT1_2, _SQRT1_2], [_SQRT1_2, -_SQRT1_2]], dtype=complex),
        "s": np.array([[1, 0], [0, 1j]], dtype=complex),
        "sdg": np.array([[1, 0], [0, -1j]], dtype=complex),
        "t": np.array([[1, 0], [0, c(_SQRT1_2, _SQRT1_2)]], dtype=complex),
        "tdg": np.array([[1, 0], [0, c(_SQRT1_2, -_SQRT1_2)]], dtype=complex),
    }


def _rotation_matrix(name: str, theta: float) -> np.ndarray:
    half = theta / 2.0
    cos, sin = math.cos(half), math.sin(half)
    if name == "rx":
        return np.array([[cos, -1j * sin], [-1j * sin, cos]], dtype=complex)
    if name == "ry":
        return np.array([[cos, -sin], [sin, cos]], dtype=complex)
    if name == "rz":
        return np.array([[cmath.exp(-1j * half), 0], [0, cmath.exp(1j * half)]], dtype=complex)
    raise ValueError(f"Unknown rotation gate {name!r}")  # pragma: no cover


class NumpyBackend(QuantumBackend):
    name = "numpy"

    @classmethod
    def is_available(cls) -> bool:
        return True  # numpy is a hard dependency of qcge

    def run(self, circuit: CircuitIR) -> SimulationResult:
        n = circuit.num_qubits
        state = np.zeros(circuit.dim, dtype=complex)
        state[0] = 1.0  # |0...0>

        static = _static_gates()
        for op in circuit.ops:
            if op.name == "swap":
                state = self._apply_swap(state, n, op)
            else:
                matrix = static[op.name] if op.name in static else _rotation_matrix(op.name, op.param)
                state = self._apply_1q(state, n, matrix, op.targets[0], op.controls)

        return SimulationResult(statevector=state, num_qubits=n)

    @staticmethod
    def _controls_satisfied(index: int, controls: tuple[int, ...]) -> bool:
        return all((index >> c) & 1 for c in controls)

    def _apply_1q(self, state, n, matrix, target, controls):
        out = state.copy()
        for index in range(len(state)):
            # only iterate the half where the target bit is 0; pair it with bit=1
            if (index >> target) & 1:
                continue
            if not self._controls_satisfied(index, controls):
                continue
            i0 = index
            i1 = index | (1 << target)
            a0, a1 = state[i0], state[i1]
            out[i0] = matrix[0, 0] * a0 + matrix[0, 1] * a1
            out[i1] = matrix[1, 0] * a0 + matrix[1, 1] * a1
        return out

    def _apply_swap(self, state, n, op: GateOp):
        a, b = op.targets
        out = state.copy()
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

"""Cross-check the numpy backend against real Qiskit on shared circuits.

Skipped automatically when Qiskit is not installed, so the suite still passes in a
minimal (browser-like) environment.
"""

import math

import numpy as np
import pytest

from qcge.ir import CircuitIR
from qcge.backends.numpy_backend import NumpyBackend
from qcge.backends.qiskit_backend import QiskitBackend

pytestmark = pytest.mark.skipif(not QiskitBackend.is_available(), reason="qiskit not installed")


def _circuits():
    return [
        CircuitIR(1).add("h", (0,)).add("t", (0,)),
        CircuitIR(2).add("h", (0,)).add("x", (1,), controls=(0,)),       # Bell
        CircuitIR(2).add("x", (0,)).add("swap", (0, 1)),
        CircuitIR(3).add("h", (0,)).add("x", (1,), controls=(0,)).add("x", (2,), controls=(1,)),  # GHZ
        CircuitIR(3).add("x", (0,)).add("x", (1,)).add("x", (2,), controls=(0, 1)),  # Toffoli
        CircuitIR(2).add("ry", (0,), param=0.9).add("rz", (1,), param=1.3).add("z", (1,), controls=(0,)),
        CircuitIR(1).add("s", (0,)).add("sdg", (0,)).add("tdg", (0,)),
    ]


@pytest.mark.parametrize("ir", _circuits())
def test_numpy_matches_qiskit_statevector(ir):
    a = NumpyBackend().run(ir).statevector
    b = QiskitBackend().run(ir).statevector
    # equal up to a global phase
    overlap = np.vdot(a, b)
    assert math.isclose(abs(overlap), 1.0, abs_tol=1e-9)

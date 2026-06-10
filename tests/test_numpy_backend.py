"""Correctness tests for the dependency-free numpy statevector backend."""

import math

import numpy as np
import pytest

from qcge.ir import CircuitIR
from qcge.backends.numpy_backend import NumpyBackend

SQRT1_2 = 1 / math.sqrt(2)
be = NumpyBackend()


def sv(ir):
    return be.run(ir).statevector


def test_ground_state():
    res = sv(CircuitIR(1))
    assert np.allclose(res, [1, 0])


def test_x_flips():
    assert np.allclose(sv(CircuitIR(1).add("x", (0,))), [0, 1])


def test_h_superposition():
    assert np.allclose(sv(CircuitIR(1).add("h", (0,))), [SQRT1_2, SQRT1_2])


def test_hz_h_equals_x_phase():
    # H Z H = X, so H,Z,H on |0> -> |1>
    ir = CircuitIR(1).add("h", (0,)).add("z", (0,)).add("h", (0,))
    assert np.allclose(sv(ir), [0, 1])


def test_little_endian_ordering():
    # X on qubit 0 only -> |...01> = index 1 (qubit0 is LSB, like Qiskit)
    res = sv(CircuitIR(2).add("x", (0,)))
    assert np.argmax(np.abs(res) ** 2) == 1


def test_bell_state_entanglement():
    ir = CircuitIR(2).add("h", (0,)).add("x", (1,), controls=(0,))
    res = sv(ir)
    probs = np.abs(res) ** 2
    assert math.isclose(probs[0], 0.5, abs_tol=1e-9)   # |00>
    assert math.isclose(probs[3], 0.5, abs_tol=1e-9)   # |11>
    assert math.isclose(probs[1], 0.0, abs_tol=1e-9)
    assert math.isclose(probs[2], 0.0, abs_tol=1e-9)


def test_toffoli():
    # set both controls then CCX flips target
    ir = CircuitIR(3).add("x", (0,)).add("x", (1,)).add("x", (2,), controls=(0, 1))
    res = sv(ir)
    assert np.argmax(np.abs(res) ** 2) == 0b111


def test_swap():
    ir = CircuitIR(2).add("x", (0,)).add("swap", (0, 1))
    res = sv(ir)
    assert np.argmax(np.abs(res) ** 2) == 0b10   # excitation moved to qubit 1


def test_rx_pi_is_x_up_to_phase():
    res = sv(CircuitIR(1).add("rx", (0,), param=math.pi))
    assert math.isclose((np.abs(res) ** 2)[1], 1.0, abs_tol=1e-9)


def test_states_stay_normalised():
    ir = CircuitIR(3).add("h", (0,)).add("t", (0,)).add("x", (1,), controls=(0,)).add("ry", (2,), param=0.7)
    res = sv(ir)
    assert math.isclose(np.sum(np.abs(res) ** 2), 1.0, abs_tol=1e-9)

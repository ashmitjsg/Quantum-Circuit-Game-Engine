"""Backend registry selection and SimulationResult behaviour."""

import math

import numpy as np
import pytest

from qcge.backends import get_backend, available_backends
from qcge.backends.numpy_backend import NumpyBackend
from qcge.backends.python_backend import PySimBackend
from qcge.backends.qiskit_backend import QiskitBackend
from qcge.ir import CircuitIR
from qcge.result import SimulationResult


def test_numpy_always_available():
    assert "numpy" in available_backends()
    assert isinstance(get_backend("numpy"), NumpyBackend)


def test_python_always_available():
    # The pure-Python backend has no third-party deps, so it is always usable -
    # this is what the browser build relies on.
    assert "python" in available_backends()
    assert isinstance(get_backend("python"), PySimBackend)


def test_aliases():
    # "sim" now resolves to the dependency-free pure-Python backend (browser-safe).
    assert isinstance(get_backend("sim"), PySimBackend)


def test_auto_prefers_qiskit_else_python():
    # auto never falls back to numpy (importing numpy breaks pygbag); the
    # dependency-free pure-Python backend is the fallback.
    auto = get_backend("auto")
    expected = "qiskit" if QiskitBackend.is_available() else "python"
    assert auto.name == expected


def test_unknown_backend_raises():
    with pytest.raises(ValueError):
        get_backend("does-not-exist")


def test_requesting_unavailable_qiskit_raises():
    if QiskitBackend.is_available():
        pytest.skip("qiskit is installed")
    with pytest.raises(RuntimeError):
        get_backend("qiskit")


def test_backend_instances_cached():
    assert get_backend("numpy") is get_backend("numpy")


def test_result_sampling_is_deterministic_with_seed():
    ir = CircuitIR(2).add("h", (0,)).add("x", (1,), controls=(0,))
    res = NumpyBackend().run(ir)
    counts = res.sample_counts(2000, rng=np.random.default_rng(0))
    assert set(counts) <= {"00", "11"}          # Bell: only correlated outcomes
    assert sum(counts.values()) == 2000


def test_result_most_likely():
    res = SimulationResult(statevector=np.array([0, 0, 0, 1], dtype=complex), num_qubits=2)
    assert res.most_likely() == "11"


def test_probabilities_sum_to_one():
    ir = CircuitIR(3).add("h", (0,)).add("h", (1,)).add("h", (2,))
    res = NumpyBackend().run(ir)
    assert math.isclose(float(np.sum(res.probabilities())), 1.0, abs_tol=1e-9)


@pytest.mark.parametrize("ir", [
    CircuitIR(1).add("h", (0,)).add("t", (0,)),
    CircuitIR(2).add("h", (0,)).add("x", (1,), controls=(0,)),                              # Bell
    CircuitIR(3).add("h", (0,)).add("x", (1,), controls=(0,)).add("x", (2,), controls=(1,)),  # GHZ
    CircuitIR(2).add("ry", (0,), param=0.9).add("z", (1,), controls=(0,)),
    CircuitIR(2).add("x", (0,)).add("swap", (0, 1)),
])
def test_python_matches_numpy(ir):
    # The pure-Python (browser) backend must agree with numpy exactly.
    a = PySimBackend().run(ir).statevector
    b = NumpyBackend().run(ir).statevector
    assert max(abs(complex(x) - complex(y)) for x, y in zip(a, b)) < 1e-12


def test_result_is_numpy_free_with_plain_list():
    # SimulationResult must work on a plain Python list - the browser path never
    # produces numpy arrays.
    res = SimulationResult(statevector=[0j, 0j, 0j, 1 + 0j], num_qubits=2)
    assert res.most_likely() == "11"
    assert res.probabilities() == [0.0, 0.0, 0.0, 1.0]
    assert res.sample_counts(100) == {"11": 100}

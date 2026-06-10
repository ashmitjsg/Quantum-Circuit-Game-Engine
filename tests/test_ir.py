"""Tests for the circuit IR and its validation."""

import math

import pytest

from qcge.ir import CircuitIR, GateOp, SUPPORTED_GATES


def test_gateop_rejects_unknown_gate():
    with pytest.raises(ValueError):
        GateOp("foo", (0,))


def test_gateop_arity_enforced():
    with pytest.raises(ValueError):
        GateOp("swap", (0,))          # swap needs 2 targets
    with pytest.raises(ValueError):
        GateOp("x", (0, 1))           # x needs exactly 1


def test_gateop_rejects_overlapping_qubits():
    with pytest.raises(ValueError):
        GateOp("x", (0,), controls=(0,))


def test_gateop_rejects_param_on_non_rotation():
    with pytest.raises(ValueError):
        GateOp("x", (0,), param=0.5)
    GateOp("rx", (0,), param=0.5)     # allowed


def test_circuit_rejects_out_of_range_index():
    ir = CircuitIR(2)
    with pytest.raises(ValueError):
        ir.add("x", (5,))


def test_circuit_add_is_chainable_and_dim():
    ir = CircuitIR(3).add("h", (0,)).add("x", (1,), controls=(0,))
    assert len(ir.ops) == 2
    assert ir.dim == 8


def test_supported_gates_present():
    for g in ("h", "x", "y", "z", "s", "sdg", "t", "tdg", "rx", "ry", "rz", "swap", "i"):
        assert g in SUPPORTED_GATES

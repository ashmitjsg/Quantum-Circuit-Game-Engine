"""Qiskit execution backend (optional).

Adapts the qcge IR to a ``qiskit.QuantumCircuit`` and evaluates it with
``qiskit.quantum_info.Statevector`` - part of Qiskit core, so it needs neither
``qiskit-aer`` nor the long-removed ``BasicAer``. Targets Qiskit >= 2.0 (the
current series; 1.x is end-of-life), using only APIs stable across 1.x/2.x.

Qiskit is an *optional* dependency (``pip install qcge[qiskit]``); it is imported
lazily so that merely importing qcge - or running the numpy backend in a browser
build - never requires it.
"""

from __future__ import annotations

import importlib.util

from qcge.backends.base import QuantumBackend
from qcge.ir import CircuitIR
from qcge.result import SimulationResult


class QiskitBackend(QuantumBackend):
    name = "qiskit"

    @classmethod
    def is_available(cls) -> bool:
        return importlib.util.find_spec("qiskit") is not None

    def to_qiskit(self, circuit: CircuitIR):
        """Translate the IR into a ``qiskit.QuantumCircuit``."""
        from qiskit import QuantumCircuit  # lazy

        qc = QuantumCircuit(circuit.num_qubits)
        for op in circuit.ops:
            self._append(qc, op)
        return qc

    @staticmethod
    def _append(qc, op) -> None:
        t = op.targets
        ctrls = op.controls
        name = op.name

        # uncontrolled forms
        if not ctrls:
            simple = {
                "i": qc.id, "x": qc.x, "y": qc.y, "z": qc.z, "h": qc.h,
                "s": qc.s, "sdg": qc.sdg, "t": qc.t, "tdg": qc.tdg,
            }
            if name in simple:
                simple[name](t[0])
            elif name in ("rx", "ry", "rz"):
                getattr(qc, name)(op.param, t[0])
            elif name == "swap":
                qc.swap(t[0], t[1])
            return

        # controlled forms (qcge only needs the common ones)
        if name == "x" and len(ctrls) == 1:
            qc.cx(ctrls[0], t[0])
        elif name == "x" and len(ctrls) == 2:
            qc.ccx(ctrls[0], ctrls[1], t[0])
        elif name == "y" and len(ctrls) == 1:
            qc.cy(ctrls[0], t[0])
        elif name == "z" and len(ctrls) == 1:
            qc.cz(ctrls[0], t[0])
        elif name == "h" and len(ctrls) == 1:
            qc.ch(ctrls[0], t[0])
        elif name == "swap" and len(ctrls) == 1:
            qc.cswap(ctrls[0], t[0], t[1])
        elif name in ("rx", "ry", "rz") and len(ctrls) == 1:
            getattr(qc, f"c{name}")(op.param, ctrls[0], t[0])
        else:
            raise ValueError(f"Qiskit backend cannot express {name!r} with controls {ctrls}")

    def run(self, circuit: CircuitIR) -> SimulationResult:
        from qiskit.quantum_info import Statevector  # lazy

        qc = self.to_qiskit(circuit)
        sv = Statevector.from_instruction(qc)
        return SimulationResult(statevector=sv.data, num_qubits=circuit.num_qubits)

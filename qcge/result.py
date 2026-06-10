"""Uniform simulation result, independent of which backend produced it."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SimulationResult:
    """The outcome of running a circuit.

    Args:
        statevector: complex amplitudes of length ``2**num_qubits`` ordered in the
            little-endian convention (qubit 0 is the least-significant bit), matching
            Qiskit. ``None`` if the backend produced only sampled counts.
        num_qubits: width of the register, needed to format bitstrings.
    """

    statevector: np.ndarray | None
    num_qubits: int

    def probabilities(self) -> np.ndarray:
        """Measurement probability of each computational basis state."""
        if self.statevector is None:
            raise ValueError("This result has no statevector to derive probabilities from")
        return np.abs(self.statevector) ** 2

    def sample_counts(self, shots: int, rng: np.random.Generator | None = None) -> dict[str, int]:
        """Sample measurement bitstrings, returning ``{bitstring: count}``.

        Bitstrings are big-endian (qubit ``n-1`` first) to match Qiskit's
        ``get_counts`` formatting, so downstream game code is backend-agnostic.
        """
        if shots <= 0:
            raise ValueError(f"shots must be positive, got {shots}")
        rng = rng or np.random.default_rng()
        probs = self.probabilities()
        draws = rng.choice(len(probs), size=shots, p=probs)
        counts: dict[str, int] = {}
        for state in draws:
            key = format(int(state), f"0{self.num_qubits}b")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def most_likely(self) -> str:
        """Big-endian bitstring of the highest-probability basis state."""
        probs = self.probabilities()
        return format(int(np.argmax(probs)), f"0{self.num_qubits}b")

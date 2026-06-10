"""Uniform simulation result, independent of which backend produced it.

Deliberately numpy-free: the statevector is a plain sequence of Python ``complex``
amplitudes. This keeps the result type (and everything that imports it, including
the always-loaded grid UI) usable inside a pygbag/WebAssembly build, where loading
numpy breaks the SDL display. The numpy and qiskit backends hand their amplitudes
over as a list.
"""

from __future__ import annotations

import random as _random
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class SimulationResult:
    """The outcome of running a circuit.

    Args:
        statevector: complex amplitudes of length ``2**num_qubits`` ordered in the
            little-endian convention (qubit 0 is the least-significant bit), matching
            Qiskit. ``None`` if the backend produced only sampled counts. May be any
            sequence of complex numbers (list, numpy array); methods treat it as a
            plain sequence so no numpy is required.
        num_qubits: width of the register, needed to format bitstrings.
    """

    statevector: Optional[Sequence[complex]]
    num_qubits: int

    def probabilities(self) -> list[float]:
        """Measurement probability of each computational basis state."""
        if self.statevector is None:
            raise ValueError("This result has no statevector to derive probabilities from")
        return [abs(a) ** 2 for a in self.statevector]

    def sample_counts(self, shots: int, rng: Optional[_random.Random] = None) -> dict[str, int]:
        """Sample measurement bitstrings, returning ``{bitstring: count}``.

        Bitstrings are big-endian (qubit ``n-1`` first) to match Qiskit's
        ``get_counts`` formatting, so downstream game code is backend-agnostic.
        """
        if shots <= 0:
            raise ValueError(f"shots must be positive, got {shots}")
        rng = rng or _random.Random()
        probs = self.probabilities()

        # Build a cumulative distribution once, then draw one random() per shot
        # (inverse-transform sampling) - no numpy needed.
        cumulative: list[float] = []
        running = 0.0
        for p in probs:
            running += p
            cumulative.append(running)
        total = cumulative[-1] if cumulative else 1.0

        counts: dict[str, int] = {}
        for _ in range(shots):
            target = rng.random() * total
            index = len(cumulative) - 1
            for i, edge in enumerate(cumulative):
                if target <= edge:
                    index = i
                    break
            key = format(index, f"0{self.num_qubits}b")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def most_likely(self) -> str:
        """Big-endian bitstring of the highest-probability basis state."""
        probs = self.probabilities()
        best = max(range(len(probs)), key=probs.__getitem__)
        return format(best, f"0{self.num_qubits}b")

"""Measurement sampling and state collapse."""
import numpy as np

def probabilities(state):
    p = np.abs(np.asarray(state, dtype=complex)) ** 2
    total = float(p.sum())
    if total <= 0:
        raise ValueError("State has zero norm")
    return p / total

def sample_measurements(state, shots=1000, rng=None):
    if int(shots) < 1 or int(shots) > 1000000:
        raise ValueError("shots must be between 1 and 1,000,000")
    rng = rng or np.random.default_rng()
    p = probabilities(state)
    outcomes = rng.choice(len(p), size=int(shots), p=p)
    counts = np.bincount(outcomes, minlength=len(p))
    return {format(i, f"0{int(np.log2(len(p)))}b"): int(c)
            for i, c in enumerate(counts) if c}

def measure_qubit(state, n_qubits, qubit, rng=None):
    """Projectively measure one qubit; returns (new_state, outcome)."""
    rng = rng or np.random.default_rng()
    state = np.asarray(state, dtype=complex).copy()
    mask = 1 << (n_qubits - 1 - qubit)
    p0 = sum(abs(a)**2 for i, a in enumerate(state) if not (i & mask))
    outcome = int(rng.random() >= p0)
    for i in range(len(state)):
        if bool(i & mask) != bool(outcome):
            state[i] = 0
    norm = np.linalg.norm(state)
    if norm:
        state /= norm
    return state, outcome

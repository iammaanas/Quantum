"""State-vector quantum circuit simulation engine."""
import numpy as np
from gates import (SINGLE_QUBIT_GATES, rx, ry, rz, cnot_matrix, cz_matrix,
                   swap_matrix, toffoli_matrix)
from measurement import probabilities, sample_measurements

class QuantumEngine:
    def __init__(self, n_qubits=2):
        self.reset(n_qubits)

    def reset(self, n_qubits=None):
        if n_qubits is not None:
            n_qubits = int(n_qubits)
            if not 1 <= n_qubits <= 10:
                raise ValueError("Choose between 1 and 10 qubits")
            self.n_qubits = n_qubits
        self.state = np.zeros(2 ** self.n_qubits, dtype=complex)
        self.state[0] = 1
        self.log = []

    def _apply(self, matrix, label, qubits):
        self.state = matrix @ self.state
        self.state /= np.linalg.norm(self.state)
        self.log.append({"gate": label, "qubits": list(qubits)})

    def apply_gate(self, gate, qubits, theta=None):
        gate = str(gate).upper()
        qubits = [int(q) for q in qubits]
        if any(q < 0 or q >= self.n_qubits for q in qubits):
            raise ValueError("Qubit index out of range")
        if gate in SINGLE_QUBIT_GATES or gate in ("RX", "RY", "RZ"):
            if len(qubits) != 1:
                raise ValueError(f"{gate} requires one qubit")
            base = SINGLE_QUBIT_GATES.get(gate)
            if gate == "RX": base = rx(float(theta or 0))
            if gate == "RY": base = ry(float(theta or 0))
            if gate == "RZ": base = rz(float(theta or 0))
            full = np.array([[1]], dtype=complex)
            for q in range(self.n_qubits):
                full = np.kron(full, base if q == qubits[0] else np.eye(2))
            self._apply(full, gate, qubits)
        elif gate in ("CNOT", "CX", "CZ", "SWAP"):
            if len(qubits) != 2 or qubits[0] == qubits[1]:
                raise ValueError(f"{gate} requires two distinct qubits")
            a, b = qubits
            matrix = (cnot_matrix(self.n_qubits, a, b) if gate in ("CNOT", "CX")
                      else cz_matrix(self.n_qubits, a, b) if gate == "CZ"
                      else swap_matrix(self.n_qubits, a, b))
            self._apply(matrix, gate, qubits)
        elif gate == "TOFFOLI":
            if len(qubits) != 3 or len(set(qubits)) != 3:
                raise ValueError("TOFFOLI requires three distinct qubits")
            self._apply(toffoli_matrix(self.n_qubits, *qubits), gate, qubits)
        else:
            raise ValueError(f"Unsupported gate: {gate}")
        return self.snapshot()

    def snapshot(self):
        p = probabilities(self.state)
        return {
            "n_qubits": self.n_qubits,
            "state": [{"basis": format(i, f"0{self.n_qubits}b"),
                       "real": float(a.real), "imag": float(a.imag),
                       "probability": float(p[i])}
                      for i, a in enumerate(self.state)],
            "log": self.log
        }

    def simulate(self, shots=1000):
        return {"snapshot": self.snapshot(),
                "counts": sample_measurements(self.state, shots)}

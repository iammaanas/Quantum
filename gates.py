"""Quantum gate matrices and gate application helpers."""
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

def rx(theta):
    c, s = np.cos(theta / 2), -1j * np.sin(theta / 2)
    return np.array([[c, s], [s, c]], dtype=complex)

def ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)

def rz(theta):
    return np.diag([np.exp(-1j * theta / 2), np.exp(1j * theta / 2)]).astype(complex)

SINGLE_QUBIT_GATES = {"I": I, "X": X, "Y": Y, "Z": Z, "H": H, "S": S, "T": T}

def controlled_matrix(n_qubits, control, target, base_gate):
    """Construct a controlled single-qubit operation in big-endian qubit order."""
    dim = 2 ** n_qubits
    result = np.zeros((dim, dim), dtype=complex)
    for col in range(dim):
        bits = [(col >> (n_qubits - 1 - q)) & 1 for q in range(n_qubits)]
        if bits[control] == 1:
            out = bits.copy()
            a, b = base_gate[:, bits[target]]
            for value, amp in enumerate((a, b)):
                out_bits = out.copy()
                out_bits[target] = value
                row = sum(bit << (n_qubits - 1 - q) for q, bit in enumerate(out_bits))
                result[row, col] += amp
        else:
            result[col, col] = 1
    return result

def cnot_matrix(n, control, target):
    return controlled_matrix(n, control, target, X)

def cz_matrix(n, control, target):
    dim = 2 ** n
    m = np.eye(dim, dtype=complex)
    for i in range(dim):
        if ((i >> (n-1-control)) & 1) and ((i >> (n-1-target)) & 1):
            m[i, i] = -1
    return m

def swap_matrix(n, q1, q2):
    dim = 2 ** n
    m = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        bits = [(i >> (n-1-q)) & 1 for q in range(n)]
        bits[q1], bits[q2] = bits[q2], bits[q1]
        j = sum(bit << (n-1-q) for q, bit in enumerate(bits))
        m[j, i] = 1
    return m

def toffoli_matrix(n, c1, c2, target):
    dim = 2 ** n
    m = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        bits = [(i >> (n-1-q)) & 1 for q in range(n)]
        if bits[c1] and bits[c2]:
            bits[target] ^= 1
        j = sum(bit << (n-1-q) for q, bit in enumerate(bits))
        m[j, i] = 1
    return m

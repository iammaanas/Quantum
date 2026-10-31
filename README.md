# Quantum Circuit Simulator

A browser-based quantum circuit simulator built with Python, Flask, NumPy and state-vector mathematics.

## Features

- State-vector simulation for 1–10 qubits.
- Single-qubit gates: I, X, Y, Z, H, S, T, RX, RY and RZ.
- Multi-qubit gates: CNOT/CX, CZ, SWAP and Toffoli.
- Measurement probabilities, repeated shot sampling and a single-qubit projective measurement helper.
- Interactive dark-mode browser UI with circuit operation log, state-vector table and measurement distribution.
- Preset demonstrations: coin-flip superposition, H-H interference, Bell entanglement, all four Bell states, GHZ and RY rotation.
- JSON API for gate application, simulation and demonstrations.

## Run locally

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/iammaanas/Quantum.git
cd Quantum
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## API

- `GET /` — simulator UI
- `GET /health` — health check
- `GET /api/gates` — available gates
- `POST /api/simulate` — simulate a sequence of gates and sample measurements
- `POST /api/gates` — apply one gate to a named in-memory session
- `GET /api/demo/<name>` — run a preset demo

Example request:

```json
{
  "session_id": "demo",
  "n_qubits": 2,
  "gates": [
    {"gate": "H", "qubits": [0]},
    {"gate": "CNOT", "qubits": [0, 1]}
  ],
  "shots": 1000
}
```

Qubit 0 is the leftmost bit in basis-state labels. The simulator uses normalized complex state vectors and applies unitary matrices. Measurement probabilities are the squared magnitudes of state amplitudes.

## Project layout

```
app.py                 Flask app and JSON API
quantum_engine.py      State-vector engine and gate orchestration
gates.py               Gate matrices and controlled operations
measurement.py         Probability, sampling and collapse helpers
templates/index.html   Interactive browser interface
requirements.txt       Python dependencies
```

## Notes

This is a reconstruction of the project based on its recorded specifications and earlier project discussions. It restores the documented functionality, but may not be byte-for-byte identical to the lost original. The current Flask demo keeps sessions in process memory; use a persistent session store before deploying it for multiple users.

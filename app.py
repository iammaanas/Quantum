"""Flask web interface and JSON API for the Quantum Circuit Simulator."""
from flask import Flask, render_template, request, jsonify
from quantum_engine import QuantumEngine
from gates import SINGLE_QUBIT_GATES

app = Flask(__name__)
ENGINES = {}

def get_engine(session_id="default", n_qubits=2):
    if session_id not in ENGINES:
        ENGINES[session_id] = QuantumEngine(n_qubits)
    return ENGINES[session_id]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/gates")
def api_gates():
    return jsonify({"single": list(SINGLE_QUBIT_GATES) + ["RX", "RY", "RZ"],
                    "multi": ["CNOT", "CZ", "SWAP", "TOFFOLI"]})

@app.post("/api/simulate")
def api_simulate():
    data = request.get_json(force=True)
    sid = str(data.get("session_id", "default"))
    try:
        n = int(data.get("n_qubits", 2))
        engine = ENGINES.get(sid)
        if engine is None or engine.n_qubits != n or data.get("reset"):
            engine = QuantumEngine(n)
            ENGINES[sid] = engine
        for operation in data.get("gates", []):
            engine.apply_gate(operation["gate"], operation.get("qubits", [0]),
                              operation.get("theta"))
        return jsonify(engine.simulate(int(data.get("shots", 1000))))
    except (ValueError, KeyError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/gates")
def apply_gate():
    data = request.get_json(force=True)
    sid = str(data.get("session_id", "default"))
    try:
        engine = get_engine(sid, int(data.get("n_qubits", 2)))
        if data.get("reset"):
            engine.reset(int(data.get("n_qubits", 2)))
        result = engine.apply_gate(data["gate"], data.get("qubits", [0]), data.get("theta"))
        return jsonify(result)
    except (ValueError, KeyError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.get("/api/demo/<name>")
def demo(name):
    presets = {
        "coin": (1, [("H", [0])]),
        "interference": (1, [("H", [0]), ("H", [0])]),
        "bell": (2, [("H", [0]), ("CNOT", [0, 1])]),
        "ghz": (3, [("H", [0]), ("CNOT", [0, 1]), ("CNOT", [0, 2])]),
        "ry": (1, [("RY", [0], 1.57079632679)])
    }
    if name in ("bell_phi_plus", "bell_phi_minus", "bell_psi_plus", "bell_psi_minus"):
        suffix = name.split("_")[-1]
        ops = [("H", [0]), ("CNOT", [0, 1])]
        if suffix == "minus": ops.insert(1, ("Z", [0]))
        if suffix.startswith("psi"): ops.insert(0, ("X", [1]))
        presets[name] = (2, ops)
    if name not in presets:
        return jsonify({"error": "Unknown demo"}), 404
    n, ops = presets[name]
    engine = QuantumEngine(n)
    for op in ops:
        engine.apply_gate(*op)
    return jsonify(engine.simulate(1000))

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)

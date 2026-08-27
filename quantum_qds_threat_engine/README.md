# Quantum-Inspired Cyber Threat Detection for Digital Signature Security (ID: 26141)

**Organization / Department**: Egreen Quanta  
**Category**: Software | **Theme**: Blockchain & Cybersecurity  
**Design Principle**: Strictly Non-AI / Non-ML Information-Theoretic Threat Defense

---

## Overview
This framework provides a quantum-inspired cyber threat detection engine specifically designed for teleportation-based Quantum Digital Signature (QDS) systems. It detects threats to digital signature integrity and authenticity—such as existential forgery, dishonest receiver framing, replay attacks, man-in-the-middle, and quantum channel probing—**without relying on artificial intelligence or machine learning**. Instead, it uses foundational quantum principles (Pauli eigenstates, Bell-state entanglement, Bell State Measurements, projective measurements, CHSH correlation witnesses) and rigorous statistical threshold estimation (QBER, Hoeffding bounds, exact Binomial testing).

---

## Key Features

1. **Quantum Teleportation QDS Protocol**:
   - Alice (Signer), Bob (Recipient/Verifier 1), and Charlie (Independent Auditor/Verifier 2).
   - Bell pairs ($|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$), Bell State Measurements (BSM), and Pauli unitary corrections ($I, X, Y, Z$).
   - Interleaved Pauli decoy states for transit channel surveillance.

2. **Strictly Non-AI Quantum Threat Detection Engine**:
   - Quantum Bit Error Rate (QBER) and Pauli basis error decomposition ($X$ bit-flip vs $Z$ phase-flip).
   - Bell-CHSH entanglement witness ($S \ge 2.80$ for entangled states vs $S \le 2.0$ for classical separable states).
   - Hoeffding deviation bounds and exact one-tailed Binomial $p$-values.
   - Dual-verifier dispute resolution and non-repudiation arbitration.

3. **7-Vector Quantum Cyber Attack Simulator**:
   - Intercept-Resend Eavesdropping (measure-and-forward in random Pauli bases).
   - CNOT Ancilla Entanglement Probing.
   - Quantum Man-in-the-Middle (MITM).
   - Existential & Chosen-Message Signature Forgery.
   - Dishonest Receiver Forgery (Malicious Bob framing Alice to Charlie).
   - Cryptographic & Quantum Session Replay Attacks.
   - Coherent Quantum Channel Jamming / Depolarization.

4. **Interactive Cyber-Quantum Command Center UI & CLI**:
   - Modern Web Dashboard with real-time Bell telemetry, live quantum circuit pipeline, interactive attack injection sandbox, non-AI mathematical proof HUD, and multi-verifier arbitration logs.
   - Interactive CLI runner with menu-driven execution.

---

## Quick Start Guide

### 1. Run Automated Test Suite
```bash
python run_tests.py
```
*Executes all 15 unit and integration tests across quantum core, protocol, threat detection, and statistical bounds.*

### 2. Run Interactive CLI
```bash
python cli/main_cli.py
```
*Provides an interactive console to simulate all attack vectors, inspect threat reports, and run benchmarks.*

### 3. Run Benchmark Suite & Launch Web Dashboard
```bash
python run_simulation.py
```
*Runs the Monte Carlo simulation, generates ROC and security scaling plots, and starts the Web Dashboard on http://localhost:8080.*

---

## Directory Structure
```
quantum_qds_threat_engine/
├── core/
│   ├── quantum_states.py         # Pure states, Pauli eigenstates, projective measurements, fidelity
│   ├── bell_pairs.py             # Bell states (|Phi+>), BSM projectors, Bell-CHSH witness
│   ├── teleportation.py          # 3-qubit teleportation, BSM, Pauli corrections U(c1, c2)
│   └── qds_protocol.py           # Multi-party QDS lifecycle (Alice, Bob, Charlie, arbitration)
├── threat_detection/
│   ├── quantum_metrics.py        # QBER, Pauli error decomposition, CHSH witness evaluation
│   ├── statistical_bounds.py     # Hoeffding bounds, exact Binomial testing, KL-divergence, P_forge
│   ├── decoy_state_analyzer.py   # Pauli decoy state disturbance & transit collapse
│   ├── anti_replay_engine.py     # Cryptographic session nonces, Bell index binding
│   └── threat_detector.py        # Central Non-AI Rule-Based Decision & Threat Classification Engine
├── simulation/
│   ├── noise_channels.py         # Depolarizing, bit-flip, phase-flip, amplitude damping channels
│   ├── attack_simulator.py       # 7+ quantum attack models
│   └── benchmark_engine.py       # Monte Carlo benchmarking, ROC curve & plot generation
├── cli/
│   └── main_cli.py               # Interactive CLI tool
├── ui/
│   ├── dashboard_app.py          # Standalone HTTP server & REST API
│   └── static/
│       ├── index.html            # Cyber-Quantum Command Center HTML
│       ├── style.css             # Cyber neon styling
│       └── app.js                # Dynamic telemetry & UI controller
├── tests/
│   ├── test_quantum_core.py      # Quantum mechanics unit tests
│   ├── test_qds_protocol.py      # Protocol acceptance tests
│   ├── test_threat_detection.py  # Attack detection tests
│   └── test_statistical_bounds.py# Statistical bounds tests
├── docs/
│   ├── mathematical_formulation.md # Full mathematical derivations & security proofs
│   └── delivery_table.md         # Deliverables table matching problem statement
├── run_tests.py                  # Automated test runner
└── run_simulation.py             # Master benchmark & dashboard runner
```

---

## Mathematical Security Guarantees
- **Information-Theoretic Forgery Bound**:
  $$P_{\text{forge}} \le \exp\left(-N \cdot D_{\text{KL}}(e_v \parallel e_d)\right)$$
- **Fidelity Bound under Eavesdropping**:
  $$D = 1 - F \ge \frac{1}{2}(1 - \sqrt{F})$$
- **CHSH Violation Criterion**:
  $$S > 2.0 \implies \text{Quantum Entanglement Preserved}$$

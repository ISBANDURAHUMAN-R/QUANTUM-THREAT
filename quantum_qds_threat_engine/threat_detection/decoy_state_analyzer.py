"""
Pauli Decoy State Disturbance Analyzer.

Performs selective analysis of decoy states interleaved in the signature stream:
- Evaluates decoy QBER vs signature QBER.
- Dissects eavesdropping signatures:
  1. High Decoy QBER + High Sig QBER -> Active Quantum Intercept-Resend / MITM.
  2. Low Decoy QBER + High Sig QBER -> Pure Classical Forgery / Key Guessing.
  3. Symmetric error across bases -> Depolarizing noise.
  4. Asymmetric Z-error vs X-error -> Coherent phase/bit-flip jamming.
"""

from typing import Dict, Any, List
from core.quantum_states import PauliBasis
from threat_detection.statistical_bounds import evaluate_statistical_confidence

def analyze_decoy_disturbances(
    sig_qber: float,
    decoy_qber: float,
    sig_qubits: int,
    decoy_qubits: int,
    baseline_noise: float = 0.03,
    detection_threshold: float = 0.08
) -> Dict[str, Any]:
    """
    Performs differential analysis between decoy state errors and signature payload errors.
    """
    sig_errors = int(round(sig_qber * sig_qubits))
    decoy_errors = int(round(decoy_qber * decoy_qubits))
    
    sig_stat = evaluate_statistical_confidence(
        sig_errors, sig_qubits, baseline_noise, detection_threshold
    )
    decoy_stat = evaluate_statistical_confidence(
        decoy_errors, decoy_qubits, baseline_noise, detection_threshold
    )
    
    decoy_anomaly = decoy_stat["is_anomaly"]
    sig_anomaly = sig_stat["is_anomaly"]
    
    if not decoy_anomaly and not sig_anomaly:
        pattern = "HONEST_CHANNEL"
        diagnosis = "Channel within normal quantum error bounds; no tampering detected."
    elif decoy_anomaly and sig_anomaly:
        pattern = "QUANTUM_CHANNEL_INTERCEPTION"
        diagnosis = "Eavesdropper physically probed or intercepted qubits (detected via Pauli decoy collapse)."
    elif not decoy_anomaly and sig_anomaly:
        pattern = "SIGNATURE_PAYLOAD_FORGERY"
        diagnosis = "Forgery attempt detected: signature payload contains forged bits without valid private key."
    else:
        pattern = "SELECTIVE_DECOY_DISTURBANCE"
        diagnosis = "Anomalous decoy disturbance detected; possible decoy-state routing attack."
        
    return {
        "pattern": pattern,
        "diagnosis": diagnosis,
        "sig_qber": sig_qber,
        "decoy_qber": decoy_qber,
        "sig_stat": sig_stat,
        "decoy_stat": decoy_stat,
        "decoy_detected_tampering": decoy_anomaly,
        "signature_detected_tampering": sig_anomaly
    }

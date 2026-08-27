"""
Quantum Metrics for Threat Detection.

Calculates quantum-mechanical invariants and observables used to detect cyber threats:
- Quantum Bit Error Rate (QBER)
- Pauli error decomposition (X bit-flip vs Z phase-flip vs Y combined)
- Bell-CHSH inequality violation witness
- Quantum state fidelity & disturbance (1 - F)
- Trace distance
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from core.quantum_states import (
    PauliBasis, quantum_fidelity, trace_distance,
    state_to_density_matrix, bloch_vector,
    PAULI_X, PAULI_Y, PAULI_Z, PAULI_I
)
from core.bell_pairs import compute_chsh_witness

def compute_qber(expected_bits: List[int], measured_bits: List[int]) -> float:
    """Computes the Quantum Bit Error Rate (QBER) e = N_errors / N_total."""
    if not expected_bits or len(expected_bits) != len(measured_bits):
        return 1.0
    errors = sum(1 for exp, meas in zip(expected_bits, measured_bits) if exp != meas)
    return float(errors / len(expected_bits))

def compute_pauli_error_decomposition(
    logs: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Decomposes errors by Pauli basis (Z: bit-flip, X: phase-flip, Y: combined).
    Enables differentiation between depolarizing noise and targeted coherent attacks.
    """
    basis_counts = {"Z": 0, "X": 0, "Y": 0}
    basis_errors = {"Z": 0, "X": 0, "Y": 0}
    
    for entry in logs:
        basis = entry.get("basis", "Z")
        is_err = entry.get("error", False)
        if basis in basis_counts:
            basis_counts[basis] += 1
            if is_err:
                basis_errors[basis] += 1
                
    qber_z = float(basis_errors["Z"] / basis_counts["Z"]) if basis_counts["Z"] > 0 else 0.0
    qber_x = float(basis_errors["X"] / basis_counts["X"]) if basis_counts["X"] > 0 else 0.0
    qber_y = float(basis_errors["Y"] / basis_counts["Y"]) if basis_counts["Y"] > 0 else 0.0
    
    return {
        "qber_z_bit_flip": qber_z,
        "qber_x_phase_flip": qber_x,
        "qber_y_combined": qber_y,
        "counts": basis_counts,
        "errors": basis_errors
    }

def evaluate_bell_witness(bell_pairs: List[np.ndarray]) -> Dict[str, Any]:
    """
    Evaluates the average CHSH witness value across a batch of distributed Bell pairs.
    Ideal Bell state |Phi+>: S = 2*sqrt(2) approx 2.8284.
    Classical bound: S <= 2.0.
    """
    if not bell_pairs:
        return {"mean_chsh": 0.0, "quantum_violation": False, "entanglement_level": "None"}
        
    s_values = [compute_chsh_witness(pair) for pair in bell_pairs]
    mean_s = float(np.mean(s_values))
    
    quantum_violation = (mean_s > 2.0)
    
    if mean_s >= 2.70:
        level = "Maximal (Pristine Entanglement)"
    elif mean_s > 2.0:
        level = "Partial (Degraded / Probed Entanglement)"
    else:
        level = "Classical / Separable (Entanglement Broken / MITM)"
        
    return {
        "mean_chsh_s": mean_s,
        "theoretical_max": 2.0 * np.sqrt(2.0),
        "classical_bound": 2.0,
        "quantum_violation": quantum_violation,
        "entanglement_level": level,
        "sample_size": len(bell_pairs)
    }

def compute_quantum_disturbance(
    target_states: List[np.ndarray],
    reference_states: List[np.ndarray]
) -> Dict[str, float]:
    """Computes average fidelity and state disturbance D = 1 - F."""
    if not target_states or len(target_states) != len(reference_states):
        return {"mean_fidelity": 0.0, "mean_disturbance": 1.0}
        
    fidelities = [quantum_fidelity(t, r) for t, r in zip(target_states, reference_states)]
    mean_f = float(np.mean(fidelities))
    mean_d = float(1.0 - mean_f)
    
    return {
        "mean_fidelity": mean_f,
        "mean_disturbance": mean_d,
        "min_fidelity": float(np.min(fidelities)),
        "max_fidelity": float(np.max(fidelities))
    }

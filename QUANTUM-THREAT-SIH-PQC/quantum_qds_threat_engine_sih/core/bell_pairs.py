"""
Bell States, Entanglement Distribution, and Bell State Measurements (BSM).

This module implements:
- The four maximally entangled Bell states (EPR pairs)
- Bell State Measurements (BSM) on 2-qubit systems
- Bell-CHSH inequality operator and correlation witness
- Entanglement quality verification
"""

import numpy as np
from enum import Enum
from typing import Tuple, List, Optional
from core.quantum_states import (
    STATE_0, STATE_1, state_to_density_matrix,
    PAULI_X, PAULI_Y, PAULI_Z, PAULI_I
)

class BellStateEnum(Enum):
    PHI_PLUS = "Phi+"    # (|00> + |11>) / sqrt(2)  -> Outcome (0, 0)
    PHI_MINUS = "Phi-"   # (|00> - |11>) / sqrt(2)  -> Outcome (0, 1)
    PSI_PLUS = "Psi+"    # (|01> + |10>) / sqrt(2)  -> Outcome (1, 0)
    PSI_MINUS = "Psi-"   # (|01> - |10>) / sqrt(2)  -> Outcome (1, 1)

# Standard 2-qubit basis vectors
KET_00 = np.kron(STATE_0, STATE_0)
KET_01 = np.kron(STATE_0, STATE_1)
KET_10 = np.kron(STATE_1, STATE_0)
KET_11 = np.kron(STATE_1, STATE_1)

# Bell State Vectors
BELL_PHI_PLUS = (KET_00 + KET_11) / np.sqrt(2.0)
BELL_PHI_MINUS = (KET_00 - KET_11) / np.sqrt(2.0)
BELL_PSI_PLUS = (KET_01 + KET_10) / np.sqrt(2.0)
BELL_PSI_MINUS = (KET_01 - KET_10) / np.sqrt(2.0)

BELL_STATE_VECTORS = {
    BellStateEnum.PHI_PLUS: BELL_PHI_PLUS,
    BellStateEnum.PHI_MINUS: BELL_PHI_MINUS,
    BellStateEnum.PSI_PLUS: BELL_PSI_PLUS,
    BellStateEnum.PSI_MINUS: BELL_PSI_MINUS,
}

# Bell State Projectors
PROJ_PHI_PLUS = np.outer(BELL_PHI_PLUS, np.conj(BELL_PHI_PLUS))
PROJ_PHI_MINUS = np.outer(BELL_PHI_MINUS, np.conj(BELL_PHI_MINUS))
PROJ_PSI_PLUS = np.outer(BELL_PSI_PLUS, np.conj(BELL_PSI_PLUS))
PROJ_PSI_MINUS = np.outer(BELL_PSI_MINUS, np.conj(BELL_PSI_MINUS))

BSM_PROJECTORS = [
    (BellStateEnum.PHI_PLUS, PROJ_PHI_PLUS, (0, 0)),
    (BellStateEnum.PHI_MINUS, PROJ_PHI_MINUS, (0, 1)),
    (BellStateEnum.PSI_PLUS, PROJ_PSI_PLUS, (1, 0)),
    (BellStateEnum.PSI_MINUS, PROJ_PSI_MINUS, (1, 1)),
]

def create_bell_pair(state_type: BellStateEnum = BellStateEnum.PHI_PLUS) -> np.ndarray:
    """Generates a 2-qubit Bell state vector."""
    return BELL_STATE_VECTORS[state_type].copy()

def perform_bell_state_measurement(
    two_qubit_state: np.ndarray,
    rng: Optional[np.random.Generator] = None
) -> Tuple[BellStateEnum, Tuple[int, int], float]:
    """
    Performs a full Bell State Measurement (BSM) on a 2-qubit density matrix or state vector.
    
    Returns:
        bell_state: The resulting BellStateEnum
        classical_bits: 2-bit classical outcome (c1, c2)
        prob: Probability of the measurement outcome
    """
    if rng is None:
        rng = np.random.default_rng()
        
    rho = two_qubit_state if two_qubit_state.ndim == 2 else state_to_density_matrix(two_qubit_state)
    
    probabilities = []
    for b_enum, proj, bits in BSM_PROJECTORS:
        p = float(np.real(np.trace(proj @ rho)))
        p = max(p, 0.0)
        probabilities.append(p)
        
    prob_sum = sum(probabilities)
    if prob_sum > 0:
        normalized_probs = [p / prob_sum for p in probabilities]
    else:
        normalized_probs = [0.25, 0.25, 0.25, 0.25]
        
    idx = rng.choice(len(BSM_PROJECTORS), p=normalized_probs)
    b_enum, _, bits = BSM_PROJECTORS[idx]
    
    return b_enum, bits, normalized_probs[idx]

def compute_chsh_witness(two_qubit_state: np.ndarray) -> float:
    """
    Computes the Clauser-Horne-Shimony-Holt (CHSH) Bell inequality correlation S.
    For local realistic theories, |S| <= 2.
    For maximally entangled state |Phi+>, S = 2 * sqrt(2) approx 2.8284.
    
    Observables:
      Alice: A1 = Z, A2 = X
      Bob:   B1 = (Z + X) / sqrt(2), B2 = (Z - X) / sqrt(2)
      CHSH Operator: B_CHSH = A1 (x) B1 + A1 (x) B2 + A2 (x) B1 - A2 (x) B2
    """
    rho = two_qubit_state if two_qubit_state.ndim == 2 else state_to_density_matrix(two_qubit_state)
    
    a1 = PAULI_Z
    a2 = PAULI_X
    b1 = (PAULI_Z + PAULI_X) / np.sqrt(2.0)
    b2 = (PAULI_Z - PAULI_X) / np.sqrt(2.0)
    
    chsh_op = (
        np.kron(a1, b1) +
        np.kron(a1, b2) +
        np.kron(a2, b1) -
        np.kron(a2, b2)
    )
    
    s_val = float(np.real(np.trace(rho @ chsh_op)))
    return s_val

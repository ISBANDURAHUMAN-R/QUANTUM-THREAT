"""
Quantum Teleportation Engine.

Implements the standard 3-qubit teleportation protocol:
1. Shared Bell pair (rho_23) between Alice (qubit 2) and Bob (qubit 3).
2. Alice couples message qubit 1 (|psi>_1) with qubit 2 and performs Bell State Measurement (BSM).
3. Alice transmits 2 classical bits (c1, c2) over a classical channel.
4. Bob applies corresponding Pauli unitary correction U_corr = Z^c2 * X^c1 on qubit 3.
5. Teleported state reconstruction and fidelity verification.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional
from core.quantum_states import (
    STATE_0, STATE_1, state_to_density_matrix, quantum_fidelity,
    PAULI_I, PAULI_X, PAULI_Y, PAULI_Z, PauliEigenstate, get_eigenstate_vector
)
from core.bell_pairs import (
    BellStateEnum, BELL_PHI_PLUS, perform_bell_state_measurement,
    BSM_PROJECTORS
)

PAULI_CORRECTIONS = {
    (0, 0): PAULI_I,
    (0, 1): PAULI_Z,
    (1, 0): PAULI_X,
    (1, 1): PAULI_X @ PAULI_Z,
}

def get_pauli_correction(c1: int, c2: int) -> np.ndarray:
    """Returns the 2x2 Pauli correction unitary for classical BSM bits (c1, c2)."""
    return PAULI_CORRECTIONS.get((c1, c2), PAULI_I).copy()

def simulate_teleportation(
    message_state: np.ndarray,
    shared_bell_pair: Optional[np.ndarray] = None,
    channel_noise_operator: Optional[np.ndarray] = None,
    rng: Optional[np.random.Generator] = None
) -> Dict[str, Any]:
    """
    Executes a complete teleportation round from Alice to Bob for general pure or mixed states.
    """
    if rng is None:
        rng = np.random.default_rng()
        
    if shared_bell_pair is None:
        shared_bell_pair = BELL_PHI_PLUS.copy()
        
    # Density matrix for message qubit 1: rho_1 (2x2)
    rho_1 = message_state if message_state.ndim == 2 else state_to_density_matrix(message_state)
    
    # Density matrix for shared Bell pair 23: rho_23 (4x4)
    rho_23 = shared_bell_pair if shared_bell_pair.ndim == 2 else state_to_density_matrix(shared_bell_pair)
    
    # Total 3-qubit density matrix: rho_123 = rho_1 (x) rho_23 (8x8)
    rho_123 = np.kron(rho_1, rho_23)
    
    # Partial trace over qubit 3 to get Alice's 2-qubit subsystem (qubits 1 & 2)
    # Reshape into 6-index tensor (2, 2, 2, 2, 2, 2) where indices are (i1, i2, i3, j1, j2, j3)
    rho_tensor = rho_123.reshape(2, 2, 2, 2, 2, 2)
    rho_12 = np.trace(rho_tensor, axis1=2, axis2=5).reshape(4, 4)
    
    # Alice performs BSM on qubits 1 and 2
    bsm_enum, classical_bits, bsm_prob = perform_bell_state_measurement(rho_12, rng=rng)
    c1, c2 = classical_bits
    
    # Post-measurement state of Bob's qubit 3:
    # rho_3 = 1/p_k * Tr_12((Pi_k (x) I_3) rho_123)
    # Find matching projector Pi_k
    proj_k = None
    for b_enum, p_op, bits in BSM_PROJECTORS:
        if bits == (c1, c2):
            proj_k = p_op
            break
            
    proj_123 = np.kron(proj_k, PAULI_I)
    rho_collapsed_123 = proj_123 @ rho_123 @ proj_123
    tensor_collapsed = rho_collapsed_123.reshape(2, 2, 2, 2, 2, 2)
    
    # Trace out qubits 1 and 2
    # First trace out qubit 1 (axis 0 and 3)
    tr1 = np.trace(tensor_collapsed, axis1=0, axis2=3) # shape (2, 2, 2, 2) -> (i2, i3, j2, j3)
    # Then trace out qubit 2 (axis 0 and 2)
    rho_3 = np.trace(tr1, axis1=0, axis2=2) # shape (2, 2) -> (i3, j3)
    
    tr_rho3 = np.real(np.trace(rho_3))
    if tr_rho3 > 1e-12:
        rho_3 = rho_3 / tr_rho3
    else:
        rho_3 = np.eye(2, dtype=complex) * 0.5
        
    # Bob applies Pauli correction unitary
    u_corr = get_pauli_correction(c1, c2)
    
    # Channel noise if any
    if channel_noise_operator is not None:
        rho_3 = channel_noise_operator @ rho_3 @ channel_noise_operator.conj().T
        
    bob_final_rho = u_corr @ rho_3 @ u_corr.conj().T
    
    fid = quantum_fidelity(rho_1, bob_final_rho)
    
    # If state is pure enough, extract dominant eigenvector
    evals, evecs = np.linalg.eigh(bob_final_rho)
    bob_final_state = evecs[:, np.argmax(evals)]
    
    return {
        "bsm_outcome": bsm_enum.value,
        "classical_bits": classical_bits,
        "pauli_correction": f"U({c1},{c2})",
        "bob_reconstructed_state": bob_final_state,
        "bob_reconstructed_rho": bob_final_rho,
        "fidelity": fid,
        "bsm_probability": bsm_prob
    }

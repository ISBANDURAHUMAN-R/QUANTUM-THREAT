"""
Unit tests for Core Quantum Mechanics and Teleportation primitives.
"""

import numpy as np
from core.quantum_states import (
    PauliBasis, PauliEigenstate, get_eigenstate_vector,
    state_to_density_matrix, quantum_fidelity, trace_distance,
    perform_projective_measurement, bloch_vector,
    STATE_0, STATE_1, STATE_PLUS, STATE_MINUS, STATE_RIGHT, STATE_LEFT,
    PAULI_X, PAULI_Y, PAULI_Z, PAULI_I
)
from core.bell_pairs import (
    create_bell_pair, BellStateEnum, compute_chsh_witness,
    perform_bell_state_measurement
)
from core.teleportation import simulate_teleportation

def test_pauli_eigenstate_properties():
    """Verify eigenstates satisfy sigma_i |psi> = lambda |psi|."""
    np.testing.assert_allclose(PAULI_Z @ STATE_0, STATE_0, atol=1e-7)
    np.testing.assert_allclose(PAULI_Z @ STATE_1, -STATE_1, atol=1e-7)
    np.testing.assert_allclose(PAULI_X @ STATE_PLUS, STATE_PLUS, atol=1e-7)
    np.testing.assert_allclose(PAULI_X @ STATE_MINUS, -STATE_MINUS, atol=1e-7)
    np.testing.assert_allclose(PAULI_Y @ STATE_RIGHT, STATE_RIGHT, atol=1e-7)
    np.testing.assert_allclose(PAULI_Y @ STATE_LEFT, -STATE_LEFT, atol=1e-7)

def test_quantum_fidelity_and_trace_distance():
    """Verify fidelity F=1 for identical states and F=0 for orthogonal states."""
    assert abs(quantum_fidelity(STATE_0, STATE_0) - 1.0) < 1e-6
    assert abs(quantum_fidelity(STATE_0, STATE_1) - 0.0) < 1e-6
    assert abs(quantum_fidelity(STATE_PLUS, STATE_MINUS) - 0.0) < 1e-6
    assert abs(quantum_fidelity(STATE_0, STATE_PLUS) - 0.5) < 1e-6
    
    # Trace distance
    assert abs(trace_distance(STATE_0, STATE_0) - 0.0) < 1e-6
    assert abs(trace_distance(STATE_0, STATE_1) - 1.0) < 1e-6

def test_bell_state_and_chsh_violation():
    """Verify Bell state |Phi+> yields maximal CHSH violation S = 2*sqrt(2)."""
    phi_plus = create_bell_pair(BellStateEnum.PHI_PLUS)
    s_val = compute_chsh_witness(phi_plus)
    assert abs(s_val - 2.0 * np.sqrt(2.0)) < 1e-4

def test_quantum_teleportation_perfect_fidelity():
    """Verify that ideal quantum teleportation reconstructs any arbitrary pure state with F=1.0."""
    states_to_test = [STATE_0, STATE_1, STATE_PLUS, STATE_MINUS, STATE_RIGHT, STATE_LEFT]
    for state in states_to_test:
        result = simulate_teleportation(state)
        assert abs(result["fidelity"] - 1.0) < 1e-5

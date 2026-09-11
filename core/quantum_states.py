"""
Quantum States, Pauli Eigenstates, and Measurement Operators.

This module provides the foundational quantum mathematical structures:
- Pure states and density matrices
- Pauli matrices (I, X, Y, Z) and their eigenstates in Z, X, and Y bases
- Projective measurement operators (Born rule and state collapse)
- Quantum state fidelity, trace distance, and Bloch vector extraction
"""

import numpy as np
from enum import Enum
from typing import Tuple, Dict, Any, Optional

class PauliBasis(Enum):
    Z = "Z"  # Computational basis {|0>, |1>}
    X = "X"  # Hadamard basis {|+>, |->}
    Y = "Y"  # Circular basis {|R>, |L>}

class PauliEigenstate(Enum):
    ZERO = "0"      # |0>
    ONE = "1"       # |1>
    PLUS = "+"      # |+>
    MINUS = "-"     # |->
    RIGHT = "R"     # |R> = (|0> + i|1>)/sqrt(2)
    LEFT = "L"      # |L> = (|0> - i|1>)/sqrt(2)

# Pauli Matrices
PAULI_I = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)

# Standard Pauli Eigenstate Vector Representations
STATE_0 = np.array([1.0, 0.0], dtype=complex)
STATE_1 = np.array([0.0, 1.0], dtype=complex)
STATE_PLUS = (STATE_0 + STATE_1) / np.sqrt(2.0)
STATE_MINUS = (STATE_0 - STATE_1) / np.sqrt(2.0)
STATE_RIGHT = (STATE_0 + 1.0j * STATE_1) / np.sqrt(2.0)
STATE_LEFT = (STATE_0 - 1.0j * STATE_1) / np.sqrt(2.0)

EIGENSTATE_MAP = {
    PauliEigenstate.ZERO: STATE_0,
    PauliEigenstate.ONE: STATE_1,
    PauliEigenstate.PLUS: STATE_PLUS,
    PauliEigenstate.MINUS: STATE_MINUS,
    PauliEigenstate.RIGHT: STATE_RIGHT,
    PauliEigenstate.LEFT: STATE_LEFT,
}

# Projectors
PROJ_0 = np.outer(STATE_0, np.conj(STATE_0))
PROJ_1 = np.outer(STATE_1, np.conj(STATE_1))
PROJ_PLUS = np.outer(STATE_PLUS, np.conj(STATE_PLUS))
PROJ_MINUS = np.outer(STATE_MINUS, np.conj(STATE_MINUS))
PROJ_RIGHT = np.outer(STATE_RIGHT, np.conj(STATE_RIGHT))
PROJ_LEFT = np.outer(STATE_LEFT, np.conj(STATE_LEFT))

BASIS_PROJECTORS = {
    PauliBasis.Z: (PROJ_0, PROJ_1),
    PauliBasis.X: (PROJ_PLUS, PROJ_MINUS),
    PauliBasis.Y: (PROJ_RIGHT, PROJ_LEFT),
}

BASIS_OUTCOME_STATES = {
    PauliBasis.Z: (STATE_0, STATE_1),
    PauliBasis.X: (STATE_PLUS, STATE_MINUS),
    PauliBasis.Y: (STATE_RIGHT, STATE_LEFT),
}

BASIS_OUTCOME_LABELS = {
    PauliBasis.Z: (0, 1),
    PauliBasis.X: (0, 1),  # 0 corresponds to |+>, 1 corresponds to |->
    PauliBasis.Y: (0, 1),  # 0 corresponds to |R>, 1 corresponds to |L>
}

def get_eigenstate_vector(state_enum: PauliEigenstate) -> np.ndarray:
    """Returns the normalized state vector for a given Pauli eigenstate."""
    return EIGENSTATE_MAP[state_enum].copy()

def state_to_density_matrix(psi: np.ndarray) -> np.ndarray:
    """Converts a pure state vector |psi> to a density matrix rho = |psi><psi|."""
    psi = psi / np.linalg.norm(psi)
    return np.outer(psi, np.conj(psi))

def quantum_fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Computes quantum state fidelity between two states.
    For pure states: F(|psi>, |phi>) = |<psi|phi>|^2.
    For density matrices: F(rho, sigma) = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2.
    """
    if state1.ndim == 1 and state2.ndim == 1:
        s1 = state1 / np.linalg.norm(state1)
        s2 = state2 / np.linalg.norm(state2)
        inner = np.vdot(s1, s2)
        return float(np.abs(inner) ** 2)
    
    rho = state1 if state1.ndim == 2 else state_to_density_matrix(state1)
    sigma = state2 if state2.ndim == 2 else state_to_density_matrix(state2)
    
    evals_rho, evecs_rho = np.linalg.eigh(rho)
    evals_rho = np.maximum(evals_rho, 0.0)
    sqrt_rho = evecs_rho @ np.diag(np.sqrt(evals_rho)) @ evecs_rho.conj().T
    
    m = sqrt_rho @ sigma @ sqrt_rho
    evals_m, _ = np.linalg.eigh(m)
    evals_m = np.maximum(evals_m, 0.0)
    fidelity = float(np.sum(np.sqrt(evals_m)) ** 2)
    return min(max(fidelity, 0.0), 1.0)

def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Computes the trace distance D(rho, sigma) = 1/2 * Tr|rho - sigma|."""
    if rho.ndim == 1:
        rho = state_to_density_matrix(rho)
    if sigma.ndim == 1:
        sigma = state_to_density_matrix(sigma)
    diff = rho - sigma
    evals, _ = np.linalg.eigh(diff)
    return float(0.5 * np.sum(np.abs(evals)))

def bloch_vector(state: np.ndarray) -> Tuple[float, float, float]:
    """
    Extracts the Bloch sphere vector (rx, ry, rz) from a single-qubit state or density matrix:
    rx = Tr(rho * X), ry = Tr(rho * Y), rz = Tr(rho * Z).
    """
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    rx = float(np.real(np.trace(rho @ PAULI_X)))
    ry = float(np.real(np.trace(rho @ PAULI_Y)))
    rz = float(np.real(np.trace(rho @ PAULI_Z)))
    return (rx, ry, rz)

def perform_projective_measurement(
    state: np.ndarray, 
    basis: PauliBasis, 
    rng: Optional[np.random.Generator] = None
) -> Tuple[int, np.ndarray, float]:
    """
    Performs a projective measurement in the specified PauliBasis (X, Y, or Z).
    
    Returns:
        outcome_bit: 0 or 1 (e.g., 0 for |0>, |+>, |R>; 1 for |1>, |->, |L>)
        collapsed_state: State vector after measurement collapse
        prob: Probability of the chosen outcome
    """
    if rng is None:
        rng = np.random.default_rng()
        
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    p0_proj, p1_proj = BASIS_PROJECTORS[basis]
    
    prob_0 = float(np.real(np.trace(p0_proj @ rho)))
    prob_0 = min(max(prob_0, 0.0), 1.0)
    prob_1 = 1.0 - prob_0
    
    if rng.random() < prob_0:
        outcome = 0
        collapsed_vec = BASIS_OUTCOME_STATES[basis][0].copy()
        prob = prob_0
    else:
        outcome = 1
        collapsed_vec = BASIS_OUTCOME_STATES[basis][1].copy()
        prob = prob_1
        
    return outcome, collapsed_vec, prob

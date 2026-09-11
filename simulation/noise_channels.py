"""
Quantum Noise Channels and Environmental Decoherence Models.

Implements standard quantum noise operations:
- Depolarizing channel: E(rho) = (1-p)*rho + (p/3)*(X*rho*X + Y*rho*Y + Z*rho*Z)
- Bit-flip channel: E(rho) = (1-p)*rho + p*X*rho*X
- Phase-flip channel: E(rho) = (1-p)*rho + p*Z*rho*Z
- Amplitude damping channel
- Unitary phase/rotation perturbations
"""

import numpy as np
from typing import Optional
from core.quantum_states import (
    state_to_density_matrix,
    PAULI_I, PAULI_X, PAULI_Y, PAULI_Z
)

def apply_depolarizing_noise(
    state: np.ndarray,
    p: float,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """Applies depolarizing channel with probability p."""
    if p <= 0.0:
        return state.copy()
    if rng is None:
        rng = np.random.default_rng()
        
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    
    # Kraus operators: sqrt(1-p)*I, sqrt(p/3)*X, sqrt(p/3)*Y, sqrt(p/3)*Z
    rho_noisy = (1.0 - p) * rho + (p / 3.0) * (
        PAULI_X @ rho @ PAULI_X.conj().T +
        PAULI_Y @ rho @ PAULI_Y.conj().T +
        PAULI_Z @ rho @ PAULI_Z.conj().T
    )
    return rho_noisy

def apply_bit_flip_noise(
    state: np.ndarray,
    p: float,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """Applies bit-flip (Pauli X) noise with probability p."""
    if p <= 0.0:
        return state.copy()
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    return (1.0 - p) * rho + p * (PAULI_X @ rho @ PAULI_X.conj().T)

def apply_phase_flip_noise(
    state: np.ndarray,
    p: float,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """Applies phase-flip (Pauli Z) noise with probability p."""
    if p <= 0.0:
        return state.copy()
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    return (1.0 - p) * rho + p * (PAULI_Z @ rho @ PAULI_Z.conj().T)

def apply_amplitude_damping(
    state: np.ndarray,
    gamma: float
) -> np.ndarray:
    """Applies amplitude damping channel with decay factor gamma in [0, 1]."""
    if gamma <= 0.0:
        return state.copy()
    rho = state if state.ndim == 2 else state_to_density_matrix(state)
    
    e0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - gamma)]], dtype=complex)
    e1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    
    return e0 @ rho @ e0.conj().T + e1 @ rho @ e1.conj().T

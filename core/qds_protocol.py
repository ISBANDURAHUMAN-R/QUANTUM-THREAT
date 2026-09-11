"""
Teleportation-Based Quantum Digital Signature (QDS) Protocol.

Implements the complete multi-party protocol:
- Alice (Signer)
- Bob (Recipient / Verifier 1)
- Charlie (Auditor / Verifier 2)

Protocol Steps:
1. Setup & Entanglement Distribution: Alice shares Bell pairs with Bob & Charlie.
2. Signature Generation: Alice encodes message M into Pauli eigenstates and teleports them.
3. Verification & Sifting: Bob & Charlie apply Pauli corrections, measure in corresponding bases,
   and evaluate error rates against statistical thresholds.
4. Non-Repudiation & Arbitration: Dual-verifier cross-parity guarantees security against signer repudiation.
"""

import numpy as np
import hashlib
import time
import secrets
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
from core.quantum_states import (
    PauliBasis, PauliEigenstate, get_eigenstate_vector,
    perform_projective_measurement, quantum_fidelity,
    BASIS_OUTCOME_LABELS
)
from core.bell_pairs import create_bell_pair, BellStateEnum
from core.teleportation import simulate_teleportation

@dataclass
class QDSSignaturePackage:
    message: str
    message_hash: str
    session_nonce: str
    timestamp: float
    classical_corrections_bob: List[Tuple[int, int]]
    classical_corrections_charlie: List[Tuple[int, int]]
    decoy_indices: List[int]
    signature_length: int

@dataclass
class QDSVerificationResult:
    is_valid: bool
    verifier_name: str
    qber_signature: float
    qber_decoy: float
    total_signature_qubits: int
    total_decoy_qubits: int
    errors_detected: int
    decision: str
    details: Dict[str, Any] = field(default_factory=dict)

class TeleportationQDSProtocol:
    def __init__(
        self,
        security_parameter_N: int = 128,
        decoy_ratio: float = 0.25,
        verification_threshold_ev: float = 0.08,
        dispute_threshold_ed: float = 0.18,
        rng_seed: Optional[int] = None
    ):
        self.N = security_parameter_N
        self.decoy_ratio = decoy_ratio
        self.num_decoy = int(self.N * decoy_ratio)
        self.total_qubits = self.N + self.num_decoy
        self.ev = verification_threshold_ev
        self.ed = dispute_threshold_ed
        self.rng = np.random.default_rng(rng_seed)
        
        # State tracking for Alice's private key and session memory
        self.alice_private_states: Dict[str, List[Dict[str, Any]]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def setup_entanglement_distribution(self) -> Dict[str, Any]:
        """
        Simulates the pre-distribution of EPR Bell pairs (|Phi+>) between Alice-Bob and Alice-Charlie.
        """
        session_nonce = secrets.token_hex(16)
        session_data = {
            "session_nonce": session_nonce,
            "created_at": time.time(),
            "total_qubits": self.total_qubits,
            "bell_pairs_bob": [create_bell_pair(BellStateEnum.PHI_PLUS) for _ in range(self.total_qubits)],
            "bell_pairs_charlie": [create_bell_pair(BellStateEnum.PHI_PLUS) for _ in range(self.total_qubits)],
        }
        self.active_sessions[session_nonce] = session_data
        return session_data

    def _message_to_pauli_states(
        self, 
        message: str, 
        session_nonce: str
    ) -> Tuple[List[Dict[str, Any]], List[int]]:
        """
        Encodes message bits into Pauli eigenstates with interleaved decoy states.
        Uses non-orthogonal states across X, Y, and Z bases for information-theoretic security.
        """
        # Hash message with session nonce to get deterministic bit expansion
        m_bytes = (message + session_nonce).encode('utf-8')
        h = hashlib.sha256(m_bytes).digest()
        
        # Expand hash into pseudo-random bitstream for N states
        expanded_bits = []
        counter = 0
        while len(expanded_bits) < self.N:
            block = hashlib.sha256(m_bytes + counter.to_bytes(4, 'big')).digest()
            for byte in block:
                for bit_pos in range(8):
                    expanded_bits.append((byte >> bit_pos) & 1)
            counter += 1
        expanded_bits = expanded_bits[:self.N]
        
        # Select random positions for decoy states
        all_indices = np.arange(self.total_qubits)
        decoy_indices = sorted(self.rng.choice(all_indices, size=self.num_decoy, replace=False).tolist())
        decoy_set = set(decoy_indices)
        
        pauli_state_sequence = []
        sig_bit_idx = 0
        
        bases = [PauliBasis.Z, PauliBasis.X, PauliBasis.Y]
        
        for idx in range(self.total_qubits):
            if idx in decoy_set:
                # Decoy state: randomly chosen Pauli eigenstate in X, Y, or Z
                basis = bases[self.rng.integers(0, 3)]
                bit_val = int(self.rng.integers(0, 2))
                is_decoy = True
            else:
                # Signature state: encodes the message bit into randomly chosen basis
                basis = bases[self.rng.integers(0, 3)]
                bit_val = expanded_bits[sig_bit_idx]
                sig_bit_idx += 1
                is_decoy = False
                
            if basis == PauliBasis.Z:
                state_enum = PauliEigenstate.ZERO if bit_val == 0 else PauliEigenstate.ONE
            elif basis == PauliBasis.X:
                state_enum = PauliEigenstate.PLUS if bit_val == 0 else PauliEigenstate.MINUS
            else:
                state_enum = PauliEigenstate.RIGHT if bit_val == 0 else PauliEigenstate.LEFT
                
            state_vec = get_eigenstate_vector(state_enum)
            
            pauli_state_sequence.append({
                "index": idx,
                "is_decoy": is_decoy,
                "basis": basis,
                "bit_val": bit_val,
                "state_enum": state_enum,
                "state_vec": state_vec
            })
            
        return pauli_state_sequence, decoy_indices

    def sign_message(
        self,
        message: str,
        session_nonce: Optional[str] = None
    ) -> Tuple[QDSSignaturePackage, Dict[str, Any]]:
        """
        Alice generates a quantum digital signature for message M using quantum teleportation.
        """
        if session_nonce is None or session_nonce not in self.active_sessions:
            session_data = self.setup_entanglement_distribution()
            session_nonce = session_data["session_nonce"]
        else:
            session_data = self.active_sessions[session_nonce]
            
        # 1. Encode message into Pauli states with decoy qubits
        quantum_state_seq, decoy_indices = self._message_to_pauli_states(message, session_nonce)
        self.alice_private_states[session_nonce] = quantum_state_seq
        
        # 2. Teleport signature states to Bob and Charlie
        corrections_bob = []
        corrections_charlie = []
        teleported_states_bob = []
        teleported_states_charlie = []
        
        for idx in range(self.total_qubits):
            psi_k = quantum_state_seq[idx]["state_vec"]
            
            # Teleport to Bob
            epr_bob = session_data["bell_pairs_bob"][idx]
            res_b = simulate_teleportation(psi_k, shared_bell_pair=epr_bob, rng=self.rng)
            corrections_bob.append(res_b["classical_bits"])
            teleported_states_bob.append(res_b["bob_reconstructed_state"])
            
            # Teleport to Charlie
            epr_charlie = session_data["bell_pairs_charlie"][idx]
            res_c = simulate_teleportation(psi_k, shared_bell_pair=epr_charlie, rng=self.rng)
            corrections_charlie.append(res_c["classical_bits"])
            teleported_states_charlie.append(res_c["bob_reconstructed_state"])
            
        # Store teleported quantum physical registers in session
        session_data["qubits_bob"] = teleported_states_bob
        session_data["qubits_charlie"] = teleported_states_charlie
        
        msg_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
        
        sig_package = QDSSignaturePackage(
            message=message,
            message_hash=msg_hash,
            session_nonce=session_nonce,
            timestamp=time.time(),
            classical_corrections_bob=corrections_bob,
            classical_corrections_charlie=corrections_charlie,
            decoy_indices=decoy_indices,
            signature_length=self.total_qubits
        )
        
        telemetry = {
            "session_nonce": session_nonce,
            "message": message,
            "message_hash": msg_hash,
            "total_qubits": self.total_qubits,
            "decoy_count": len(decoy_indices),
            "signature_qubit_count": self.N,
        }
        
        return sig_package, telemetry

    def verify_signature(
        self,
        sig_package: QDSSignaturePackage,
        verifier: str = "Bob",
        tampered_qubits: Optional[List[np.ndarray]] = None
    ) -> QDSVerificationResult:
        """
        Verifier (Bob or Charlie) verifies the received signature package.
        Applies projective measurements in bases specified by Alice's private key state.
        """
        session_nonce = sig_package.session_nonce
        if session_nonce not in self.alice_private_states:
            return QDSVerificationResult(
                is_valid=False,
                verifier_name=verifier,
                qber_signature=1.0,
                qber_decoy=1.0,
                total_signature_qubits=self.N,
                total_decoy_qubits=self.num_decoy,
                errors_detected=self.total_qubits,
                decision="REJECTED: Unknown or expired session nonce",
                details={"reason": "Session nonce not found in state store"}
            )
            
        alice_states = self.alice_private_states[session_nonce]
        session_data = self.active_sessions[session_nonce]
        
        # Get verifier's teleported qubits
        if tampered_qubits is not None:
            qubits = tampered_qubits
        elif verifier.lower() == "bob":
            qubits = session_data.get("qubits_bob", [])
        else:
            qubits = session_data.get("qubits_charlie", [])
            
        if len(qubits) != self.total_qubits:
            return QDSVerificationResult(
                is_valid=False,
                verifier_name=verifier,
                qber_signature=1.0,
                qber_decoy=1.0,
                total_signature_qubits=self.N,
                total_decoy_qubits=self.num_decoy,
                errors_detected=self.total_qubits,
                decision="REJECTED: Mismatched quantum register size"
            )
            
        decoy_set = set(sig_package.decoy_indices)
        sig_errors = 0
        decoy_errors = 0
        
        measurement_logs = []
        
        for idx in range(self.total_qubits):
            target_qubit = qubits[idx]
            expected_info = alice_states[idx]
            basis = expected_info["basis"]
            expected_bit = expected_info["bit_val"]
            
            # Projective measurement in expected basis
            measured_bit, _, _ = perform_projective_measurement(target_qubit, basis, rng=self.rng)
            
            is_error = (measured_bit != expected_bit)
            if expected_info["is_decoy"]:
                if is_error:
                    decoy_errors += 1
            else:
                if is_error:
                    sig_errors += 1
                    
            measurement_logs.append({
                "index": idx,
                "is_decoy": expected_info["is_decoy"],
                "basis": basis.value,
                "expected_bit": expected_bit,
                "measured_bit": measured_bit,
                "error": is_error
            })
            
        qber_sig = float(sig_errors / self.N) if self.N > 0 else 0.0
        qber_decoy = float(decoy_errors / self.num_decoy) if self.num_decoy > 0 else 0.0
        
        # Non-AI Verification Decision:
        # 1. Decoy QBER must not exceed verification threshold ev
        # 2. Signature QBER must not exceed verification threshold ev
        is_valid = (qber_sig <= self.ev) and (qber_decoy <= self.ev)
        
        decision_str = "ACCEPTED" if is_valid else "REJECTED (Threshold Exceeded)"
        
        return QDSVerificationResult(
            is_valid=is_valid,
            verifier_name=verifier,
            qber_signature=qber_sig,
            qber_decoy=qber_decoy,
            total_signature_qubits=self.N,
            total_decoy_qubits=self.num_decoy,
            errors_detected=sig_errors + decoy_errors,
            decision=decision_str,
            details={
                "measurement_logs": measurement_logs[:20],  # truncated sample
                "ev_threshold": self.ev,
                "ed_threshold": self.ed,
                "signature_errors": sig_errors,
                "decoy_errors": decoy_errors
            }
        )

    def dispute_arbitration(
        self,
        res_bob: QDSVerificationResult,
        res_charlie: QDSVerificationResult
    ) -> Dict[str, Any]:
        """
        Arbitration protocol for non-repudiation between Bob and Charlie.
        Guarantees that Alice cannot sign a message that Bob accepts while Charlie rejects.
        """
        # Cross-verifier error discrepancy
        delta_qber = abs(res_bob.qber_signature - res_charlie.qber_signature)
        
        if res_bob.is_valid and res_charlie.is_valid:
            status = "MUTUAL_ACCEPTANCE"
            description = "Signature verified and accepted by both independent verifiers."
            arbitration_passed = True
        elif not res_bob.is_valid and not res_charlie.is_valid:
            status = "MUTUAL_REJECTION"
            description = "Signature rejected by both verifiers due to high quantum disturbance / forgery."
            arbitration_passed = True
        else:
            # One accepted, one rejected -> Discrepancy / Repudiation test
            if delta_qber > (self.ed - self.ev):
                status = "SIGNER_REPUDIATION_ATTACK_DETECTED"
                description = "Discrepancy exceeds dispute threshold (ed). Signer Alice attempted selective repudiation or targeted channel manipulation."
                arbitration_passed = False
            else:
                status = "CHANNEL_ASYMMETRY_ERROR"
                description = "Marginal error difference near threshold."
                arbitration_passed = False
                
        return {
            "status": status,
            "description": description,
            "arbitration_passed": arbitration_passed,
            "bob_qber": res_bob.qber_signature,
            "charlie_qber": res_charlie.qber_signature,
            "delta_qber": delta_qber,
            "threshold_ev": self.ev,
            "threshold_ed": self.ed
        }

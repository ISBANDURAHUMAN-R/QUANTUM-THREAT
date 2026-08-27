"""
Quantum Cyber Attack Simulator.

Simulates 7+ quantum attack vectors against the teleportation-based QDS protocol:
1. Intercept-Resend Eavesdropping (measure-and-forward in random Pauli bases)
2. CNOT Entanglement Probe Attack (ancilla coupling to Bell channel)
3. Quantum Man-in-the-Middle (MITM - entanglement substitution)
4. Existential & Chosen-Message Signature Forgery (attacker fabricates signature without private key)
5. Dishonest Receiver Forgery (Malicious Bob frames Alice by forging to Charlie)
6. Signature Replay Attack (replay captured session nonces & classical records)
7. Unauthorized Verification Attempt (unauthenticated measurement without BSM keys)
8. Coherent Quantum Channel Jamming (targeted Pauli phase/bit flip noise)
"""

import numpy as np
import time
from typing import Dict, Any, List, Tuple, Optional
from core.quantum_states import (
    PauliBasis, PauliEigenstate, get_eigenstate_vector,
    perform_projective_measurement, state_to_density_matrix,
    PAULI_X, PAULI_Y, PAULI_Z, PAULI_I
)
from core.bell_pairs import create_bell_pair, BellStateEnum
from core.qds_protocol import TeleportationQDSProtocol, QDSSignaturePackage, QDSVerificationResult
from threat_detection.threat_detector import QuantumThreatDetector
from simulation.noise_channels import apply_depolarizing_noise, apply_bit_flip_noise, apply_phase_flip_noise

class QuantumAttackSimulator:
    def __init__(
        self,
        protocol: Optional[TeleportationQDSProtocol] = None,
        detector: Optional[QuantumThreatDetector] = None,
        rng_seed: Optional[int] = None
    ):
        self.protocol = protocol if protocol is not None else TeleportationQDSProtocol(security_parameter_N=128)
        self.detector = detector if detector is not None else QuantumThreatDetector()
        self.rng = np.random.default_rng(rng_seed)

    def execute_honest_protocol(
        self,
        message: str = "CONFIDENTIAL_TRANSACTION_PAYLOAD_001"
    ) -> Dict[str, Any]:
        """
        Executes standard legitimate protocol without any attacker interference.
        Expected: Signature accepted with near-zero QBER (or minimal baseline noise).
        """
        sig_pkg, telemetry = self.protocol.sign_message(message)
        session_data = self.protocol.active_sessions[sig_pkg.session_nonce]
        
        # Bob and Charlie verify
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        res_charlie = self.protocol.verify_signature(sig_pkg, verifier="Charlie")
        
        # Threat detector inspection
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            res_charlie,
            bell_pairs_bob=session_data["bell_pairs_bob"],
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "NONE (Honest Baseline)",
            "message": message,
            "signature_package": sig_pkg,
            "res_bob": res_bob,
            "res_charlie": res_charlie,
            "threat_report": report
        }

    def simulate_intercept_resend_attack(
        self,
        message: str = "CONFIDENTIAL_TRANSACTION_PAYLOAD_001",
        intercept_probability: float = 1.0
    ) -> Dict[str, Any]:
        """
        Eve intercepts qubits in transit, measures them in a random Pauli basis (X, Y, or Z),
        and re-prepares the measured eigenstate to forward to Bob.
        Physics: Conjugate basis mismatch collapses state, inducing theoretical ~25% QBER.
        """
        sig_pkg, _ = self.protocol.sign_message(message)
        session_data = self.protocol.active_sessions[sig_pkg.session_nonce]
        original_qubits = session_data["qubits_bob"]
        
        tampered_qubits = []
        bases = [PauliBasis.Z, PauliBasis.X, PauliBasis.Y]
        
        for q in original_qubits:
            if self.rng.random() < intercept_probability:
                # Eve measures in a randomly guessed basis
                eve_basis = bases[self.rng.integers(0, 3)]
                outcome_bit, collapsed_state, _ = perform_projective_measurement(q, eve_basis, rng=self.rng)
                # Eve forwards collapsed state
                tampered_qubits.append(collapsed_state)
            else:
                tampered_qubits.append(q)
                
        # Bob verifies tampered qubits
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob", tampered_qubits=tampered_qubits)
        res_charlie = self.protocol.verify_signature(sig_pkg, verifier="Charlie")
        
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            res_charlie,
            bell_pairs_bob=session_data["bell_pairs_bob"],
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "INTERCEPT_RESEND_EAVESDROPPING",
            "intercept_probability": intercept_probability,
            "res_bob": res_bob,
            "res_charlie": res_charlie,
            "threat_report": report
        }

    def simulate_cnot_entanglement_probe(
        self,
        message: str = "CONFIDENTIAL_TRANSACTION_PAYLOAD_001",
        probe_coupling_theta: float = np.pi / 4.0
    ) -> Dict[str, Any]:
        """
        Eve attaches an ancilla probe qubit |0>_E and applies an entangling unitary
        U_probe(theta) to Alice's half of the Bell pair during distribution.
        Physics: Entanglement degradation reduces Bell-CHSH witness value S below 2.828.
        """
        session_data = self.protocol.setup_entanglement_distribution()
        session_nonce = session_data["session_nonce"]
        
        # Degrade Bell pairs via probe interaction
        probed_bell_pairs = []
        for pair in session_data["bell_pairs_bob"]:
            # Apply entangling rotation / phase damping
            rho_pair = state_to_density_matrix(pair)
            
            # Partial depolarizing/damping model for ancilla probe
            probe_noise = float(np.sin(probe_coupling_theta) ** 2 * 0.4)
            rho_probed = (1.0 - probe_noise) * rho_pair + probe_noise * (
                np.kron(PAULI_Z, PAULI_I) @ rho_pair @ np.kron(PAULI_Z, PAULI_I)
            )
            probed_bell_pairs.append(rho_probed)
            
        session_data["bell_pairs_bob"] = probed_bell_pairs
        
        # Sign message
        sig_pkg, _ = self.protocol.sign_message(message, session_nonce=session_nonce)
        
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        res_charlie = self.protocol.verify_signature(sig_pkg, verifier="Charlie")
        
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            res_charlie,
            bell_pairs_bob=probed_bell_pairs,
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "CNOT_ENTANGLEMENT_PROBE",
            "probe_theta": probe_coupling_theta,
            "res_bob": res_bob,
            "res_charlie": res_charlie,
            "threat_report": report
        }

    def simulate_quantum_mitm(
        self,
        message: str = "CONFIDENTIAL_TRANSACTION_PAYLOAD_001"
    ) -> Dict[str, Any]:
        """
        Eve intercepts the Bell channel completely, creating separate classical/separable states.
        Physics: Bell-CHSH witness S collapses to classical limit (<= 2.0).
        """
        session_data = self.protocol.setup_entanglement_distribution()
        session_nonce = session_data["session_nonce"]
        
        # Replace entangled states with separable mixed states (rho = 0.5|00><00| + 0.5|11><11|)
        separable_pairs = []
        rho_sep = 0.5 * np.outer(np.kron([1, 0], [1, 0]), np.kron([1, 0], [1, 0])) + \
                  0.5 * np.outer(np.kron([0, 1], [0, 1]), np.kron([0, 1], [0, 1]))
                  
        for _ in range(self.protocol.total_qubits):
            separable_pairs.append(rho_sep.astype(complex))
            
        session_data["bell_pairs_bob"] = separable_pairs
        sig_pkg, _ = self.protocol.sign_message(message, session_nonce=session_nonce)
        
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        res_charlie = self.protocol.verify_signature(sig_pkg, verifier="Charlie")
        
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            res_charlie,
            bell_pairs_bob=separable_pairs,
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "QUANTUM_MAN_IN_THE_MIDDLE",
            "res_bob": res_bob,
            "res_charlie": res_charlie,
            "threat_report": report
        }

    def simulate_existential_forgery(
        self,
        forged_message: str = "TRANSFER_1000000_USD_TO_EVE_ACCOUNT"
    ) -> Dict[str, Any]:
        """
        Eve attempts to forge Alice's signature on a forged message by fabricating random classical
        BSM strings and preparing random quantum states without Alice's private key.
        Physics: Measurements in non-orthogonal Pauli bases yield ~50% random guessing error.
        """
        # Alice signs a genuine message
        sig_pkg, _ = self.protocol.sign_message("GENUINE_MSG_001")
        
        # Eve creates a forged signature package
        random_corrections = [(int(self.rng.integers(0, 2)), int(self.rng.integers(0, 2))) 
                              for _ in range(self.protocol.total_qubits)]
                              
        forged_pkg = QDSSignaturePackage(
            message=forged_message,
            message_hash="forged_hash_" + str(self.rng.integers(100000, 999999)),
            session_nonce=sig_pkg.session_nonce,
            timestamp=time.time(),
            classical_corrections_bob=random_corrections,
            classical_corrections_charlie=random_corrections,
            decoy_indices=sig_pkg.decoy_indices,
            signature_length=self.protocol.total_qubits
        )
        
        # Random quantum states prepared by Eve
        bases = [PauliBasis.Z, PauliBasis.X, PauliBasis.Y]
        forged_qubits = []
        for _ in range(self.protocol.total_qubits):
            b = bases[self.rng.integers(0, 3)]
            state_enum = PauliEigenstate.ZERO if self.rng.integers(0, 2) == 0 else PauliEigenstate.ONE
            forged_qubits.append(get_eigenstate_vector(state_enum))
            
        res_bob = self.protocol.verify_signature(forged_pkg, verifier="Bob", tampered_qubits=forged_qubits)
        
        report = self.detector.inspect_and_evaluate(
            forged_pkg,
            res_bob,
            bell_pairs_bob=self.protocol.active_sessions[sig_pkg.session_nonce]["bell_pairs_bob"],
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "EXISTENTIAL_SIGNATURE_FORGERY",
            "forged_message": forged_message,
            "res_bob": res_bob,
            "threat_report": report
        }

    def simulate_dishonest_receiver_forgery(
        self,
        message: str = "AGREEMENT_PAYLOAD_001"
    ) -> Dict[str, Any]:
        """
        Malicious Bob measures his received qubits to extract key information, then constructs
        a forged signature and presents it to Charlie to frame Alice.
        Physics: Quantum no-cloning and measurement disturbance causes state collapse,
        inducing a large discrepancy between Bob and Charlie that is caught in arbitration.
        """
        sig_pkg, _ = self.protocol.sign_message(message)
        session_data = self.protocol.active_sessions[sig_pkg.session_nonce]
        bob_qubits = session_data["qubits_bob"]
        
        # Bob measures his qubits to guess Alice's state
        guessed_qubits = []
        bases = [PauliBasis.Z, PauliBasis.X, PauliBasis.Y]
        for q in bob_qubits:
            b = bases[self.rng.integers(0, 3)]
            _, collapsed_state, _ = perform_projective_measurement(q, b, rng=self.rng)
            guessed_qubits.append(collapsed_state)
            
        # Bob forwards guessed states to Charlie claiming they are from Alice
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        res_charlie = self.protocol.verify_signature(sig_pkg, verifier="Charlie", tampered_qubits=guessed_qubits)
        
        arbitration = self.protocol.dispute_arbitration(res_bob, res_charlie)
        
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            res_charlie,
            bell_pairs_bob=session_data["bell_pairs_bob"],
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "DISHONEST_RECEIVER_FORGERY",
            "arbitration": arbitration,
            "res_bob": res_bob,
            "res_charlie": res_charlie,
            "threat_report": report
        }

    def simulate_replay_attack(
        self,
        message: str = "AUTHORIZE_WIRE_TRANSFER_REF_9921"
    ) -> Dict[str, Any]:
        """
        Eve replays a previously accepted signature packet.
        Physics/Crypto: Dynamic session nonces and consumed Bell pair indices detect replay with 100% certainty.
        """
        sig_pkg, _ = self.protocol.sign_message(message)
        session_data = self.protocol.active_sessions[sig_pkg.session_nonce]
        
        # Round 1: Legitimate verification
        res_bob_1 = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        report_1 = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob_1,
            bell_pairs_bob=session_data["bell_pairs_bob"]
        )
        
        # Round 2: Replay attempt using the identical signature package
        res_bob_2 = self.protocol.verify_signature(sig_pkg, verifier="Bob")
        report_2 = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob_2,
            bell_pairs_bob=session_data["bell_pairs_bob"]
        )
        
        return {
            "attack_type": "REPLAY_ATTACK",
            "round_1_legitimate": report_1,
            "round_2_replayed": report_2
        }

    def simulate_quantum_channel_jamming(
        self,
        message: str = "CRITICAL_GRID_CONTROL_SIGNAL",
        noise_level: float = 0.20
    ) -> Dict[str, Any]:
        """
        Attacker or environment injects severe Pauli noise / depolarizing jamming into channel.
        """
        sig_pkg, _ = self.protocol.sign_message(message)
        session_data = self.protocol.active_sessions[sig_pkg.session_nonce]
        original_qubits = session_data["qubits_bob"]
        
        jammed_qubits = [apply_depolarizing_noise(q, p=noise_level, rng=self.rng) for q in original_qubits]
        
        res_bob = self.protocol.verify_signature(sig_pkg, verifier="Bob", tampered_qubits=jammed_qubits)
        
        report = self.detector.inspect_and_evaluate(
            sig_pkg,
            res_bob,
            bell_pairs_bob=session_data["bell_pairs_bob"],
            raw_measurement_logs=res_bob.details.get("measurement_logs")
        )
        
        return {
            "attack_type": "QUANTUM_CHANNEL_JAMMING",
            "noise_level": noise_level,
            "res_bob": res_bob,
            "threat_report": report
        }

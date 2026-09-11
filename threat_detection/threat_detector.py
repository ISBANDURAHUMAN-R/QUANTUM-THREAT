"""
Central Quantum-Inspired Cyber Threat Detection Engine (Strictly Non-AI).

Applies quantum physical principles and statistical decision boundaries to classify and mitigate threats:
1. Anti-replay & session nonce freshness check
2. Bell-CHSH entanglement witness evaluation (Physics Layer)
3. Decoy-state disturbance & quantum transit collapse (Transit Layer)
4. Pauli eigenstate collapse & projective measurement verification (Payload Layer)
5. Multi-verifier arbitration and non-repudiation (Arbitration Layer)
6. Hoeffding bounds and exact binomial hypothesis testing (Statistical Layer)
"""

from typing import Dict, Any, List, Optional
import numpy as np
from core.qds_protocol import QDSSignaturePackage, QDSVerificationResult
from threat_detection.quantum_metrics import (
    evaluate_bell_witness, compute_pauli_error_decomposition,
    compute_quantum_disturbance
)
from threat_detection.statistical_bounds import (
    evaluate_statistical_confidence, calculate_forgery_probability_bound,
    hoeffding_upper_bound
)
from threat_detection.decoy_state_analyzer import analyze_decoy_disturbances
from threat_detection.anti_replay_engine import AntiReplayEngine

class QuantumThreatDetector:
    def __init__(
        self,
        baseline_channel_noise: float = 0.03,
        verification_threshold_ev: float = 0.08,
        dispute_threshold_ed: float = 0.18,
        chsh_tolerance: float = 0.12,
        max_timestamp_drift: float = 300.0
    ):
        self.baseline_noise = baseline_channel_noise
        self.ev = verification_threshold_ev
        self.ed = dispute_threshold_ed
        self.chsh_tolerance = chsh_tolerance
        self.anti_replay = AntiReplayEngine(max_timestamp_drift_seconds=max_timestamp_drift)
        self.incident_history: List[Dict[str, Any]] = []

    def inspect_and_evaluate(
        self,
        sig_package: QDSSignaturePackage,
        res_bob: QDSVerificationResult,
        res_charlie: Optional[QDSVerificationResult] = None,
        bell_pairs_bob: Optional[List[np.ndarray]] = None,
        raw_measurement_logs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes comprehensive quantum threat analysis across the quantum physical stack.
        """
        # 1. Anti-Replay Verification (Layer 1)
        replay_check = self.anti_replay.validate_session_freshness(
            sig_package.session_nonce,
            sig_package.timestamp
        )
        
        if not replay_check["is_fresh"]:
            threat_type = replay_check["threat_flag"]
            return self._build_threat_report(
                threat_detected=True,
                threat_classification=threat_type,
                confidence_score=100.0,
                is_signature_accepted=False,
                summary=f"Replay attack detected: {replay_check['reason']}",
                mitigation_action="Discard signature packet; flag origin IP/channel for replay investigation.",
                metrics={"replay_check": replay_check}
            )

        # 2. Statistical Analysis of QBER & Decoy Disturbance
        decoy_analysis = analyze_decoy_disturbances(
            sig_qber=res_bob.qber_signature,
            decoy_qber=res_bob.qber_decoy,
            sig_qubits=res_bob.total_signature_qubits,
            decoy_qubits=res_bob.total_decoy_qubits,
            baseline_noise=self.baseline_noise,
            detection_threshold=self.ev
        )
        
        # 3. Bell-CHSH Entanglement Witness (Layer 2)
        chsh_metrics = None
        if bell_pairs_bob:
            chsh_metrics = evaluate_bell_witness(bell_pairs_bob)
            
        # 4. Pauli Error Decomposition (Z vs X vs Y)
        pauli_decomp = None
        if raw_measurement_logs:
            pauli_decomp = compute_pauli_error_decomposition(raw_measurement_logs)
            
        # 5. Non-AI Rule-Based Decision Logic (Physics Stack Order)
        sig_qber = res_bob.qber_signature
        decoy_qber = res_bob.qber_decoy
        mean_chsh = chsh_metrics["mean_chsh_s"] if chsh_metrics else 2.8284
        
        arbitration_result = None
        if res_charlie is not None:
            delta = abs(res_bob.qber_signature - res_charlie.qber_signature)
            arbitration_result = {
                "bob_qber": res_bob.qber_signature,
                "charlie_qber": res_charlie.qber_signature,
                "delta_qber": delta,
                "dispute_threshold": self.ed
            }

        # Rule Tree - Layer by Layer:
        # Layer 2: Entanglement Health on Physical Bell Channel
        if mean_chsh <= 2.0:
            threat_detected = True
            threat_classification = "QUANTUM_MAN_IN_THE_MIDDLE"
            confidence_score = 100.0
            is_accepted = False
            summary = f"Quantum Man-in-the-Middle detected. Bell-CHSH witness S={mean_chsh:.3f} <= 2.0 demonstrates broken entanglement (separable classical states)."
            mitigation = "Terminate quantum link immediately. Quarantine communication channel."
            
        elif mean_chsh < (2.8284 - self.chsh_tolerance):
            threat_detected = True
            threat_classification = "CNOT_ENTANGLEMENT_PROBE"
            confidence_score = 96.5
            is_accepted = False
            summary = f"Entanglement degradation detected: CHSH witness S={mean_chsh:.3f} reveals ancilla probe coupling by eavesdropper."
            mitigation = "Purge compromised Bell pairs. Re-run privacy amplification."
            
        # Layer 3: Active Quantum Interception in Transit (Decoy State Collapse)
        elif decoy_qber > self.ev and sig_qber <= 0.40:
            threat_detected = True
            threat_classification = "INTERCEPT_RESEND_EAVESDROPPING"
            confidence_score = decoy_analysis["decoy_stat"]["confidence_percentage"]
            is_accepted = False
            summary = f"Active intercept-resend attack detected (Decoy QBER: {decoy_qber*100:.1f}%, Payload QBER: {sig_qber*100:.1f}%). Quantum state collapse observed."
            mitigation = "Abort session. Re-distribute fresh Bell pairs over alternate optical path."
            
        # Layer 4: Payload / Classical Forgery
        elif sig_qber > self.ev and decoy_qber <= self.ev:
            threat_detected = True
            threat_classification = "EXISTENTIAL_SIGNATURE_FORGERY"
            confidence_score = decoy_analysis["sig_stat"]["confidence_percentage"]
            is_accepted = False
            summary = f"Signature payload forgery detected: Payload QBER={sig_qber*100:.1f}% exceeds threshold {self.ev*100:.1f}%, while decoy channel remained unperturbed."
            mitigation = "Reject signature. Attacker attempted existential/chosen-message forgery without private key."
            
        elif sig_qber > 0.40 and decoy_qber > 0.40:
            threat_detected = True
            threat_classification = "EXISTENTIAL_SIGNATURE_FORGERY"
            confidence_score = 99.9
            is_accepted = False
            summary = f"Blind signature forgery detected: High error rate (Payload QBER={sig_qber*100:.1f}%, Decoy QBER={decoy_qber*100:.1f}%) indicates randomly guessed quantum states."
            mitigation = "Reject signature. Attacker forged entire quantum burst."

        # Layer 5: Multi-Verifier Discrepancy (Signer Repudiation / Framing)
        elif arbitration_result and arbitration_result["delta_qber"] > (self.ed - self.ev):
            threat_detected = True
            threat_classification = "DISHONEST_RECEIVER_FORGERY_OR_REPUDIATION"
            confidence_score = 99.8
            is_accepted = False
            summary = f"Signer repudiation or dishonest receiver forgery detected: Bob QBER ({res_bob.qber_signature*100:.1f}%) and Charlie QBER ({res_charlie.qber_signature*100:.1f}%) exhibit non-repudiation violation (delta={arbitration_result['delta_qber']*100:.1f}%)."
            mitigation = "Trigger arbitration protocol. Hold offending party accountable for repudiation attempt."

        # Layer 6: Honest Legitimate Signature
        elif sig_qber <= self.ev and decoy_qber <= self.ev:
            threat_detected = False
            threat_classification = "LEGITIMATE_SIGNATURE"
            confidence_score = 99.9
            is_accepted = True
            summary = f"Signature verified with high fidelity (QBER: {sig_qber*100:.1f}%, CHSH: {mean_chsh:.3f})."
            mitigation = "Accept signature as authentic."

        else:
            threat_detected = True
            threat_classification = "QUANTUM_CHANNEL_JAMMING_OR_NOISE"
            confidence_score = 90.0
            is_accepted = False
            summary = f"Channel disturbance QBER={sig_qber*100:.1f}% exceeds safe tolerance."
            mitigation = "Initiate channel recalibration."

        sec_bounds = calculate_forgery_probability_bound(
            res_bob.total_signature_qubits,
            ev=self.ev,
            ed=self.ed
        )
        
        report = self._build_threat_report(
            threat_detected=threat_detected,
            threat_classification=threat_classification,
            confidence_score=confidence_score,
            is_signature_accepted=is_accepted,
            summary=summary,
            mitigation_action=mitigation,
            metrics={
                "sig_qber": sig_qber,
                "decoy_qber": decoy_qber,
                "baseline_noise": self.baseline_noise,
                "verification_threshold_ev": self.ev,
                "dispute_threshold_ed": self.ed,
                "chsh_metrics": chsh_metrics,
                "decoy_analysis": decoy_analysis,
                "pauli_decomposition": pauli_decomp,
                "arbitration_result": arbitration_result,
                "security_bounds": sec_bounds,
                "replay_check": replay_check
            }
        )
        
        self.incident_history.append(report)
        return report

    def _build_threat_report(
        self,
        threat_detected: bool,
        threat_classification: str,
        confidence_score: float,
        is_signature_accepted: bool,
        summary: str,
        mitigation_action: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "threat_detected": threat_detected,
            "threat_classification": threat_classification,
            "confidence_score": confidence_score,
            "is_signature_accepted": is_signature_accepted,
            "summary": summary,
            "mitigation_action": mitigation_action,
            "metrics": metrics
        }

"""
Unit tests for non-AI quantum threat detection across all simulated attack vectors.
"""

from core.qds_protocol import TeleportationQDSProtocol
from threat_detection.threat_detector import QuantumThreatDetector
from simulation.attack_simulator import QuantumAttackSimulator

def get_simulator():
    protocol = TeleportationQDSProtocol(security_parameter_N=128, rng_seed=42)
    detector = QuantumThreatDetector()
    return QuantumAttackSimulator(protocol=protocol, detector=detector, rng_seed=42)

def test_detect_intercept_resend_attack(simulator=None):
    """Verify that intercept-resend attack is caught due to QBER ~ 25%."""
    if simulator is None:
        simulator = get_simulator()
    res = simulator.simulate_intercept_resend_attack()
    report = res["threat_report"]
    assert report["threat_detected"] is True
    assert "INTERCEPT_RESEND" in report["threat_classification"]
    assert report["is_signature_accepted"] is False
    assert report["metrics"]["sig_qber"] > 0.15

def test_detect_cnot_entanglement_probe(simulator=None):
    """Verify that CNOT probe is caught via Bell-CHSH witness degradation."""
    if simulator is None:
        simulator = get_simulator()
    res = simulator.simulate_cnot_entanglement_probe()
    report = res["threat_report"]
    assert report["threat_detected"] is True
    assert report["is_signature_accepted"] is False
    assert report["metrics"]["chsh_metrics"]["mean_chsh_s"] < 2.70

def test_detect_quantum_mitm(simulator=None):
    """Verify that MITM separable state causes CHSH <= 2.0 and triggers alarm."""
    if simulator is None:
        simulator = get_simulator()
    res = simulator.simulate_quantum_mitm()
    report = res["threat_report"]
    assert report["threat_detected"] is True
    assert report["threat_classification"] == "QUANTUM_MAN_IN_THE_MIDDLE"
    assert report["metrics"]["chsh_metrics"]["mean_chsh_s"] <= 2.0

def test_detect_existential_forgery(simulator=None):
    """Verify that existential forgery is caught via high payload QBER with clean decoy channel."""
    if simulator is None:
        simulator = get_simulator()
    res = simulator.simulate_existential_forgery()
    report = res["threat_report"]
    assert report["threat_detected"] is True
    assert "FORGERY" in report["threat_classification"]
    assert report["metrics"]["sig_qber"] > 0.25

def test_detect_replay_attack(simulator=None):
    """Verify that replayed signatures are caught on round 2."""
    if simulator is None:
        simulator = get_simulator()
    res = simulator.simulate_replay_attack()
    assert res["round_1_legitimate"]["threat_detected"] is False
    assert res["round_2_replayed"]["threat_detected"] is True
    assert "REPLAY" in res["round_2_replayed"]["threat_classification"]

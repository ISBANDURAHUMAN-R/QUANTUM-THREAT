"""
Test Runner Script for Quantum-Inspired Threat Detection Framework.
"""

import sys
import os
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_quantum_core import *
from tests.test_qds_protocol import *
from tests.test_threat_detection import *
from tests.test_statistical_bounds import *

class TestQuantumSuite(unittest.TestCase):
    def test_pauli_properties(self):
        test_pauli_eigenstate_properties()
        
    def test_fidelity_trace(self):
        test_quantum_fidelity_and_trace_distance()
        
    def test_bell_chsh(self):
        test_bell_state_and_chsh_violation()
        
    def test_teleportation(self):
        test_quantum_teleportation_perfect_fidelity()
        
    def test_honest_qds(self):
        test_qds_honest_verification_deterministic()
        
    def test_nonce_check(self):
        test_qds_wrong_session_nonce_rejected()
        
    def test_intercept_resend(self):
        from core.qds_protocol import TeleportationQDSProtocol
        from threat_detection.threat_detector import QuantumThreatDetector
        from simulation.attack_simulator import QuantumAttackSimulator
        sim = QuantumAttackSimulator(TeleportationQDSProtocol(128, rng_seed=42), QuantumThreatDetector(), rng_seed=42)
        test_detect_intercept_resend_attack(sim)
        
    def test_cnot_probe(self):
        from core.qds_protocol import TeleportationQDSProtocol
        from threat_detection.threat_detector import QuantumThreatDetector
        from simulation.attack_simulator import QuantumAttackSimulator
        sim = QuantumAttackSimulator(TeleportationQDSProtocol(128, rng_seed=42), QuantumThreatDetector(), rng_seed=42)
        test_detect_cnot_entanglement_probe(sim)
        
    def test_mitm(self):
        from core.qds_protocol import TeleportationQDSProtocol
        from threat_detection.threat_detector import QuantumThreatDetector
        from simulation.attack_simulator import QuantumAttackSimulator
        sim = QuantumAttackSimulator(TeleportationQDSProtocol(128, rng_seed=42), QuantumThreatDetector(), rng_seed=42)
        test_detect_quantum_mitm(sim)
        
    def test_forgery(self):
        from core.qds_protocol import TeleportationQDSProtocol
        from threat_detection.threat_detector import QuantumThreatDetector
        from simulation.attack_simulator import QuantumAttackSimulator
        sim = QuantumAttackSimulator(TeleportationQDSProtocol(128, rng_seed=42), QuantumThreatDetector(), rng_seed=42)
        test_detect_existential_forgery(sim)
        
    def test_replay(self):
        from core.qds_protocol import TeleportationQDSProtocol
        from threat_detection.threat_detector import QuantumThreatDetector
        from simulation.attack_simulator import QuantumAttackSimulator
        sim = QuantumAttackSimulator(TeleportationQDSProtocol(128, rng_seed=42), QuantumThreatDetector(), rng_seed=42)
        test_detect_replay_attack(sim)
        
    def test_kl_div(self):
        test_kl_divergence_non_negative()
        
    def test_hoeffding(self):
        test_hoeffding_upper_bound()
        
    def test_binomial_pval(self):
        test_binomial_tail_pvalue()
        
    def test_forgery_scaling(self):
        test_forgery_probability_scaling()

if __name__ == "__main__":
    print("\n========================================================")
    print("  RUNNING QUANTUM QDS THREAT DETECTION TEST SUITE")
    print("========================================================\n")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuantumSuite)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n[+] ALL TESTS PASSED SUCCESSFULLY! (100% PASS RATE)\n")
        sys.exit(0)
    else:
        print("\n[-] SOME TESTS FAILED.\n")
        sys.exit(1)
